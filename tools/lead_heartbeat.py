"""Automatic heartbeat for claude-lead (vivek-pc only).

The banner (tools/swarm_status.py) shows the lead ONLINE while
machines/<lead machine>/lead-heartbeat.json is under 10 minutes old. The lead is an
interactive session with no listener, so without this it drops to OFFLINE whenever it
sits waiting for Vivek. This loop pushes that file every 4 minutes straight to origin
(common.push_files_direct): it never touches the lead's HEAD, index or working tree.

It is tied to one Claude Code process and exits as soon as that process is gone, so a
closed lead session can never keep showing ONLINE. Only one copy runs at a time.

Usage (from the repo root, inside the lead's Claude Code session):
    python tools/lead_heartbeat.py --start        # find this session's claude.exe, launch hidden in the background
    python tools/lead_heartbeat.py --status       # is it running, and for which session?
    python tools/lead_heartbeat.py --stop
    python tools/lead_heartbeat.py --watch-pid N  # run in the foreground (what --start launches)
Log: local/logs/lead-heartbeat.log
"""
from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import push_files_direct  # noqa: E402

EVERY_S = 240
PUSH_TRIES = 5
PIDFILE = REPO_ROOT / "local" / "lead-heartbeat.pid"
LOGFILE = REPO_ROOT / "local" / "logs" / "lead-heartbeat.log"
# Under pythonw (no console) every git child would otherwise open its own terminal window.
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def log(msg: str) -> None:
    LOGFILE.parent.mkdir(parents=True, exist_ok=True)
    with LOGFILE.open("a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}\n")


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def pid_alive(pid: int) -> bool:
    """Windows-safe liveness check (os.kill(pid, 0) would terminate the process on Windows)."""
    if pid <= 0:
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    k32 = ctypes.windll.kernel32
    h = k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return False
    code = ctypes.c_ulong()
    ok = k32.GetExitCodeProcess(h, ctypes.byref(code))
    k32.CloseHandle(h)
    return bool(ok) and code.value == 259  # STILL_ACTIVE


def find_claude_ancestor() -> int | None:
    """Walk up from this process to the nearest claude.exe (Windows, via CIM)."""
    ps = (
        "$p = Get-CimInstance Win32_Process -Filter \"ProcessId=%d\"; "
        "while ($p) { if ($p.Name -like 'claude*') { $p.ProcessId; break }; "
        "if ($p.ParentProcessId -eq 0) { break }; "
        "$p = Get-CimInstance Win32_Process -Filter \"ProcessId=$($p.ParentProcessId)\" }" % os.getpid()
    )
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True).stdout.strip()
    return int(out) if out.isdigit() else None


def git(*args: str) -> tuple[int, str]:
    r = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, creationflags=NO_WINDOW)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def lead_machine() -> str:
    reg = json.loads((REPO_ROOT / "machines" / "registry.json").read_text(encoding="utf-8"))
    return reg["workers"]["claude-lead"]["machine"]


def beat(machine: str, watch_pid: int) -> None:
    """Push the lead heartbeat straight to origin without touching HEAD, the index or the working tree.
    The old version committed in the lead's working tree and pulled with --autostash; on 30 Sep that
    stashed the render helper's uncommitted film v2 fixes and never restored them."""
    rel = f"machines/{machine}/lead-heartbeat.json"
    hb = {"worker": "claude-lead", "machine": machine, "time": now_iso(), "status": "active",
          "pid": watch_pid, "source": "lead_heartbeat.py"}
    if not push_files_direct({rel: (json.dumps(hb, indent=2) + "\n").encode("utf-8")}, f"heartbeat {machine} lead",
                             tries=PUSH_TRIES):
        log("push gave up; next round tries again")


def read_pidfile() -> tuple[int, int] | None:
    try:
        me, watched = PIDFILE.read_text().split()
        return int(me), int(watched)
    except Exception:
        return None


def run(watch_pid: int) -> None:
    cur = read_pidfile()
    if cur and cur[0] != os.getpid() and pid_alive(cur[0]):
        print(f"already running (pid {cur[0]}, watching {cur[1]})")
        return
    PIDFILE.parent.mkdir(parents=True, exist_ok=True)
    PIDFILE.write_text(f"{os.getpid()} {watch_pid}")
    machine = lead_machine()
    log(f"start: pid {os.getpid()}, watching Claude Code pid {watch_pid}, every {EVERY_S}s")
    try:
        while pid_alive(watch_pid):
            try:
                beat(machine, watch_pid)
            except Exception as e:  # never die on one bad round
                log(f"beat error: {e!r}")
            for _ in range(EVERY_S):
                if not pid_alive(watch_pid):
                    break
                time.sleep(1)
        log(f"Claude Code pid {watch_pid} is gone; stopping")
    finally:
        cur = read_pidfile()
        if cur and cur[0] == os.getpid():
            PIDFILE.unlink(missing_ok=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--start", action="store_true")
    g.add_argument("--status", action="store_true")
    g.add_argument("--stop", action="store_true")
    g.add_argument("--watch-pid", type=int)
    a = ap.parse_args()
    cur = read_pidfile()
    running = bool(cur and pid_alive(cur[0]))
    if a.status:
        print(f"running: pid {cur[0]}, watching Claude Code pid {cur[1]}" if running else "not running")
    elif a.stop:
        if running:
            subprocess.run(["taskkill", "/PID", str(cur[0]), "/F"], capture_output=True)
            PIDFILE.unlink(missing_ok=True)
            log("stopped by --stop")
        print("stopped" if running else "not running")
    elif a.start:
        if running:
            print(f"already running: pid {cur[0]}, watching {cur[1]}")
            return
        cpid = find_claude_ancestor()
        if not cpid:
            sys.exit("could not find the Claude Code process above this shell; use --watch-pid N")
        exe = Path(sys.executable)
        pyw = exe.with_name("pythonw.exe")
        flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        subprocess.Popen([str(pyw if pyw.exists() else exe), str(Path(__file__).resolve()), "--watch-pid", str(cpid)],
                         cwd=REPO_ROOT, creationflags=flags, close_fds=True,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        cur = read_pidfile()
        print(f"started: pid {cur[0]}, watching Claude Code pid {cpid}" if cur else "launched; check --status")
    else:
        run(a.watch_pid)


if __name__ == "__main__":
    main()
