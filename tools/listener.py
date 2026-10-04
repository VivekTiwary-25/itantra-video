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
import uuid
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (NO_WINDOW, REPO_ROOT, SAFE_TOKEN, git, load_machine_config, now_iso, read_json, run, update_sync_state, which, worker_path, write_json)  # noqa: E402

SYNC_EVERY_S = 30
HEARTBEAT_EVERY_S = 300
MAX_FILE_MB = 20
MAX_PREVIEW_MB = 10
PUSH_TRIES = 8
HEARTBEAT_PUSH_BUDGET = 90  # seconds: one push cycle may not take longer, so a dead connection cannot freeze the listener
RESULT_PUSH_BUDGET = 240  # seconds for result / start commits; anything left over is retried on later cycles
NET_TIMEOUT = 45  # seconds for any single network git call: a half-dead connection must not block the listener for minutes
NET = ["-c", "http.lowSpeedLimit=1000", "-c", "http.lowSpeedTime=20"]  # abort a transfer that has stalled for 20 s
DEFAULT_TIMEOUT_MIN = 60
RATE_RE = re.compile(r"rate.?limit(ed| reached| exceeded)|usage limit|too many requests|\b429\b|quota (exceeded|reached)|exceeded your|limit reached|try again (in|later|at)", re.I)
STATUS_RE = re.compile(r"^\s*status\s*:\s*[\"']?(done|failed|refused)\b", re.I | re.M)

CFG = load_machine_config()
MACHINE = CFG["machine"]
REGISTRY = read_json(REPO_ROOT / "machines" / "registry.json", {})
MY_WORKERS: list[str] = CFG["workers"]
FOOTAGE_ROOT = CFG["footage_root"]
RENDERS_DIR = Path(CFG["renders_dir"])
GUARD_REPOS: list[str] = CFG.get("guard_repos", [])  # other repos that no task may change
LOG_DIR = REPO_ROOT / "local" / "logs"
TASK_TMP = REPO_ROOT / "local" / "tmp"  # workers get this as TEMP/TMP: inside the repo, so workspace-write allows it
OFFLINE = False

rate_until: dict[str, dt.datetime] = {}
RATE_FILE = REPO_ROOT / "local" / "rate-limits.json"  # survives listener restarts (a tools/ pull restarts us)


def load_rate_until() -> None:
    try:
        data = json.loads(RATE_FILE.read_text(encoding="utf-8"))
        for w, iso in data.items():
            rate_until[w] = dt.datetime.fromisoformat(iso)
    except Exception:  # noqa: BLE001 - missing or bad file means no pauses
        pass


def save_rate_until() -> None:
    try:
        RATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        RATE_FILE.write_text(json.dumps({w: t.isoformat() for w, t in rate_until.items()}), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
last_usage: dict = {}
last_codex_rate_limits: dict | None = None
current_task: str | None = None
last_heartbeat = 0.0
warned_blocked: set[str] = set()
restarting = False
RESTART_CODE = 75
STOP_FLAG = REPO_ROOT / "local" / "listener.stop"  # written by `swarm stop`; the loops (listener_loop.py, run-listener.cmd) do not restart while it exists


def source_stamp() -> str:
    """Fingerprint of the tool code. When a git pull changes it, the listener restarts itself between tasks."""
    h = hashlib.sha256()
    for f in sorted((REPO_ROOT / "tools").glob("*.py")):
        try:
            h.update(f.name.encode() + f.read_bytes())
        except OSError:
            pass
    return h.hexdigest()


START_STAMP = source_stamp()


def check_for_update() -> None:
    global restarting
    if source_stamp() != START_STAMP:
        restarting = True
        log("tool code changed after git pull: restarting to load it (the listener loop restarts it automatically)")
        sys.exit(RESTART_CODE)


def clean_tmp(days: int = 2) -> None:
    """Delete week-old scratch files so local/tmp cannot grow without limit."""
    cutoff = time.time() - days * 86400
    if not TASK_TMP.is_dir():
        return
    for child in TASK_TMP.iterdir():
        try:
            if child.stat().st_mtime < cutoff:
                shutil.rmtree(child, ignore_errors=True) if child.is_dir() else child.unlink()
        except OSError:
            pass


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


def count_unpushed() -> int | None:
    rc, out = git("rev-list", "--count", f"origin/{branch()}..HEAD")
    try:
        return int(out.strip()) if rc == 0 else None
    except ValueError:
        return None


def has_unpushed_results() -> bool:
    """Whether a result commit still needs delivery to GitHub."""
    rc, out = git("rev-list", "--count", f"origin/{branch()}..HEAD", "--", "results")
    try:
        return rc == 0 and int(out.strip()) > 0
    except ValueError:
        return False


def stash_count() -> int:
    return len([l for l in git("stash", "list")[1].splitlines() if l.strip()])


def pull_rebase() -> tuple[int, str]:
    """Time out only the network fetch; let the local rebase finish or abort cleanly.
    Listener clones should be clean. If an autostash cannot be put back, say so loudly (local/autostash-left.flag,
    read by the supervisor) instead of leaving the work silently in the stash list, as happened on 30 Sep."""
    rc, out = git(*NET, "fetch", "origin", branch(), timeout=NET_TIMEOUT)
    if rc != 0:
        return rc, out
    before = stash_count()
    rc, rebase_out = git("rebase", "--autostash", "FETCH_HEAD", timeout=None)
    if rc != 0:
        git("rebase", "--abort", timeout=None)
    if stash_count() > before:
        flag = REPO_ROOT / "local" / "autostash-left.flag"
        flag.write_text(f"{now_iso()} local changes could not be re-applied after a pull; they are in stash@{{0}}\n", encoding="utf-8")
        log("WARNING: local uncommitted changes could not be re-applied after the pull; they are kept in stash@{0}")
    return rc, out + rebase_out


def sync() -> bool:
    if OFFLINE:
        return True
    rc, out = pull_rebase()
    if rc != 0:
        if "couldn't find remote ref" in out:
            return True  # remote branch not created yet
        log(f"git sync failed: {out.strip()[:300]}")
        update_sync_state(last_pull_error_at=now_iso())
        return False
    update_sync_state(last_pull_ok=now_iso(), unpushed=count_unpushed())
    return True


def push_with_retries(tries: int = PUSH_TRIES, quiet: bool = False, budget: int | None = None) -> bool:
    """Pull/rebase then push, retrying transient network errors and concurrent pushes.
    `budget` (seconds, default 90 for quiet heartbeat pushes and 240 otherwise) stops retries between attempts.
    Network calls have their own timeout; the local rebase is never interrupted by either limit."""
    if OFFLINE:
        return True
    if budget is None:
        budget = HEARTBEAT_PUSH_BUDGET if quiet else RESULT_PUSH_BUDGET
    start = time.time()
    out_of_time = False
    for attempt in range(1, tries + 1):
        rc, out = pull_rebase()
        if rc != 0:
            log(f"push attempt {attempt}/{tries}: pull/rebase failed: {out.strip()[:200]}")
        else:
            rc, out = git(*NET, "push", "origin", "HEAD", timeout=NET_TIMEOUT)
            if rc == 0:
                update_sync_state(last_push_ok=now_iso(), unpushed=0)
                log(f"push succeeded on attempt {attempt}/{tries}")
                return True
            log(f"push attempt {attempt}/{tries} failed: {out.strip()[:200]}")
        if attempt < tries:
            wait = random.uniform(3, 15)
            if time.time() - start + wait > budget:
                out_of_time = True
                break
            time.sleep(wait)
    if not quiet:
        why = f"time budget of {budget} s used up after {time.time() - start:.0f} s" if out_of_time else "retries used up"
        log(f"push gave up ({why}); the commit stays local and will be retried on later cycles")
    update_sync_state(last_push_error_at=now_iso(), unpushed=count_unpushed())
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
    sync_state = read_json(REPO_ROOT / "local" / "sync-state.json", {}) or {}
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
        "unpushed_commits": count_unpushed() or 0,
        "last_push_ok": sync_state.get("last_push_ok"),
    }
    rel = f"machines/{MACHINE}/heartbeat.json"
    write_json(REPO_ROOT / rel, hb)
    last_heartbeat = time.time()
    update_sync_state(listener_seen=now_iso(), listener_status=status)
    if commit_paths([rel], f"heartbeat {MACHINE} {status}") and push:
        push_with_retries(quiet=True)


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


LANES = ("video", "ppt", "misc")


def lane_order(worker: str) -> list[str]:
    """Home lane first, then the others: an idle worker may take tasks from any lane."""
    home = REGISTRY.get("workers", {}).get(worker, {}).get("home_lane")
    return ([home] if home in LANES else []) + [l for l in LANES if l != home]


def runnable(f: Path, worker: str, pool: bool) -> bool:
    rid = f.stem
    rdir = REPO_ROOT / "results" / rid
    if (rdir / "STARTED.json").exists() or (rdir / "REPORT.md").exists():
        return False
    if review_verdict(rid) == "dropped":  # the lead cancels a queued task by writing reviews/<id>.md verdict: dropped
        return False
    fm, _ = parse_frontmatter(f.read_text(encoding="utf-8", errors="replace"))
    if pool:  # a lane task may limit who takes it: cli: codex|claude, machine: <name>
        winfo = REGISTRY.get("workers", {}).get(worker, {})
        if fm.get("cli") not in (None, "any", winfo.get("cli")):
            return False
        if fm.get("machine") not in (None, "any", MACHINE):
            return False
        if fm.get("worker") not in (None, "any", worker):
            return False
        if worker in (fm.get("avoid_worker") or "").replace(",", " ").split():  # e.g. a redo after this worker's rate limit
            return False
    import importlib.util
    if any(importlib.util.find_spec(m) is None for m in (fm.get("requires") or [])):  # e.g. requires: [pptx]
        return False
    return deps_ready(rid, fm.get("depends_on") or [])


def for_cli(fm: dict, key: str, cli: str):
    """model / effort for this CLI: `model_codex:` / `model_claude:` win over `model:` (lane tasks can go to either)."""
    return fm.get(f"{key}_{cli}") or fm.get(key)


def next_task(worker: str) -> tuple[Path, bool] | None:
    """The worker's own queue first, then the lane pools queue/lane-<lane>/ (home lane first).
    Returns (task file, is_pool_task)."""
    qdirs = [(REPO_ROOT / "queue" / worker, False)] + [(REPO_ROOT / "queue" / f"lane-{l}", True) for l in lane_order(worker)]
    for qdir, pool in qdirs:
        if not qdir.is_dir():
            continue
        for f in sorted(qdir.glob("*.md"), key=lambda f: id_sort_key(f.stem)):
            if runnable(f, worker, pool):
                return f, pool
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
                notes.append(f"- `{f.relative_to(REPO_ROOT).as_posix()}` ({mb:.1f} MB) was too big for git. Moved to local path: `RENDERS:{dest.relative_to(RENDERS_DIR).as_posix()}` (inside renders_dir on {MACHINE})")
                log(f"moved oversize file {f.name} ({mb:.1f} MB) to {dest}")
    return notes


def kill_tree(proc: subprocess.Popen) -> None:
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, timeout=30, creationflags=NO_WINDOW)
        else:
            proc.kill()
    except Exception as e:  # noqa: BLE001
        log(f"kill failed: {e}")


def error_text(blob: str, cli: str) -> str:
    """The part of a worker's output that can carry a real error. Never the tool output or the model's
    own messages: those echo our docs (which mention 'rate limit') and caused a false alarm on yash-pc."""
    lines = blob.splitlines()
    if cli != "codex":
        return "\n".join(lines[-40:])
    keep = []
    for ln in lines:
        if not ln.startswith("{"):
            keep.append(ln)  # plain stderr line
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            keep.append(ln)
            continue
        if ev.get("type") in ("error", "turn.failed"):
            keep.append(ln)
    return "\n".join(keep)


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
SESSION_FILE = REPO_ROOT / "local" / "claude-second-session.json"
UUID_RE = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"


def session_args() -> list[str]:
    """How claude-second continues its conversation between tasks. Tracked by session ID, never by name:
    two sessions with the same name make `--resume <name>` fail ('matches 2 sessions'), as happened on yojitth-pc."""
    override = read_json(REPO_ROOT / "machine.local.json", CFG).get("claude_session_id")
    if override:
        return ["--resume", override]
    st = read_json(SESSION_FILE)
    if st and st.get("id"):
        return ["--resume", st["id"]] if st.get("created") else ["--session-id", st["id"]]
    if (REPO_ROOT / "local" / "claude-second-session.flag").exists():  # older installs resumed by name; heal_session() upgrades them
        return ["--resume", "claude-second"]
    sid = str(uuid.uuid4())
    write_json(SESSION_FILE, {"id": sid, "created": False})
    return ["--session-id", sid]


def mark_session_created() -> None:
    st = read_json(SESSION_FILE)
    if st and st.get("id") and not st.get("created"):
        st["created"] = True
        write_json(SESSION_FILE, st)


def heal_session(text: str) -> bool:
    """Fix the two session errors we have seen. Returns True if the task should be retried once."""
    m = re.search(r"matches [0-9]+ sessions.*?(" + UUID_RE + ")", text, re.S)
    if m:  # the message lists the newest session first
        write_json(SESSION_FILE, {"id": m.group(1), "created": True})
        log(f"claude-second: name was ambiguous, now tracking session {m.group(1)[:8]}... by ID")
        return True
    if "is already in use" in text:
        st = read_json(SESSION_FILE)
        if st and st.get("id"):
            st["created"] = True
            write_json(SESSION_FILE, st)
            log("claude-second: session already exists, switching to resume")
            return True
    return False


def build_command(worker: str, fm: dict, rid: str, prompt_file_hint: str) -> tuple[list[str], str]:
    winfo = REGISTRY.get("workers", {}).get(worker, {})
    cli = winfo.get("cli", "codex")
    override = CFG.get("cli_overrides", {}).get(cli)
    exe = list(override) if isinstance(override, list) else ([override] if override else [which(cli)])
    if not exe[0]:
        raise RuntimeError(f"'{cli}' was not found on PATH. Run tools/doctor.py.")
    model = for_cli(fm, "model", cli) or ("opus" if cli == "claude" else "gpt-6-sol")
    effort = for_cli(fm, "effort", cli) or ("high" if cli == "claude" else "medium")
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
            cmd += session_args()
    return cmd, cli


def build_prompt(worker: str, cli: str, rid: str, task_rel: str) -> str:
    guide = "AGENTS.md" if cli == "codex" else "CLAUDE.md"
    return (f"You are worker {worker} on machine {MACHINE}. Your machine config is machine.local.json. "
            f"Read {guide}, PROTOCOL.md and brief/decisions.md, then do the task in {task_rel} exactly. "
            f"Finish by writing results/{rid}/REPORT.md.")


# ---------------------------------------------------------------- keep private paths out of the (public) repo
TEXT_EXT = {'.md', '.txt', '.json', '.jsonl', '.html', '.css', '.js', '.mjs', '.py', '.csv', '.srt', '.vtt', '.log', '.xml', '.yml', '.yaml'}
_HOME = str(Path.home())
_SEP = "(?:" + chr(92) * 2 + "+|/)"  # one or more backslashes, or a forward slash: logs nest paths inside JSON inside JSON


def path_regex(path: str) -> re.Pattern:
    return re.compile(_SEP.join(re.escape(part) for part in re.split("[" + chr(92) * 2 + "/]+", path) if part), re.I)


# most specific first: renders_dir sits inside repo_root, which may sit inside the home folder
REDACTIONS = [(path_regex(v), label) for v, label in ((CFG.get("renders_dir"), "<RENDERS_DIR>"), (CFG.get("footage_root"), "<FOOTAGE_ROOT>"),
                                                       (CFG.get("repo_root"), "<REPO>"), (_HOME, "<HOME>")) if v]
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:[.][A-Za-z0-9-]+)*[.][A-Za-z]{2,}")
ALLOWED_EMAIL_TAILS = ("users.noreply.github.com", "noreply@anthropic.com")
SECRET_RE = re.compile(r"gh[opusr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----")


def text_files(roots: list[Path]):
    seen: set[str] = set()
    for root in roots:
        files = [root] if root.is_file() else ([p for p in root.rglob("*") if p.is_file()] if root.exists() else [])
        for f in files:
            key = str(f.resolve()).lower()
            if key in seen:
                continue
            seen.add(key)
            if f.suffix.lower() in TEXT_EXT and f.stat().st_size <= 5 * 1024 * 1024:
                yield f


def redact_home_paths(roots: list[Path]) -> int:
    """Replace this PC's private paths (home, repo, footage, renders) with placeholders in text files about to be committed."""
    n = 0
    for f in text_files(roots):
        try:
            text = f.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new = text
        for rx, label in REDACTIONS:
            new, k = rx.subn(label, new)
            n += k
        if new != text:
            f.write_bytes(new.encode("utf-8"))
    return n


def find_private_data(roots: list[Path]) -> list[tuple[Path, str]]:
    """Emails (other than GitHub/Anthropic no-reply addresses) and token-like strings cannot be safely rewritten: block them."""
    bad = []
    for f in text_files(roots):
        if ".min." in f.name.lower() or {"vendor", "node_modules"} & {part.lower() for part in f.parts}:
            continue  # libraries such as gsap.min.js name their authors in the license header
        try:
            text = f.read_bytes().decode("utf-8", "replace")
        except OSError:
            continue
        if SECRET_RE.search(text):
            bad.append((f, "a token or key"))
        elif any(not m.group(0).lower().endswith(ALLOWED_EMAIL_TAILS) for m in EMAIL_RE.finditer(text)):
            bad.append((f, "an email address"))
    return bad


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
def run_task(worker: str, task_file: Path, _healed: bool = False, pool: bool = False) -> None:
    global current_task
    rid = task_file.stem
    task_rel = task_file.relative_to(REPO_ROOT).as_posix()
    fm, _ = parse_frontmatter(task_file.read_text(encoding="utf-8", errors="replace"))
    rdir = REPO_ROOT / "results" / rid
    rdir.mkdir(parents=True, exist_ok=True)
    cli = REGISTRY.get("workers", {}).get(worker, {}).get("cli", "codex")
    model = str(for_cli(fm, "model", cli) or ("opus" if cli == "claude" else "gpt-6-sol"))
    effort = str(for_cli(fm, "effort", cli) or ("high" if cli == "claude" else "medium"))
    msg_tail = f"({worker}@{MACHINE})"

    # --- refusals: Astra ban, bad values, wrong worker
    problem = None
    if "astra" in model.lower():
        problem = ("refused", f"Model `{model}` contains 'astra'. GPT-6 Astra is banned (PROTOCOL.md section 5, rule 1). Nothing was run.")
    elif not SAFE_TOKEN.match(model) or not SAFE_TOKEN.match(effort):
        problem = ("failed", f"Model `{model}` or effort `{effort}` contains characters that are not allowed. Nothing was run.")
    elif not pool and fm.get("worker") not in (None, worker):
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
    start_msg = f"start {rid} {msg_tail}"
    committed = commit_paths([f"results/{rid}/STARTED.json"], start_msg)
    pushed = push_with_retries()
    if pool and not pushed:
        # Lane tasks are open to every worker: only run one once our claim is on GitHub. If another listener
        # claimed it first (its STARTED.json makes our rebase conflict) or the network is down, undo our claim.
        if committed and git("log", "-1", "--format=%s")[1].strip() == start_msg:
            git("reset", "-q", "--keep", "HEAD~1")
        (rdir / "STARTED.json").unlink(missing_ok=True)
        current_task = None
        log(f"{rid}: could not publish the claim (taken by another worker, or no network); not running it")
        return
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
        prompt = build_prompt(worker, cli, rid, task_rel)
        env = dict(os.environ, FOOTAGE_ROOT=FOOTAGE_ROOT, RENDERS_DIR=str(RENDERS_DIR), MACHINE=MACHINE,
                   WORKER=worker, TASK_ID=rid, HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1")
        env["PATH"] = worker_path(read_json(REPO_ROOT / "machine.local.json", CFG), env.get("PATH", ""))  # re-read: path_prepend edits apply at once
        TASK_TMP.mkdir(parents=True, exist_ok=True)
        env.update(TEMP=str(TASK_TMP), TMP=str(TASK_TMP), TMPDIR=str(TASK_TMP))
        RENDERS_DIR.mkdir(parents=True, exist_ok=True)
        with open(out_log, "w", encoding="utf-8", errors="replace") as fh:
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=fh, stderr=subprocess.STDOUT, cwd=str(REPO_ROOT),
                                    env=env, text=True, encoding="utf-8",
                                    creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | NO_WINDOW)
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
            mark_session_created()
    except Exception as e:  # noqa: BLE001
        out_log.write_text(f"listener could not launch the worker: {e}\n", encoding="utf-8")
        log(f"{rid}: launch error: {e}")

    if (worker == "claude-second" and exit_code != 0 and not _healed and not interrupted and not timed_out
            and out_log.exists() and heal_session(out_log.read_text(encoding="utf-8", errors="replace"))):
        log(f"{rid}: retrying once after fixing the session")
        current_task = None
        return run_task(worker, task_file, _healed=True, pool=False)  # the claim is already on GitHub

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
        blob = error_text(out_log.read_text(encoding="utf-8", errors="replace"), cli) if out_log.exists() else ""
        if RATE_RE.search(blob):
            until = dt.datetime.now(dt.timezone.utc) + parse_wait(blob)
            rate_until[worker] = until
            save_rate_until()
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
    scrubbed = redact_home_paths(roots + [rdir])
    if scrubbed:
        log(f"{rid}: replaced {scrubbed} private home-folder path(s) with <HOME> before committing")
    blocked = find_private_data(roots + [rdir])
    if blocked:
        qdir = REPO_ROOT / "local" / "quarantine" / rid
        qdir.mkdir(parents=True, exist_ok=True)
        names = []
        for f, kind in blocked:
            shutil.move(str(f), str(qdir / f.name))
            names.append(f"{f.name} ({kind})")
        log(f"{rid}: BLOCKED from the public repo: " + ", ".join(names) + " (moved to local/quarantine)")
        status = "failed"
        why = ("Files were held back because they looked like they contain private data (this repo is public): "
               + ", ".join(names) + ". The owner of this machine should look in local/quarantine/" + rid + ", then the lead can re-queue the task.")
        if any(f.name == "REPORT.md" and f.parent == rdir for f, _ in blocked) or not report.exists():
            write_report(rid, "failed", worker, why)
        else:  # the worker's own report is fine: keep it, add the warning, set the status to failed
            text = report.read_text(encoding="utf-8-sig")
            text = re.sub(r"(?im)^status\s*:\s*\w+", "status: failed", text, count=1)
            report.write_text(text.rstrip() + "\n\n> **Listener warning:** " + why + "\n", encoding="utf-8", newline="\n")
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
            # Only a live listener.py counts: after a reboot Windows reuses PIDs, and a stale lock blocked yojitth-pc on 2 Oct.
            cmdline = subprocess.run(["powershell", "-NoProfile", "-Command",
                                      f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine"],
                                     capture_output=True, text=True, creationflags=NO_WINDOW).stdout if os.name == "nt" else ""
            if pid != os.getpid() and "listener.py" in cmdline:
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
        clean_tmp()
        load_rate_until()
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
                found = next_task(worker)
                if found:
                    task, pool = found
                    try:
                        run_task(worker, task, pool=pool)
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:  # noqa: BLE001
                        import traceback
                        log(f"{task.stem}: UNEXPECTED ERROR in the listener, marking the task failed and carrying on: {e}")
                        log(traceback.format_exc())
                        current_task = None
                        if not (REPO_ROOT / "results" / task.stem / "REPORT.md").exists():
                            write_report(task.stem, "failed", worker, f"The listener hit an unexpected error while handling this task: {type(e).__name__}. The lead should re-queue it.")
                        commit_paths([f"results/{task.stem}"], f"result {task.stem} failed (listener error) ({worker}@{MACHINE})")
                        push_with_retries()
                    ran = True
                    break
            if args.once or STOP_FLAG.exists():
                if STOP_FLAG.exists():
                    log("local/listener.stop found: stopping (swarm stop)")
                break
            if ran:
                sync()
                if has_unpushed_results():
                    log("unpushed result commit detected; retrying delivery")
                    push_with_retries()
                check_for_update()
                continue
            wait = SYNC_EVERY_S + random.uniform(0, 8)
            end = time.time() + wait
            while time.time() < end and not STOP_FLAG.exists():
                time.sleep(1)
                if heartbeat_due():
                    write_heartbeat()
            sync()
            if has_unpushed_results():
                log("unpushed result commit detected; retrying delivery")
                push_with_retries()
            check_for_update()
    except KeyboardInterrupt:
        log("Ctrl+C: stopping")
    finally:
        current_task = None
        try:
            write_heartbeat("restarting" if restarting else "stopped")
        except Exception as e:  # noqa: BLE001
            log(f"final heartbeat failed: {e}")
        try:
            lock.unlink()
        except OSError:
            pass


if __name__ == "__main__":
    main()
