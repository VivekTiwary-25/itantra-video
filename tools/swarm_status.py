"""swarm_status.py - the swarm banner. Real data only.

Reads machines/registry.json, machines/<machine>/heartbeat.json and local/claude-usage.json.
ONLINE = heartbeat under 10 minutes old (and the listener has not said "stopped").
Anything else shows OFFLINE with "last seen X ago", or "never seen" if there is no data at all.
The lead is interactive (no listener), so it counts as ONLINE when the status-line file
local/claude-usage.json was refreshed in the last 10 minutes.

The lead runs it as `python tools/swarm_status.py --as-lead`. That flag first records
machines/<lead machine>/lead-heartbeat.json ("the lead is running right now"), so the lead shows ONLINE.
Without the flag nothing is written, so a human or another agent running the banner cannot fake the lead.

Usage: python tools/swarm_status.py [--as-lead]     (run `git pull` first to get fresh heartbeats)
"""
import argparse
import datetime as dt
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, now_iso, read_json, write_json  # noqa: E402

ONLINE_MINUTES = 10
WIDTH = 55
NODE_W, AGENT_W, MODEL_W = 13, 15, 16


def parse_time(s):
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def ago(t, now):
    if t is None:
        return "never seen"
    secs = max(0, (now - t).total_seconds())
    if secs < 90:
        return "just now"
    if secs < 3600:
        return f"{secs / 60:.0f}m ago"
    if secs < 86400:
        return f"{secs / 3600:.0f}h ago"
    return f"{secs / 86400:.0f}d ago"


def bar(pct):
    filled = max(0, min(10, round(pct / 10)))
    return "█" * filled + "░" * (10 - filled)


def usage_cell(label, pct):
    if not isinstance(pct, (int, float)):
        return f"{label} no data"
    return f"{label} {bar(pct)} {(f'{pct:.0f}%').ljust(4)}"


def agent_state(worker, info, now, usage):
    """Return (online, detail) using only real files."""
    if info.get("interactive") and not info.get("queue"):  # the lead
        lead_hb = read_json(REPO_ROOT / "machines" / info["machine"] / "lead-heartbeat.json")
        times = [parse_time((usage or {}).get("updated_at")), parse_time((lead_hb or {}).get("time"))]
        times = [x for x in times if x]
        t = max(times) if times else None
        if t and (now - t).total_seconds() < ONLINE_MINUTES * 60:
            return True, "← command"
        return False, ("last seen " + ago(t, now)) if t else "never seen (no status-line data yet)"
    hb = read_json(REPO_ROOT / "machines" / info["machine"] / "heartbeat.json")
    t = parse_time((hb or {}).get("time"))
    if not hb or t is None:
        return False, "never seen"
    fresh = (now - t).total_seconds() < ONLINE_MINUTES * 60
    state = hb.get("status")
    if fresh and state != "stopped":
        if worker in (hb.get("paused_by_safety_check") or {}):
            return True, "PAUSED: safety check, owner must look"
        if hb.get("current_task"):
            return True, f"working {hb['current_task']}"
        if state == "rate_limited":
            return True, "rate-limited"
        return True, "standing by" if worker == "claude-second" else "idle"
    if state == "stopped":
        return False, f"listener stopped {ago(t, now)}"
    return False, "last seen " + ago(t, now)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-lead", action="store_true", help="record that claude-lead is running right now (only the lead should use this)")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    reg = read_json(REPO_ROOT / "machines" / "registry.json", {})
    if args.as_lead:
        lead_machine = reg.get("workers", {}).get("claude-lead", {}).get("machine")
        if lead_machine:
            write_json(REPO_ROOT / "machines" / lead_machine / "lead-heartbeat.json",
                       {"worker": "claude-lead", "machine": lead_machine, "time": now_iso(), "status": "active", "pid": os.getppid()})
    usage = read_json(REPO_ROOT / "local" / "claude-usage.json")
    now = dt.datetime.now(dt.timezone.utc)
    heavy, light = "═" * WIDTH, "─" * WIDTH

    rows = []
    for worker, info in reg.get("workers", {}).items():
        if info.get("swarm") is False:
            continue
        online, detail = agent_state(worker, info, now, usage)
        rows.append((info["machine"], worker, info.get("display_model", "?"), online, detail))

    out = [heavy,
           "  iTANTRA CREATIVE SWARM · Team chmod 777",
           "  ▸ activating agent swarm...",
           heavy,
           f"  {'NODE':<{NODE_W}}{'AGENT':<{AGENT_W}}{'MODEL':<{MODEL_W}}STATUS"]
    for node, agent, model, online, detail in rows:
        status = ("● ONLINE  " if online else "○ OFFLINE ") + detail
        out.append(f"  {node:<{NODE_W}}{agent:<{AGENT_W}}{model:<{MODEL_W}}{status}")
    out.append(light)

    rl = (usage or {}).get("rate_limits") or {}
    five = (rl.get("five_hour") or {}).get("used_percentage")
    seven = (rl.get("seven_day") or {}).get("used_percentage")
    line = f"  Usage     {usage_cell('5h', five)}  {usage_cell('7d', seven)}".rstrip()
    ut = parse_time((usage or {}).get("updated_at"))
    if usage is None:
        line = "  Usage     no data yet (the status line writes it after the lead's first reply)"
    elif ut and (now - ut).total_seconds() >= ONLINE_MINUTES * 60:
        line += f"   (updated {ago(ut, now)})"
    out += [line, light]

    n_on = sum(1 for r in rows if r[3])
    total = len(rows)
    if n_on == total:
        tail = f"{n_on}/{total} agents online. Swarm active. Awaiting orders..."
    elif n_on == 0:
        tail = f"0/{total} agents online. Swarm offline."
    else:
        down = ", ".join(r[1] for r in rows if not r[3])
        tail = f"{n_on}/{total} agents online. Offline: {down}."
    out.append("  " + tail)
    print("\n".join(out))


if __name__ == "__main__":
    main()
