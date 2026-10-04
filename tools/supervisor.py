"""supervisor.py - keeps every listener of one project working. Runs on the lead's PC, started by `swarm.py start`.

Every minute it probes each listener clone over SSH (tools/swarm.py PROBE) and fixes what it can:

  problem                                     detected by                                 fix
  machine unreachable                         3 failed probes in a row (~3 min)           network failure: queued tasks of its workers move to their lane
                                                                                          pool; tasks it was running get a redo in the pool after 15 min
  listener crashed / never started            no listener process and no loop           start it: schtasks /Run itantra-listener (the user's desktop
                                                                                          session, where Codex works); WMI only if the clone has no task
  listener hung                               process alive, heartbeat file > 12 min old  kill it; the loop (listener_loop.py / run-listener.cmd) restarts it
  git rebase stuck                            .git/rebase-* older than 5 min              git rebase --abort
  dirty working tree (listener idle)          tracked changes for 10 min, no task         git stash push -m "supervisor autosave ..." (never dropped)
  autostash could not be restored             local/autostash-left.flag                   reported (needs a human: it is someone's work)
  worker CLI hung                             task log silent for 20 min                  kill the CLI; listener writes a failed REPORT; one redo in the pool
  worker exited without a REPORT              listener's own failed REPORT                one redo in the pool
  rate-limited worker                         heartbeat rate_limited_until                its queued tasks move to the lane pool
  pushes failing                              unpushed commits, last push > 15 min ago    reported

It only touches the listener clone folders, the listener processes and the worker CLIs those listeners started.
Never: installs, deletes outside the clone, force-pushes, drops stashes, or kills interactive sessions.
Commits go through common.push_files_direct (never through anyone's working tree).
Public status (machine names and states only): machines/supervisor/status.json. Log: local/logs/supervisor.log.

Usage: python tools/supervisor.py [--project P] [--once] [--dry-run]
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import NO_WINDOW, REPO_ROOT, now_iso, push_files_direct, read_json, write_json  # noqa: E402
import swarm  # noqa: E402

EVERY_S = 60
UNREACHABLE_AFTER = 3          # failed probes in a row
RUNNING_GRACE_MIN = 15         # before a task running on an unreachable machine is redone elsewhere
HUNG_LISTENER_S = 12 * 60
STUCK_REBASE_S = 5 * 60
DIRTY_IDLE_S = 10 * 60
SILENT_TASK_S = 20 * 60
STATUS_EVERY_S = 5 * 60
LOG = REPO_ROOT / "local" / "logs" / "supervisor.log"
STATE_FILE = REPO_ROOT / "local" / "supervisor-state.json"
DRY = False

KILL_CLI = r"""
foreach ($p in ($pids -split ',')) { if ($p) { taskkill /F /T /PID $p | Out-Null } }
"killed $pids"
"""
KILL_LISTENER = r"""
Set-Location $repo
if (Test-Path local\listener.lock) { taskkill /F /T /PID ((Get-Content local\listener.lock -Raw).Trim()) | Out-Null; "killed listener" }
"""
ABORT_REBASE = r"""
Set-Location $repo
git rebase --abort 2>&1 | Out-Null
"rebase aborted: " + (-not ((Test-Path .git\rebase-merge) -or (Test-Path .git\rebase-apply)))
"""
AUTOSAVE = r"""
Set-Location $repo
git stash push -m "supervisor autosave $stamp (listener clone was dirty while idle)" 2>&1 | Out-String
"""


def log(msg: str) -> None:
    line = f"{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def act(l: dict, what: str, script: str, params: dict) -> str:
    log(f"{l['name']}: {what}" + (" (dry run)" if DRY else ""))
    if DRY:
        return "dry run"
    rc, out = swarm.ps(l.get("host"), script, {"repo": l["repo"], **params})
    out = out.strip().splitlines()[-1] if out.strip() else f"exit {rc}"
    log(f"{l['name']}: -> {out}")
    return out


# ---------------------------------------------------------------- git view of the queue (from origin, no working tree)
def g(*args: str, timeout: int = 60) -> str:
    try:
        p = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, timeout=timeout, creationflags=NO_WINDOW)
        return (p.stdout or b"").decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return ""


def origin_files(prefixes: tuple[str, ...]) -> set[str]:
    return set(g("ls-tree", "-r", "--name-only", "origin/main", "--", *prefixes).splitlines())


def show(path: str) -> str:
    return g("show", f"origin/main:{path}")


def frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^﻿?---\s*\r?\n(.*?)\r?\n---\s*\r?\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, m.group(2)


def set_fields(text: str, **fields: str) -> str:
    """Change or add front-matter lines."""
    head, _, rest = text.partition("\n---")
    lines = head.splitlines()
    for k, v in fields.items():
        for i, line in enumerate(lines):
            if line.split(":", 1)[0].strip() == k:
                lines[i] = f"{k}: {v}"
                break
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines) + "\n---" + rest


def lane_of(fm: dict, worker: str, reg: dict) -> str:
    lane = (fm.get("lane") or "").lower()
    return lane if lane in ("video", "ppt", "misc") else reg["workers"].get(worker, {}).get("home_lane", "misc")


def move_queued_to_pool(workers: list[str], why: str, reg: dict) -> None:
    """Queued (not started) tasks of these workers go to their lane pool, so any free worker takes them."""
    files = origin_files(("queue", "results", "reviews"))
    changes: dict[str, bytes | None] = {}
    moved = []
    for w in workers:
        for path in sorted(f for f in files if f.startswith(f"queue/{w}/") and f.endswith(".md")):
            rid = Path(path).stem
            if f"results/{rid}/STARTED.json" in files or f"results/{rid}/REPORT.md" in files:
                continue
            text = show(path)
            fm, _ = frontmatter(text)
            if "dropped" in show(f"reviews/{rid}.md")[:200]:
                continue
            if fm.get("pin") == "true":  # a task that must run on this worker (e.g. a final render) stays
                continue
            lane = lane_of(fm, w, reg)
            changes[path] = None
            changes[f"queue/lane-{lane}/{rid}.md"] = set_fields(text, worker="any", lane=lane,
                                                                  moved_by=f"supervisor ({why}, from {w})").encode("utf-8")
            moved.append(f"{rid}->{lane}")
    if moved:
        log(f"moving queued tasks to lane pools ({why}): {', '.join(moved)}")
        if not DRY and not push_files_direct(changes, f"supervisor: move {len(moved)} queued task(s) of {', '.join(workers)} to lane pools ({why})"):
            log("  push failed; will retry next round")


def queue_redo(rid: str, why: str, state: dict, avoid: str = "") -> None:
    """One redo per task, in the lane pool, with redo_of. Only ever once per original task."""
    if rid in state.setdefault("redone", {}) or re.search(r"r\d+$", rid):
        return
    files = origin_files(("queue",))
    src = next((f for f in files if f.endswith(f"/{rid}.md")), None)
    if not src:
        return
    text = show(src)
    fm, _ = frontmatter(text)
    reg = read_json(REPO_ROOT / "machines" / "registry.json", {})
    w = Path(src).parent.name
    lane = lane_of(fm, w if not w.startswith("lane-") else "", reg) if not w.startswith("lane-") else w[5:]
    new_id = f"{rid}r1"
    body = set_fields(text, id=new_id, worker="any", lane=lane, redo_of=rid, created_by="supervisor")
    if avoid:  # never hand the redo back to the worker that just hit its limit
        body = set_fields(body, avoid_worker=avoid)
    body = body.replace(f"results/{rid}/", f"results/{new_id}/")
    body += f"\n\n## Note from the supervisor\nRedo of {rid}: {why}. Read results/{rid}/ first if it exists; continue from there.\n"
    log(f"{rid}: queueing redo {new_id} in lane {lane} ({why})")
    state["redone"][rid] = new_id
    if not DRY:
        push_files_direct({f"queue/lane-{lane}/{new_id}.md": body.encode("utf-8")}, f"supervisor: redo {rid} as {new_id} ({why})")


def check_failed_reports(state: dict) -> None:
    """A REPORT the listener wrote itself (worker crashed, hung, exited without a report) gets one redo,
    unless it was a rate limit (the task is fine; the worker was not) - that one is also redone."""
    files = origin_files(("results",))
    for path in sorted(f for f in files if f.endswith("/REPORT.md")):
        rid = path.split("/")[1]
        if rid in state.setdefault("seen_reports", []):
            continue
        state["seen_reports"].append(rid)
        if not state.get("baseline_done"):
            continue  # everything that existed when the supervisor first ran is history, not new work
        text = show(path)
        fm, _ = frontmatter(text)
        if fm.get("status") == "failed" and fm.get("written_by") == "listener":
            rl = "rate-limit" in text
            why = "rate limit" if rl else "worker stopped without a report or was killed"
            # never hand a redo straight back to the worker that just failed it (a limit it did not report,
            # a broken environment...): another worker takes it, or it waits until the lead reassigns it
            queue_redo(rid, why, state, avoid=fm.get("worker", ""))
    state["baseline_done"] = True


# ---------------------------------------------------------------- one round
def age_s(iso: str | None) -> float | None:
    try:
        t = dt.datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return (dt.datetime.now(dt.timezone.utc) - t).total_seconds()
    except (TypeError, ValueError):
        return None


def handle(l: dict, d: dict, state: dict, reg: dict) -> str:
    name = l["name"]
    st = state.setdefault("machines", {}).setdefault(name, {})
    workers = reg["machines"].get(name, {}).get("listener_workers", [])
    if not d.get("reachable"):
        st["fails"] = st.get("fails", 0) + 1
        st.setdefault("unreachable_since", now_iso())
        if st["fails"] == UNREACHABLE_AFTER:
            log(f"{name}: unreachable {UNREACHABLE_AFTER} times in a row -> network failure")
            move_queued_to_pool(workers, f"{name} unreachable", reg)
        if st["fails"] >= UNREACHABLE_AFTER and (age_s(st["unreachable_since"]) or 0) > RUNNING_GRACE_MIN * 60:
            files = origin_files(("results",))
            for f in sorted(x for x in files if x.endswith("/STARTED.json")):
                rid = f.split("/")[1]
                if f"results/{rid}/REPORT.md" in files:
                    continue
                info = json.loads(show(f) or "{}")
                if info.get("machine") == name:
                    queue_redo(rid, f"{name} lost its network while running it", state)
        return "UNREACHABLE"
    if st.get("fails", 0) >= UNREACHABLE_AFTER:
        log(f"{name}: reachable again")
    st["fails"] = 0
    st.pop("unreachable_since", None)
    if not d.get("repo_ok"):
        return "repo folder missing"
    notes = []

    # stuck rebase first: nothing else works while it is there
    if d.get("rebase_age") is not None and d["rebase_age"] > STUCK_REBASE_S:
        act(l, f"rebase stuck for {d['rebase_age']}s -> abort", ABORT_REBASE, {})
        notes.append("rebase aborted")

    if d.get("stop_flag"):
        return "stopped by swarm stop"
    if not d.get("listener_alive") and not d.get("loop_alive"):
        log(f"{name}: listener not running -> starting it")
        if not DRY:
            log(f"{name}: -> {swarm.start_one(l)}")
        return "listener started"
    hb_age = d.get("hb_age")
    if d.get("listener_alive") and hb_age is not None and hb_age > HUNG_LISTENER_S:
        act(l, f"heartbeat {hb_age}s old while the listener runs -> hung, killing it (the listener loop restarts it)", KILL_LISTENER, {})
        return "hung listener restarted"

    task = d.get("current_task")
    if task and d.get("task_log_age") is not None and d["task_log_age"] > SILENT_TASK_S:
        cli = [c.split(":")[0] for c in d.get("children", []) if re.search(r":(codex|claude|node)\.exe$", c, re.I)]
        if cli:
            act(l, f"{task}: no output for {d['task_log_age']}s -> killing the worker CLI", KILL_CLI, {"pids": ",".join(cli)})
            notes.append(f"killed hung {task}")

    if d.get("dirty") and not task and d.get("hb_status") != "busy":
        first = st.setdefault("dirty_since", time.time())
        if time.time() - first > DIRTY_IDLE_S:
            act(l, f"working tree dirty while idle ({', '.join(d['dirty'][:3])}) -> autosave stash", AUTOSAVE,
                {"stamp": dt.datetime.now().strftime("%Y-%m-%d %H:%M")})
            st.pop("dirty_since", None)
            notes.append("dirty tree stashed")
    else:
        st.pop("dirty_since", None)

    if d.get("autostash_flag") and not st.get("autostash_reported"):
        log(f"{name}: WARNING an autostash could not be re-applied; someone's local changes are in that clone's stash list")
        st["autostash_reported"] = True
        notes.append("AUTOSTASH LEFT (needs a human)")

    rl = d.get("rate_limited") or {}
    if rl:
        limited = [w for w in rl if w in workers]
        if limited and not st.get("rl_moved"):
            move_queued_to_pool(limited, f"{', '.join(limited)} rate-limited", reg)
            st["rl_moved"] = True
        notes.append("rate-limited")
    else:
        st.pop("rl_moved", None)

    if (d.get("unpushed") or 0) > 0 and (age_s(d.get("last_push_ok")) or 1e9) > 15 * 60:
        notes.append(f"{d['unpushed']} unpushed commit(s)")
    state_word = "busy " + task if task else (d.get("hb_status") or "?")
    return state_word + (" · " + ", ".join(notes) if notes else "")


def round_once(cfg: dict, state: dict) -> dict:
    reg = read_json(REPO_ROOT / "machines" / "registry.json", {})
    g("fetch", "-q", "origin", "main", timeout=60)
    ls = swarm.pick(cfg, None)
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        probes = list(ex.map(swarm.probe, ls))
    summary = {}
    for l, d in zip(ls, probes):
        try:
            summary[l["name"]] = handle(l, d, state, reg)
        except Exception as e:  # noqa: BLE001 - one bad machine must not stop the others
            log(f"{l['name']}: supervisor error {e!r}")
            summary[l["name"]] = "supervisor error"
    try:
        check_failed_reports(state)
    except Exception as e:  # noqa: BLE001
        log(f"report check error {e!r}")
    return summary


def single_instance(project: str) -> bool:
    """A named mutex, so a second supervisor (started from another clone, or by `swarm start`) cannot double-act on the listeners."""
    if os.name != "nt":
        return True
    import ctypes
    global _MUTEX
    _MUTEX = ctypes.windll.kernel32.CreateMutexW(None, False, f"Local\\itantra-supervisor-{project}")
    return ctypes.windll.kernel32.GetLastError() != 183  # ERROR_ALREADY_EXISTS


_MUTEX = None


def main() -> None:
    global DRY
    ap = argparse.ArgumentParser()
    ap.add_argument("--project")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    DRY = a.dry_run
    cfg = swarm.load_config(a.project)
    swarm.CURRENT_PROJECT = cfg.get("project", "")
    pidf = REPO_ROOT / "local" / "supervisor.pid"
    if not a.once:
        if not single_instance(swarm.CURRENT_PROJECT):
            log("another supervisor is already running for this project on this PC: exiting")
            return
        pidf.write_text(str(os.getpid()))
    state = read_json(STATE_FILE, {}) or {}
    log(f"supervisor started (pid {os.getpid()}, project {swarm.CURRENT_PROJECT}, dry run {DRY})")
    last_status = 0.0
    while True:
        started = time.time()
        summary = round_once(cfg, state)
        write_json(STATE_FILE, state)
        if a.once:
            for k, v in summary.items():
                print(f"{k:<18} {v}")
            return
        if time.time() - last_status > STATUS_EVERY_S:
            up = sum(1 for v in summary.values() if v != "UNREACHABLE")
            public = {"time": now_iso(), "summary": f"{up}/{len(summary)} machines reachable",
                      "machines": {k: v for k, v in summary.items()}}
            if push_files_direct({"machines/supervisor/status.json": (json.dumps(public, indent=2) + "\n").encode()},
                                 "supervisor status"):
                last_status = time.time()
        time.sleep(max(5, EVERY_S - (time.time() - started)))


if __name__ == "__main__":
    main()
