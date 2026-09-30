"""find_stuck_tasks.py - queued tasks that cannot start because their machine is silent, stopped, paused or rate-limited.

For the lead foreman. Run `git pull` first. It reads machines/*/heartbeat.json and queue/<worker>/*.md, and for every task that
has not started (no STARTED.json, no REPORT.md) whose worker's machine is not healthy, it says WHY and which online worker of the
same kind (Codex or Claude) could take it instead. It never changes anything: reassigning is the lead's decision, done by writing a
NEW task with `redo_of: <old id>` (PROTOCOL.md section 3).

A machine is unhealthy when its heartbeat is older than --minutes (default 15, PROTOCOL.md section 7), or says "stopped",
or the worker is rate-limited or paused by the safety check.

Usage: python tools/find_stuck_tasks.py [--minutes 15]
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, read_json, sync_warnings  # noqa: E402


def parse_time(s):
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def machine_health(machine: str, worker: str, minutes: int, now):
    """Return (healthy, reason, age_minutes)."""
    hb = read_json(REPO_ROOT / "machines" / machine / "heartbeat.json")
    t = parse_time((hb or {}).get("time"))
    if not hb or t is None:
        return False, "never sent a heartbeat", None
    age = (now - t).total_seconds() / 60
    if hb.get("status") == "stopped":
        return False, f"listener STOPPED cleanly {age:.0f} min ago", age
    if age > minutes:
        return False, f"SILENT: last heartbeat {age:.0f} min ago (limit {minutes})", age
    if worker in (hb.get("paused_by_safety_check") or {}):
        return False, "worker PAUSED by the safety check (the owner must look)", age
    until = parse_time(((hb.get("rate_limited_until") or {}).get(worker)))
    if until and until > now:
        return False, f"worker RATE-LIMITED until {until.isoformat()}", age
    return True, f"healthy, heartbeat {age:.0f} min ago, {hb.get('status')}", age


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # the warning symbol crashes old Windows code pages
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=int, default=15)
    args = ap.parse_args()
    reg = read_json(REPO_ROOT / "machines" / "registry.json", {})
    workers = reg.get("workers", {})
    now = dt.datetime.now(dt.timezone.utc)
    pull_stale, msgs = sync_warnings(now)
    for m in msgs:
        print(m)
    if pull_stale:
        print("Not judging stuck tasks: this PC's copy of the heartbeats is out of date, so a machine may only look silent.")
        return

    health = {}
    for w, info in workers.items():
        if info.get("queue"):
            health[w] = machine_health(info["machine"], w, args.minutes, now)

    stuck = 0
    for w, info in workers.items():
        qdir = REPO_ROOT / "queue" / w
        if not info.get("queue") or not qdir.is_dir():
            continue
        ok, why, _ = health[w]
        for f in sorted(qdir.glob("*.md")):
            rid = f.stem
            rdir = REPO_ROOT / "results" / rid
            if (rdir / "STARTED.json").exists() or (rdir / "REPORT.md").exists():
                continue
            if ok:
                continue
            stuck += 1
            print(f"STUCK  {rid}  ({w} on {info['machine']}): {why}")
            options = [o for o, oinfo in workers.items()
                       if o != w and oinfo.get("queue") and oinfo.get("cli") == info.get("cli") and health[o][0]]
            if options:
                print(f"       could go to: " + ", ".join(f"{o} ({workers[o]['machine']}, {health[o][1]})" for o in options))
                print(f"       to reassign: write a NEW task with the same content, worker: {options[0]}, and redo_of: {rid}; then review {rid} as dropped.")
            else:
                print("       no healthy worker of the same kind is online: wait for the machine to return, or tell Vivek.")
    if not stuck:
        print("No stuck tasks: every queued task belongs to a healthy machine.")


if __name__ == "__main__":
    main()
