"""Idle watcher: tells the lead (and Vivek, via ntfy) when a worker sits idle while work is waiting.

Runs on vivek-pc against a dedicated read-only clone. Stdlib only (Python 3.12).

    python tools/idle_watcher.py --clone <watch clone> --out <status.md> [--active-flag <file>] [--loop] [--interval 120]
    python tools/idle_watcher.py --test-ping [done|failed|idle]

Readiness follows PROTOCOL.md section 4: a task is ready when it has no STARTED.json (and no REPORT.md),
is not dropped, and every depends_on has REPORT status done and review verdict accepted.
Running = STARTED.json without REPORT.md.
Also pings once per new results/<id>/REPORT.md (done/failed/refused from its front-matter status line).
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
SKIP_WORKERS = {"codex-yojitth"}  # out of the swarm
LANES = ("video", "ppt", "misc")
IDLE_ALERT_MIN = 10
STALE_ALERT_MIN = 15
REPING_MIN = 30
LOG_MAX = 1_000_000
NTFY_VARS = ("Ntfy Topic", "NTFY_TOPIC")
NTFY_VAR = NTFY_VARS[0]

LOG_PATH: Path | None = None


# ---------------------------------------------------------------- logging
def log(msg: str) -> None:
    line = f"{dt.datetime.now(IST):%Y-%m-%d %H:%M:%S} {msg}\n"
    if LOG_PATH is None:
        sys.stderr.write(line)
        return
    try:
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > LOG_MAX:
            os.replace(LOG_PATH, LOG_PATH.with_name(LOG_PATH.name + ".1"))
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        sys.stderr.write(line)


# ---------------------------------------------------------------- parsing
def parse_frontmatter(text: str) -> dict:
    text = text.lstrip("﻿")
    m = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*(\r?\n|$)", text, re.S)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            fm[k] = [x.strip().strip("\"'") for x in v[1:-1].split(",") if x.strip()]
        elif v.lower() in ("", "null", "~", "none"):
            fm[k] = None
        else:
            fm[k] = v.strip("\"'")
    return fm


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def read_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def parse_time(s) -> dt.datetime | None:
    if not s:
        return None
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def hhmm(t: dt.datetime | None) -> str:
    return t.astimezone(IST).strftime("%H:%M") if t else "?"


def id_sort_key(task_id: str):
    m = re.match(r"^([A-Za-z]*)(\d+)", task_id)
    return (m.group(1), int(m.group(2)), task_id) if m else ("~", 0, task_id)


# ---------------------------------------------------------------- repo state
class Repo:
    def __init__(self, root: Path):
        self.root = root

    def report_status(self, rid: str) -> str | None:
        p = self.root / "results" / rid / "REPORT.md"
        if not p.exists():
            return None
        text = read_text(p)
        st = parse_frontmatter(text).get("status")
        if st:
            return str(st).lower()
        m = re.search(r"status\s*:\s*(done|failed|refused)", text[:2000], re.I)
        return m.group(1).lower() if m else "unknown"

    def verdict(self, rid: str) -> str | None:
        p = self.root / "reviews" / f"{rid}.md"
        if not p.exists():
            return None
        text = read_text(p)
        v = parse_frontmatter(text).get("verdict")
        if v:
            return str(v).lower()
        m = re.search(r"verdict\s*:\s*(accepted|redo|dropped)", text, re.I)
        return m.group(1).lower() if m else None

    def started(self, rid: str) -> dict | None:
        p = self.root / "results" / rid / "STARTED.json"
        return (read_json(p) or {"time": None}) if p.exists() else None

    def deps_ok(self, deps) -> bool:
        return all(self.report_status(d) == "done" and self.verdict(d) == "accepted" for d in (deps or []))

    def tasks(self) -> list[dict]:
        """Every queued task file with its state."""
        out = []
        qroot = self.root / "queue"
        if not qroot.is_dir():
            return out
        for qdir in sorted(qroot.iterdir()):
            if not qdir.is_dir():
                continue
            pool = qdir.name.startswith("lane-")
            for f in qdir.glob("*.md"):
                fm = parse_frontmatter(read_text(f))
                rid = f.stem
                started = self.started(rid)
                report = self.report_status(rid)
                dropped = self.verdict(rid) == "dropped"
                t = {
                    "id": rid, "queue": qdir.name, "pool": pool, "fm": fm,
                    "title": fm.get("title") or "", "started": started, "report": report,
                }
                t["running"] = started is not None and report is None and not dropped
                t["ready"] = (started is None and report is None and not dropped
                              and self.deps_ok(fm.get("depends_on")))
                out.append(t)
        out.sort(key=lambda t: id_sort_key(t["id"]))
        return out


def pool_ok(task: dict, worker: str, winfo: dict) -> bool:
    """Same limits as listener.runnable() for lane tasks: cli, machine, worker."""
    fm = task["fm"]
    if fm.get("cli") not in (None, "any", winfo.get("cli")):
        return False
    if fm.get("machine") not in (None, "any", winfo.get("machine")):
        return False
    return fm.get("worker") in (None, "any", worker)


# ---------------------------------------------------------------- ntfy
def ntfy_topic() -> str | None:
    topic = next((os.environ[v] for v in NTFY_VARS if os.environ.get(v)), None)
    if not topic and sys.platform == "win32":
        import winreg
        for v in NTFY_VARS:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                    topic = winreg.QueryValueEx(k, v)[0]
                break
            except OSError:
                topic = None
    return (topic or "").strip() or None


NTFY_TAGS = {"done": "white_check_mark", "failed": "x", "refused": "x", "idle": "warning"}
NTFY_PS = ("$b = [Convert]::FromBase64String($env:NTFY_B); "
           "Invoke-RestMethod -Method Post -Uri ('https://ntfy.sh/' + $env:NTFY_T) "
           "-Headers @{Title = $env:NTFY_TITLE; Tags = $env:NTFY_TAGS} "
           "-Body $b -ContentType 'text/plain; charset=utf-8' | Out-Null")


def send_ntfy(message: str, kind: str = "idle", title: str = "iTantra") -> bool:
    """POST to ntfy.sh. Body is UTF-8 (base64 in the child's env, decoded to bytes there);
    headers are plain ASCII (Title, Tags as ntfy shortcodes). No topic/body on the command line."""
    topic = ntfy_topic()
    if not topic:
        log(f"ntfy: no '{NTFY_VAR}' variable set; not sent: {message}")
        return False
    title = title.encode("ascii", "ignore").decode("ascii").strip() or "iTantra"
    env = dict(os.environ, NTFY_T=topic, NTFY_TITLE=title, NTFY_TAGS=NTFY_TAGS.get(kind, "warning"),
               NTFY_B=base64.b64encode(message.encode("utf-8")).decode("ascii"))
    cmd = ["powershell", "-NoProfile", "-Command", NTFY_PS]
    try:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60, creationflags=flags)
    except (OSError, subprocess.TimeoutExpired) as e:
        log(f"ntfy: failed to run powershell: {e}")
        return False
    if r.returncode != 0:
        log(f"ntfy: powershell exit {r.returncode}: {(r.stderr or '').strip()[:300]}")
        return False
    log(f"ntfy: sent [{kind}]: {message}")
    return True


def report_kind(repo: "Repo", rid: str) -> str | None:
    """done/failed/refused from the REPORT.md front-matter status line only, else None."""
    st = parse_frontmatter(read_text(repo.root / "results" / rid / "REPORT.md")).get("status")
    st = str(st).strip().lower() if st else ""
    return st if st in ("done", "failed", "refused") else None


def notify_reports(args, repo: "Repo", tasks: list[dict], state: dict) -> None:
    """One ping per new results/<id>/REPORT.md. First run (no 'notified' list) just marks all as seen."""
    rdir = repo.root / "results"
    ids = sorted((d.name for d in rdir.iterdir() if (d / "REPORT.md").is_file()), key=id_sort_key) if rdir.is_dir() else []
    if "notified" not in state:
        state["notified"] = ids
        log(f"report notifications: marked {len(ids)} existing REPORTs as seen")
        return
    seen = set(state["notified"])
    titles = {t["id"]: t["title"] for t in tasks}
    for rid in ids:
        if rid in seen:
            continue
        kind = report_kind(repo, rid)
        if kind is None:
            continue  # front matter not readable yet; try again next pass
        title = " ".join(str(titles.get(rid) or "").split())[:60]
        msg = f"{rid} {kind}" + (f": {title}" if title else "")
        if args.no_ntfy:
            log(f"report (ntfy off): {msg}")
        elif not send_ntfy(msg, kind, f"iTantra {rid} {kind}"):
            continue  # retry next pass
        state["notified"].append(rid)
        seen.add(rid)


# ---------------------------------------------------------------- one pass
def git_pull(clone: Path) -> None:
    try:
        r = subprocess.run(["git", "-C", str(clone), "pull", "--ff-only", "-q"],
                           capture_output=True, text=True, timeout=120,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if r.returncode != 0:
            log(f"git pull failed (exit {r.returncode}), using old state: {(r.stderr or r.stdout).strip()[:300]}")
    except (OSError, subprocess.TimeoutExpired) as e:
        log(f"git pull failed, using old state: {e}")


def atomic_write(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def one_pass(args, state_path: Path) -> None:
    clone = Path(args.clone)
    if not args.no_pull:
        git_pull(clone)
    repo = Repo(clone)
    now = dt.datetime.now(dt.timezone.utc)
    registry = read_json(clone / "machines" / "registry.json")
    workers = {w: i for w, i in (registry.get("workers") or {}).items()
               if i.get("queue") is True and w not in SKIP_WORKERS}
    state = read_json(state_path)
    wstate = state.setdefault("workers", {})
    pings = state.setdefault("pings", {})  # alert key -> last ping time (ISO); key removed when the episode ends
    tasks = repo.tasks()
    ready = [t for t in tasks if t["ready"]]
    running = [t for t in tasks if t["running"]]
    active = bool(args.active_flag) and Path(args.active_flag).exists()

    rows, alerts, active_keys = [], [], set()
    for w, info in sorted(workers.items()):
        machine = info.get("machine") or "?"
        hb = read_json(clone / "machines" / machine / "heartbeat.json")
        hb_time = parse_time(hb.get("time"))
        status = str(hb.get("status") or "unknown")
        cur = hb.get("current_task") or ""
        prev = wstate.get(w) or {}
        if prev.get("status") != status:
            since = hb_time if not prev else now
            wstate[w] = {"status": status, "since": (since or now).isoformat()}
        since = parse_time(wstate[w]["since"])
        own_ready = [t for t in ready if not t["pool"] and t["queue"] == w]
        pool_ready = [t for t in ready if t["pool"] and pool_ok(t, w, info)]
        hb_age = (now - hb_time).total_seconds() / 60 if hb_time else None
        idle_min = (now - since).total_seconds() / 60 if since else 0
        rows.append((w, machine, status, hhmm(since), cur or "-", len(own_ready), len(pool_ready),
                     f"{hb_age:.0f} min" if hb_age is not None else "none"))

        could_take = len(own_ready) + len(pool_ready)
        if status == "idle" and idle_min > IDLE_ALERT_MIN and (active or could_take):
            key = f"idle:{w}"
            why = f"{could_take} tasks ready" if could_take else "film work open"
            alerts.append((key, f"{w} idle {idle_min:.0f} min, {why}"))
        if hb_age is None or hb_age > STALE_ALERT_MIN:
            key = f"stale:{machine}"
            age = f"{hb_age:.0f} min" if hb_age is not None else "missing"
            alerts.append((key, f"{machine} heartbeat stale {age}"))

    # dedupe (two workers on one machine share a stale alert)
    seen, uniq = set(), []
    for key, msg in alerts:
        if key not in seen:
            seen.add(key)
            uniq.append((key, msg))
    alerts = uniq

    for key, msg in alerts:
        active_keys.add(key)
        last = parse_time(pings.get(key))
        if last and (now - last).total_seconds() < REPING_MIN * 60:
            continue
        if args.no_ntfy:
            log(f"alert (ntfy off): {msg}")
            pings[key] = now.isoformat()
        elif send_ntfy(f"iTantra: {msg}", "idle", "iTantra watcher"):
            pings[key] = now.isoformat()
    for key in list(pings):
        if key not in active_keys:
            del pings[key]  # episode over: the next one pings again at once

    notify_reports(args, repo, tasks, state)

    lines = [f"# Worker status ({hhmm(now)} IST)", ""]
    if alerts:
        lines += ["## ALERTS", ""] + [f"- {m}" for _, m in alerts] + [""]
    else:
        lines += ["No alerts", ""]
    lines += [f"Film work open (active flag): {'yes' if active else 'no'}", "",
              "| worker | machine | busy/idle | since | current task | own ready | pool ready | heartbeat age |",
              "|---|---|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    lines += ["", "## Ready tasks", ""]
    if ready:
        lines += ["| id | worker/pool | title |", "|---|---|---|"]
        for t in ready:
            who = t["queue"] if not t["pool"] else f"pool {t['queue']}"
            lines.append(f"| {t['id']} | {who} | {t['title'].replace('|', '/')} |")
    else:
        lines.append("None")
    lines += ["", "## Running", ""]
    if running:
        lines += ["| id | worker | started |", "|---|---|---|"]
        for t in running:
            st = t["started"] or {}
            lines.append(f"| {t['id']} | {st.get('worker') or t['queue']} | {hhmm(parse_time(st.get('time')))} |")
    else:
        lines.append("None")
    atomic_write(Path(args.out), "\n".join(lines) + "\n")
    atomic_write(state_path, json.dumps(state, indent=2))


# ---------------------------------------------------------------- main
def main() -> int:
    global LOG_PATH
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--clone", help="dedicated read-only clone of the repo")
    ap.add_argument("--out", help="status markdown file to write")
    ap.add_argument("--active-flag", help="file whose existence means the film has unfinished work")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=int, default=120)
    ap.add_argument("--no-ntfy", action="store_true", help="log alerts instead of sending them")
    ap.add_argument("--no-pull", action="store_true", help="skip git pull (testing on a working clone)")
    ap.add_argument("--test-ping", nargs="?", const="done", choices=("done", "failed", "idle"),
                    help="send one clearly-marked test ping of that kind (default done) and exit")
    args = ap.parse_args()

    if args.test_ping:
        k = args.test_ping
        return 0 if send_ntfy(f"TEST ONLY: simulated {k} ping from iTantra watcher", k, f"iTantra test {k}") else 1
    if not args.clone or not args.out:
        ap.error("--clone and --out are required")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH = out.with_name(out.name + ".log")
    state_path = out.with_name(out.name + ".state.json")

    while True:
        try:
            one_pass(args, state_path)
        except Exception:  # never crash the loop
            log("pass failed:\n" + traceback.format_exc())
        if not args.loop:
            return 0
        try:
            time.sleep(max(10, args.interval))
        except KeyboardInterrupt:
            return 0


if __name__ == "__main__":
    sys.exit(main())
