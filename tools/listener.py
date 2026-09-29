"""listener.py - the worker daemon for one machine.

Pulls the repo every ~30 s, runs queued tasks for this machine's workers (one at a time per worker),
writes STARTED.json / REPORT.md / heartbeat.json, enforces the size rules and the Astra ban, and pushes results.

Usage:
  python tools/listener.py              run until Ctrl+C
  python tools/listener.py --once       do one pass (sync, at most one task per worker) then exit
  python tools/listener.py --offline    never pull or push (commits stay local). For testing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (REPO_ROOT, SAFE_TOKEN, git, load_machine_config, now_iso, read_json, run, which, write_json)  # noqa: E402

SYNC_EVERY_S = 30
HEARTBEAT_EVERY_S = 300
MAX_FILE_MB = 20
MAX_PREVIEW_MB = 10
PUSH_TRIES = 5
DEFAULT_TIMEOUT_MIN = 60
RATE_RE = re.compile(r"rate.?limit|usage limit|quota|too many requests|\b429\b|limit reached|exceeded your", re.I)
STATUS_RE = re.compile(r"^\s*status\s*:\s*[\"']?(done|failed|refused)\b", re.I | re.M)

CFG = load_machine_config()
MACHINE = CFG["machine"]
REGISTRY = read_json(REPO_ROOT / "machines" / "registry.json", {})
MY_WORKERS: list[str] = CFG["workers"]
FOOTAGE_ROOT = CFG["footage_root"]
RENDERS_DIR = Path(CFG["renders_dir"])
GUARD_REPOS: list[str] = CFG.get("guard_repos", [])  # other repos that no task may change
LOG_DIR = REPO_ROOT / "local" / "logs"
OFFLINE = False

rate_until: dict[str, dt.datetime] = {}
last_usage: dict = {}
last_codex_rate_limits: dict | None = None
current_task: str | None = None
last_heartbeat = 0.0
warned_blocked: set[str] = set()


# ---------------------------------------------------------------- logging
def log(msg: str) -> None:
    line = f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / f"listener-{dt.date.today().isoformat()}.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------- small parsers
def parse_frontmatter(text: str) -> tuple[dict, str]:
    text = text.lstrip("﻿")
    m = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    fm: dict = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            fm[k.strip()] = [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
        elif v.lower() in ("", "null", "~", "none"):
            fm[k.strip()] = None
        elif v.lower() in ("true", "false"):
            fm[k.strip()] = v.lower() == "true"
        elif re.fullmatch(r"-?\d+", v):
            fm[k.strip()] = int(v)
        else:
            fm[k.strip()] = v.strip("\"'")
    return fm, m.group(2)


def id_sort_key(task_id: str):
    m = re.match(r"^([A-Za-z]*)(\d+)", task_id)
    return (m.group(1), int(m.group(2)), task_id) if m else ("~", 0, task_id)


def report_status(rid: str) -> str | None:
    p = REPO_ROOT / "results" / rid / "REPORT.md"
    if not p.exists():
        return None
    fm, body = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
    if fm.get("status"):
        return str(fm["status"]).lower()
    m = STATUS_RE.search(body[:2000])
    return m.group(1).lower() if m else None


def review_verdict(rid: str) -> str | None:
    p = REPO_ROOT / "reviews" / f"{rid}.md"
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(text)
    if fm.get("verdict"):
        return str(fm["verdict"]).lower()
    m = re.search(r"verdict\s*:\s*(accepted|redo|dropped)", text, re.I)
    return m.group(1).lower() if m else None


# ---------------------------------------------------------------- git
def branch() -> str:
    return git("branch", "--show-current")[1].strip() or "main"


def sync() -> bool:
    if OFFLINE:
        return True
    rc, out = git("pull", "--rebase", "--autostash", "origin", branch())
    if rc != 0:
        if "couldn't find remote ref" in out:
            return True  # remote branch not created yet
        log(f"git pull failed: {out.strip()[:300]}")
        git("rebase", "--abort")
        return False
    return True


def push_with_retries() -> bool:
    if OFFLINE:
        return True
    for attempt in range(1, PUSH_TRIES + 1):
        rc, out = git("push", "origin", "HEAD")
        if rc == 0:
            return True
        log(f"push attempt {attempt}/{PUSH_TRIES} failed: {out.strip()[:200]}")
        rc2, out2 = git("pull", "--rebase", "--autostash", "origin", branch())
        if rc2 != 0 and "couldn't find remote ref" not in out2:
            git("rebase", "--abort")
        time.sleep(random.uniform(1, 4))
    log("push gave up after retries; the commit stays local and will go out with the next push")
    return False


def commit_paths(paths: list[str], message: str) -> bool:
    """Stage and commit exactly these repo-relative paths. Returns True if a commit was made."""
    existing = [p for p in paths if (REPO_ROOT / p).exists()]
    if not existing:
        return False
    git("add", "--", *existing)
    rc, out = git("commit", "-q", "-m", message, "--", *existing)
    if rc != 0 and "nothing to commit" not in out and "no changes added" not in out:
        log(f"commit failed: {out.strip()[:300]}")
    return rc == 0


# ---------------------------------------------------------------- heartbeat
def paused_workers() -> dict[str, str]:
    now = dt.datetime.now(dt.timezone.utc)
    return {w: t.isoformat() for w, t in rate_until.items() if t > now}


def write_heartbeat(status: str | None = None, push: bool = True) -> None:
    global last_heartbeat
    paused = paused_workers()
    if status is None:
        status = "busy" if current_task else ("rate_limited" if paused and len(paused) == len(MY_WORKERS) else "idle")
    hb = {
        "machine": MACHINE,
        "time": now_iso(),
        "status": status,
        "current_task": current_task,
        "workers": MY_WORKERS,
        "rate_limited_until": paused or None,
        "paused_by_safety_check": guard_paused() or None,
        "listener_pid": os.getpid(),
        "last_task_usage": last_usage or None,
        "codex_rate_limits": last_codex_rate_limits,
    }
    rel = f"machines/{MACHINE}/heartbeat.json"
    write_json(REPO_ROOT / rel, hb)
    last_heartbeat = time.time()
    if commit_paths([rel], f"heartbeat {MACHINE} {status}") and push:
        push_with_retries()


def heartbeat_due() -> bool:
    return time.time() - last_heartbeat >= HEARTBEAT_EVERY_S


# ---------------------------------------------------------------- task helpers
def deps_ready(task_id: str, deps: list[str]) -> bool:
    for d in deps or []:
        if report_status(d) == "done" and review_verdict(d) == "accepted":
            continue
        if report_status(d) in ("failed", "refused") or review_verdict(d) in ("redo", "dropped"):
            if task_id not in warned_blocked:
                warned_blocked.add(task_id)
                log(f"{task_id} is blocked: dependency {d} did not finish accepted. Waiting for the lead.")
        return False
    return True


def next_task(worker: str) -> Path | None:
    qdir = REPO_ROOT / "queue" / worker
    if not qdir.is_dir():
        return None
    files = sorted((f for f in qdir.glob("*.md")), key=lambda f: id_sort_key(f.stem))
    for f in files:
        rid = f.stem
        rdir = REPO_ROOT / "results" / rid
        if (rdir / "STARTED.json").exists() or (rdir / "REPORT.md").exists():
            continue
        fm, _ = parse_frontmatter(f.read_text(encoding="utf-8", errors="replace"))
        if not deps_ready(rid, fm.get("depends_on") or []):
            continue
        return f
    return None


def write_report(rid: str, status: str, worker: str, body: str, extra: dict | None = None) -> None:
    rdir = REPO_ROOT / "results" / rid
    rdir.mkdir(parents=True, exist_ok=True)
    lines = ["---", f"id: {rid}", f"status: {status}", f"worker: {worker}", f"machine: {MACHINE}",
             "written_by: listener", f"time: {now_iso()}"]
    for k, v in (extra or {}).items():
        lines.append(f"{k}: {v}")
    lines += ["---", "", f"# Report {rid} (written by the listener)", "", body.rstrip(), ""]
    (rdir / "REPORT.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def tail_lines(path: Path, n: int = 50) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-n:]
    except OSError:
        return "(no output captured)"
    return "\n".join(l[:400] for l in lines)


def enforce_sizes(rid: str, roots: list[Path]) -> list[str]:
    """Move oversize files to local/renders/<id>/... and return notes for REPORT.md."""
    notes = []
    results_dir = REPO_ROOT / "results" / rid
    for root in roots:
        if not root.exists():
            continue
        for f in ([root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]):
            mb = f.stat().st_size / 1024 / 1024
            is_preview = f.suffix.lower() == ".mp4" and results_dir in f.parents
            if mb > MAX_FILE_MB or (is_preview and mb > MAX_PREVIEW_MB):
                inside = results_dir in f.parents
                dest = RENDERS_DIR / rid / (f.relative_to(results_dir) if inside else f.relative_to(REPO_ROOT))
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(f), str(dest))
                notes.append(f"- `{f.relative_to(REPO_ROOT).as_posix()}` ({mb:.1f} MB) was too big for git. Moved to local path: `{dest}`")
                log(f"moved oversize file {f.name} ({mb:.1f} MB) to {dest}")
    return notes


def kill_tree(proc: subprocess.Popen) -> None:
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, timeout=30)
        else:
            proc.kill()
    except Exception as e:  # noqa: BLE001
        log(f"kill failed: {e}")


def parse_wait(text: str) -> dt.timedelta:
    m = re.search(r"(?:try again|retry|resets?|available again)[^.\n]{0,60}?\bin\s+([^.\n]{1,60})", text, re.I)
    if m:
        total = 0.0
        for num, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(d|days?|h|hrs?|hours?|m|mins?|minutes?|s|secs?|seconds?)\b", m.group(1), re.I):
            u = unit.lower()[0]
            total += float(num) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[u]
        if total > 0:
            return dt.timedelta(seconds=min(total, 7 * 86400))
    return dt.timedelta(minutes=30)


def scan_codex_events(log_path: Path) -> None:
    global last_codex_rate_limits, last_usage
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return

    def find_rate(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if "rate_limit" in k.lower():
                    return v
                r = find_rate(v)
                if r is not None:
                    return r
        elif isinstance(o, list):
            for v in o:
                r = find_rate(v)
                if r is not None:
                    return r
        return None

    for line in lines:
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        rl = find_rate(ev)
        if rl is not None:
            last_codex_rate_limits = {"seen_at": now_iso(), "value": rl}
        if ev.get("type") == "turn.completed" and "usage" in ev:
            last_usage = {"seen_at": now_iso(), **ev["usage"]}


# ---------------------------------------------------------------- building the command
def build_command(worker: str, fm: dict, rid: str, prompt_file_hint: str) -> tuple[list[str], str]:
    winfo = REGISTRY.get("workers", {}).get(worker, {})
    cli = winfo.get("cli", "codex")
    override = CFG.get("cli_overrides", {}).get(cli)
    exe = list(override) if isinstance(override, list) else ([override] if override else [which(cli)])
    if not exe[0]:
        raise RuntimeError(f"'{cli}' was not found on PATH. Run tools/doctor.py.")
    model = fm.get("model") or ("opus" if cli == "claude" else "gpt-6-sol")
    effort = fm.get("effort") or ("high" if cli == "claude" else "medium")
    last_msg = str(REPO_ROOT / "results" / rid / "last-message.md")
    if cli == "codex":
        cmd = [*exe, "exec", "-m", model, "-c", f'model_reasoning_effort="{effort}"',
               "--sandbox", CFG.get("codex_sandbox", "workspace-write"),
               "--cd", str(REPO_ROOT), "--json", "-o", last_msg]
        for d in CFG.get("codex_add_dirs", []):
            cmd += ["--add-dir", d]
        cmd.append("-")  # prompt comes from stdin: no Windows quoting problems
    else:
        cmd = [*exe, "-p", "--model", model, "--effort", effort, "--permission-mode", "auto",
               "--add-dir", FOOTAGE_ROOT]
        if worker == "claude-second":
            flag = REPO_ROOT / "local" / "claude-second-session.flag"
            cmd += ["--resume", "claude-second"] if flag.exists() else ["-n", "claude-second"]
    return cmd, cli


def build_prompt(worker: str, cli: str, rid: str) -> str:
    guide = "AGENTS.md" if cli == "codex" else "CLAUDE.md"
    return (f"You are worker {worker} on machine {MACHINE}. Your machine config is machine.local.json. "
            f"Read {guide}, PROTOCOL.md and brief/decisions.md, then do the task in queue/{worker}/{rid}.md exactly. "
            f"Finish by writing results/{rid}/REPORT.md.")


# ---------------------------------------------------------------- safety net for wide sandboxes
def repo_state(path: str) -> dict | None:
    """Snapshot of another git repo: file list, hash of tracked changes, HEAD. None if it is not a repo."""
    p = Path(path)
    if not (p / ".git").exists():
        return None
    g = ["git", "-C", str(p)]
    _, status = run([*g, "status", "--porcelain=v1", "-uall"], timeout=180)
    _, diff = run([*g, "diff", "--no-ext-diff"], timeout=180)
    _, head = run([*g, "rev-parse", "HEAD"], timeout=30)
    return {"status": sorted(status.splitlines()), "diff_hash": hashlib.sha256(diff.encode("utf-8", "replace")).hexdigest(),
            "head": head.strip()}


def snapshot_guards() -> dict:
    snap = {}
    for r in GUARD_REPOS:
        st = repo_state(r)
        if st is None:
            log(f"guard: {r} is not a git repo, skipping")
        else:
            snap[r] = st
    return snap


def guard_changes(before: dict) -> list[str]:
    """Human-readable list of what changed in guarded repos since `before` (empty = untouched)."""
    lines = []
    for r, b in before.items():
        a = repo_state(r)
        if a is None:
            lines.append(f"{r}: could not be read after the task")
            continue
        if a["head"] != b["head"]:
            lines.append(f"{r}: HEAD moved {b['head'][:8]} -> {a['head'][:8]}")
        if a["diff_hash"] != b["diff_hash"]:
            lines.append(f"{r}: the content of tracked files changed")
        added, removed = sorted(set(a["status"]) - set(b["status"])), sorted(set(b["status"]) - set(a["status"]))
        lines += [f"{r}: now listed: {x}" for x in added] + [f"{r}: no longer listed: {x}" for x in removed]
    return lines


def guard_flag(worker: str) -> Path:
    return REPO_ROOT / "local" / f"paused-{worker}.flag"


def guard_paused() -> dict[str, str]:
    out = {}
    for w in MY_WORKERS:
        f = guard_flag(w)
        if f.exists():
            out[w] = f.read_text(encoding="utf-8", errors="replace").splitlines()[0] if f.stat().st_size else "paused"
    return out


# ---------------------------------------------------------------- run one task
def run_task(worker: str, task_file: Path) -> None:
    global current_task
    rid = task_file.stem
    fm, _ = parse_frontmatter(task_file.read_text(encoding="utf-8", errors="replace"))
    rdir = REPO_ROOT / "results" / rid
    rdir.mkdir(parents=True, exist_ok=True)
    cli = REGISTRY.get("workers", {}).get(worker, {}).get("cli", "codex")
    model = str(fm.get("model") or ("opus" if cli == "claude" else "gpt-6-sol"))
    effort = str(fm.get("effort") or ("high" if cli == "claude" else "medium"))
    msg_tail = f"({worker}@{MACHINE})"

    # --- refusals: Astra ban, bad values, wrong worker
    problem = None
    if "astra" in model.lower():
        problem = ("refused", f"Model `{model}` contains 'astra'. GPT-6 Astra is banned (PROTOCOL.md section 5, rule 1). Nothing was run.")
    elif not SAFE_TOKEN.match(model) or not SAFE_TOKEN.match(effort):
        problem = ("failed", f"Model `{model}` or effort `{effort}` contains characters that are not allowed. Nothing was run.")
    elif fm.get("worker") not in (None, worker):
        problem = ("failed", f"Task says worker `{fm.get('worker')}` but it is in queue/{worker}/. Nothing was run.")
    if problem:
        status, why = problem
        write_report(rid, status, worker, why)
        log(f"{rid}: {status} - {why}")
        commit_paths([f"results/{rid}"], f"result {rid} {status} {msg_tail}")
        push_with_retries()
        return

    timeout_min = int(fm.get("timeout_min") or DEFAULT_TIMEOUT_MIN)
    writes = fm.get("writes") or [f"results/{rid}/"]
    write_paths = []
    for w in writes:
        p = (REPO_ROOT / w).resolve()
        try:
            rel = p.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            log(f"{rid}: ignoring writes entry outside the repo: {w}")
            continue
        if rel.split("/")[0] in ("local", ".git"):
            continue
        write_paths.append(rel or ".")

    # --- claim the task
    current_task = rid
    (rdir / "STARTED.json").write_text(json.dumps({
        "id": rid, "machine": MACHINE, "worker": worker, "time": now_iso(), "model": model,
        "effort": effort, "pid": os.getpid(), "timeout_min": timeout_min}, indent=2) + "\n", encoding="utf-8")
    commit_paths([f"results/{rid}/STARTED.json"], f"start {rid} {msg_tail}")
    push_with_retries()
    write_heartbeat("busy")
    log(f"{rid}: starting on {worker} with {model}/{effort}, timeout {timeout_min} min")

    guards_before = snapshot_guards() if GUARD_REPOS else {}

    # --- launch
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    out_log = LOG_DIR / f"task-{rid}.log"
    timed_out = interrupted = False
    exit_code = -1
    try:
        cmd, cli = build_command(worker, fm, rid, "")
        prompt = build_prompt(worker, cli, rid)
        env = dict(os.environ, FOOTAGE_ROOT=FOOTAGE_ROOT, RENDERS_DIR=str(RENDERS_DIR), MACHINE=MACHINE,
                   WORKER=worker, TASK_ID=rid)
        RENDERS_DIR.mkdir(parents=True, exist_ok=True)
        with open(out_log, "w", encoding="utf-8", errors="replace") as fh:
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=fh, stderr=subprocess.STDOUT, cwd=str(REPO_ROOT),
                                    env=env, text=True, encoding="utf-8",
                                    creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
            try:
                proc.stdin.write(prompt)
                proc.stdin.close()
            except OSError:
                pass
            deadline = time.time() + timeout_min * 60
            try:
                while proc.poll() is None:
                    time.sleep(2)
                    if time.time() > deadline:
                        timed_out = True
                        log(f"{rid}: timeout after {timeout_min} min, killing")
                        kill_tree(proc)
                        break
                    if heartbeat_due():
                        write_heartbeat("busy")
            except KeyboardInterrupt:
                interrupted = True
                log(f"{rid}: Ctrl+C, stopping the task")
                kill_tree(proc)
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                kill_tree(proc)
            exit_code = proc.returncode if proc.returncode is not None else -1
        if cli == "claude" and worker == "claude-second" and exit_code == 0:
            (REPO_ROOT / "local").mkdir(exist_ok=True)
            (REPO_ROOT / "local" / "claude-second-session.flag").write_text(now_iso(), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        out_log.write_text(f"listener could not launch the worker: {e}\n", encoding="utf-8")
        log(f"{rid}: launch error: {e}")

    # --- after exit
    tail = tail_lines(out_log)
    if cmd_is_codex(worker):
        scan_codex_events(out_log)
    report = rdir / "REPORT.md"
    status = report_status(rid) if report.exists() else None
    extra = {}
    if not report.exists():
        why = "The listener stopped it (Ctrl+C)." if interrupted else (
            f"The task ran past its time limit ({timeout_min} min) and was killed." if timed_out else
            f"The worker exited (code {exit_code}) without writing REPORT.md.")
        write_report(rid, "failed", worker, f"{why}\n\n## Last 50 lines of output\n\n```\n{tail}\n```")
        status = "failed"
    elif status is None:
        status = "done" if exit_code == 0 else "failed"

    if status == "failed" or exit_code != 0:
        blob = out_log.read_text(encoding="utf-8", errors="replace") if out_log.exists() else ""
        if RATE_RE.search(blob):
            until = dt.datetime.now(dt.timezone.utc) + parse_wait(blob)
            rate_until[worker] = until
            log(f"{rid}: rate limit detected. Pausing {worker} until {until.isoformat()}")
            with open(report, "a", encoding="utf-8", newline="\n") as f:
                f.write(f"\n> Listener note: a rate-limit or quota error was seen. {worker} is paused until {until.isoformat()}. "
                        "The lead should reassign or re-queue this task.\n")

    if guards_before:
        changed = guard_changes(guards_before)
        if changed:
            (REPO_ROOT / "local" / "guard").mkdir(parents=True, exist_ok=True)
            (REPO_ROOT / "local" / "guard" / f"{rid}.txt").write_text("\n".join(changed) + "\n", encoding="utf-8")
            guard_flag(worker).write_text(f"paused after {rid}: a guarded repo changed. Look at local/guard/{rid}.txt, then delete this file.\n", encoding="utf-8")
            log(f"{rid}: SAFETY WARNING - a guarded repo changed ({len(changed)} differences). {worker} is paused.")
            with open(report, "a", encoding="utf-8", newline="\n") as f:
                f.write(f"\n> **SAFETY WARNING (listener):** a repo outside this project that must not be touched changed while this task ran "
                        f"({len(changed)} differences). {worker} on {MACHINE} is now PAUSED until the owner looks at it. "
                        f"Details are kept on that machine only (local/guard/{rid}.txt) because this repo is public.\n")

    roots = [REPO_ROOT / p for p in write_paths]
    notes = enforce_sizes(rid, roots + [rdir])
    if notes:
        with open(report, "a", encoding="utf-8", newline="\n") as f:
            f.write("\n## Files moved out of git by the listener\n\n" + "\n".join(notes) + "\n")

    to_commit = sorted(set([f"results/{rid}"] + [p for p in write_paths if p != "."]))
    commit_paths(to_commit, f"result {rid} {status} {msg_tail}")
    push_with_retries()
    current_task = None
    write_heartbeat()
    log(f"{rid}: finished with status {status}")
    if interrupted:
        raise KeyboardInterrupt


def cmd_is_codex(worker: str) -> bool:
    return REGISTRY.get("workers", {}).get(worker, {}).get("cli") == "codex"


# ---------------------------------------------------------------- startup helpers
def recover_orphans() -> None:
    """A STARTED.json from this machine with no REPORT means the listener died mid-task."""
    for sf in (REPO_ROOT / "results").glob("*/STARTED.json"):
        info = read_json(sf, {})
        rid = sf.parent.name
        if info.get("machine") == MACHINE and info.get("worker") in MY_WORKERS and not (sf.parent / "REPORT.md").exists():
            write_report(rid, "failed", info["worker"], "The listener on this machine stopped or crashed while this task was running. The lead should re-queue it.")
            commit_paths([f"results/{rid}"], f"result {rid} failed (recovered on restart) ({info['worker']}@{MACHINE})")
            log(f"{rid}: was left running by an earlier listener; marked failed")


def acquire_lock() -> Path:
    lock = REPO_ROOT / "local" / "listener.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    if lock.exists():
        try:
            pid = int(lock.read_text().strip())
            out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout if os.name == "nt" else ""
            if str(pid) in out:
                sys.exit(f"Another listener is already running on this machine (pid {pid}). Close it first.")
        except (ValueError, OSError):
            pass
    lock.write_text(str(os.getpid()))
    return lock


def validate() -> None:
    mreg = REGISTRY["machines"][MACHINE]
    for w in MY_WORKERS:
        if w not in mreg.get("workers", []):
            sys.exit(f"Worker '{w}' is not assigned to {MACHINE} in machines/registry.json.")
        if not REGISTRY["workers"].get(w, {}).get("queue"):
            sys.exit(f"Worker '{w}' has no task queue (it is interactive). Remove it from machine.local.json.")
    if not Path(FOOTAGE_ROOT).is_dir():
        log(f"WARNING: footage_root does not exist yet: {FOOTAGE_ROOT}")


def main() -> None:
    global OFFLINE, current_task
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    OFFLINE = args.offline
    validate()
    lock = acquire_lock()
    log(f"listener started: machine={MACHINE} workers={MY_WORKERS} offline={OFFLINE} pid={os.getpid()}")
    try:
        sync()
        recover_orphans()
        write_heartbeat("idle")
        while True:
            ran = False
            for worker in MY_WORKERS:
                if worker in guard_paused():
                    continue
                until = rate_until.get(worker)
                if until and until > dt.datetime.now(dt.timezone.utc):
                    continue
                task = next_task(worker)
                if task:
                    run_task(worker, task)
                    ran = True
                    break
            if args.once:
                break
            if ran:
                sync()
                continue
            wait = SYNC_EVERY_S + random.uniform(0, 8)
            end = time.time() + wait
            while time.time() < end:
                time.sleep(1)
                if heartbeat_due():
                    write_heartbeat()
            sync()
    except KeyboardInterrupt:
        log("Ctrl+C: stopping")
    finally:
        current_task = None
        try:
            write_heartbeat("stopped")
        except Exception as e:  # noqa: BLE001
            log(f"final heartbeat failed: {e}")
        try:
            lock.unlink()
        except OSError:
            pass


if __name__ == "__main__":
    main()
