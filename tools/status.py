"""status.py - one-screen view of all machines, for the lead foreman.

Reads machines/*/heartbeat.json (after `git pull`) and flags stale machines.
A machine is STALE if its heartbeat is older than 15 minutes, or it says "stopped".
Usage: python tools/status.py [--minutes 15]
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, read_json  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=int, default=15)
    args = ap.parse_args()
    reg = read_json(REPO_ROOT / "machines" / "registry.json", {})
    now = dt.datetime.now(dt.timezone.utc)
    print(f"{'machine':<12} {'state':<13} {'age':>8}  {'task':<8} note")
    for m in reg.get("machines", {}):
        hb = read_json(REPO_ROOT / "machines" / m / "heartbeat.json")
        if not hb:
            print(f"{m:<12} {'NO HEARTBEAT':<13} {'-':>8}  {'-':<8} never seen; is the listener running?")
            continue
        t = dt.datetime.fromisoformat(hb["time"].replace("Z", "+00:00"))
        age = (now - t).total_seconds() / 60
        state = hb.get("status", "?")
        note = ""
        if age > args.minutes or state == "stopped":
            note = "STALE: reassign any queued tasks" if hb.get("status") != "stopped" else "STOPPED (listener exited); reassign queued tasks"
        if hb.get("rate_limited_until"):
            note += f" rate-limited until {hb['rate_limited_until']}"
        print(f"{m:<12} {state:<13} {age:>6.1f}m  {str(hb.get('current_task') or '-'):<8} {note}")


if __name__ == "__main__":
    main()
