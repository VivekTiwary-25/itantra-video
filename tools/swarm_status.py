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
from common import REPO_ROOT, now_iso, read_json, sync_warnings, write_json  # noqa: E402

ONLINE_MINUTES = 10
UNPUSHED_WARN_MINUTES = 10
WIDTH = 60
NODE_W, AGENT_W, MODEL_W = 18, 15, 16


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


def push_warning(info, now):
    """Return a visible warning when a machine has been unable to publish commits for ten minutes."""
    hb = read_json(REPO_ROOT / "machines" / info["machine"] / "heartbeat.json") or {}
    try:
        count = int(hb.get("unpushed_commits") or 0)
    except (TypeError, ValueError):
        count = 0
    last_ok = parse_time(hb.get("last_push_ok"))
    overdue = count > 0 and (last_ok is None or (now - last_ok).total_seconds() > UNPUSHED_WARN_MINUTES * 60)
    return f"⚠ {count} unpushed commit(s)" if overdue else ""


def overdue_tasks(now):
    """Return tasks claimed by a listener but still missing a report past their declared deadline."""
    overdue = []
    for started in sorted((REPO_ROOT / "results").glob("*/STARTED.json")):
        if (started.parent / "REPORT.md").exists():
            continue
        info = read_json(started, {}) or {}
        began = parse_time(info.get("time"))
        try:
            timeout_min = int(info.get("timeout_min") or 60)
        except (TypeError, ValueError):
            timeout_min = 60
        if began and (now - began).total_seconds() > timeout_min * 60:
            late_min = (now - began).total_seconds() / 60 - timeout_min
            overdue.append(f"⚠ OVERDUE {started.parent.name} ({info.get('worker', '?')}@{info.get('machine', '?')}, {late_min:.0f}m past {timeout_min}m timeout)")
    return overdue


LANES = ("video", "ppt", "misc")


def task_lane(path):
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:1500]
    except OSError:
        return None
    for line in head.splitlines()[1:]:
        if line.strip() == "---":
            break
        if line.lower().startswith("lane:"):
            return line.split(":", 1)[1].strip().lower()
    return None


def lane_counts():
    """Tasks with a lane: line, wherever they are queued (own queue or queue/lane-<lane>/)."""
    counts = {}
    for f in (REPO_ROOT / "queue").glob("*/*.md"):
        lane = task_lane(f)
        if f.parent.name.startswith("lane-"):
            lane = f.parent.name[5:]
        if lane not in LANES:
            continue
        rdir = REPO_ROOT / "results" / f.stem
        verdict = (REPO_ROOT / "reviews" / f"{f.stem}.md")
        if verdict.exists() and "dropped" in verdict.read_text(encoding="utf-8", errors="replace")[:200]:
            continue
        rep = rdir / "REPORT.md"
        if rep.exists():
            text = rep.read_text(encoding="utf-8", errors="replace")[:600].lower()
            state = "done" if "status: done" in text else "failed"
        elif (rdir / "STARTED.json").exists():
            state = "running"
        else:
            state = "queued"
        counts.setdefault(lane, {}).setdefault(state, 0)
        counts[lane][state] += 1
    return counts


def supervisor_line(now):
    st = read_json(REPO_ROOT / "machines" / "supervisor" / "status.json")
    if not st:
        return "Supervisor  never seen"
    t = parse_time(st.get("time"))
    alive = t and (now - t).total_seconds() < 12 * 60
    return (f"Supervisor  {'● running' if alive else '○ NOT RUNNING'} (last report {ago(t, now)})"
            + (f"  · {st['summary']}" if st.get("summary") else ""))


def agent_state(worker, info, now, usage):
    """Return (online, detail) using only real files."""
    if info.get("interactive") and not info.get("queue"):  # the lead
        lead_hb = read_json(REPO_ROOT / "machines" / info["machine"] / "lead-heartbeat.json")
        seen = read_json(REPO_ROOT / "local" / "lead-seen.json")
        times = [parse_time((usage or {}).get("updated_at")), parse_time((lead_hb or {}).get("time")), parse_time((seen or {}).get("time"))]
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
    if args.as_lead:  # git-ignored: writing the tracked heartbeat here left the lead's working tree dirty
        write_json(REPO_ROOT / "local" / "lead-seen.json", {"worker": "claude-lead", "time": now_iso(), "pid": os.getppid()})
    usage = read_json(REPO_ROOT / "local" / "claude-usage.json")
    now = dt.datetime.now(dt.timezone.utc)
    sync_state = read_json(REPO_ROOT / "local" / "sync-state.json") or {}
    last_pull = parse_time(sync_state.get("last_pull_ok"))
    data_age = ago(last_pull, now) if last_pull else "unknown"
    heavy, light = "═" * WIDTH, "─" * WIDTH

    rows = []
    for worker, info in reg.get("workers", {}).items():
        if info.get("swarm") is False:
            continue
        online, detail = agent_state(worker, info, now, usage)
        warning = push_warning(info, now)
        if warning:
            detail = f"{detail}  {warning}"
        rows.append((info["machine"], worker, info.get("display_model", "?"), online, detail, info.get("home_lane")))

    pull_stale, sync_msgs = sync_warnings(now)
    out = [heavy,
           f"  data as of {data_age} since last successful git pull",
           "  iTANTRA CREATIVE SWARM · Team chmod 777",
           "  ▸ activating agent swarm...",
           heavy,
           f"  {'NODE':<{NODE_W}}{'AGENT':<{AGENT_W}}{'MODEL':<{MODEL_W}}STATUS"]

    def row(r):
        node, agent, model, online, detail, _ = r
        status = ("● ONLINE  " if online else ("? UNKNOWN " if pull_stale else "○ OFFLINE ")) + detail
        return f"  {node:<{NODE_W}}{agent:<{AGENT_W}}{model:<{MODEL_W}}{status}"

    out += [row(r) for r in rows if not r[5]]  # the lead
    counts = lane_counts()
    for lane in LANES:
        c = counts.get(lane, {})
        out.append(f"  ── {lane.upper()} lane · queued {c.get('queued', 0)} · running {c.get('running', 0)} · done {c.get('done', 0)} "
                   f"· failed {c.get('failed', 0)}")
        out += [row(r) for r in rows if r[5] == lane] or ["  (no home workers; idle workers from other lanes take these)"]
    out += ["  " + task for task in overdue_tasks(now)]
    out.append("  " + supervisor_line(now))
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
        tail = f"{n_on}/{total} agents online. " + (f"Unknown: {down}." if pull_stale else f"Offline: {down}.")
    out.append("  " + tail)
    out += ["  " + m for m in sync_msgs]
    print("\n".join(out))


if __name__ == "__main__":
    main()
