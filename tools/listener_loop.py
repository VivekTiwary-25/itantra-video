"""listener_loop.py - windowless listener loop for a friend's Windows laptop.

Run by the scheduled task `itantra-listener` with pythonw.exe (see `python tools/swarm.py install-task`).
The task is "run only when the user is logged on", so it starts in the user's desktop session. Codex needs that:
started over SSH/WMI the listener lands in session 0, and Codex fails there with "timed out ... connecting runner pipe-in".

Same restart behaviour as the .cmd files: exit code 75 (new tool code after a git pull) restarts at once,
any other exit restarts after 10 s, and it stops for good when local/listener.stop exists (`swarm stop`).
Console output of the listener goes to local/logs/listener-console.log. Nothing opens a window.
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STOP_FLAG = REPO_ROOT / "local" / "listener.stop"
CONSOLE_LOG = REPO_ROOT / "local" / "logs" / "listener-console.log"
RESTART_CODE = 75
PAUSE_S = 10
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def single_instance() -> object | None:
    """A named mutex per clone, so a second trigger of the task cannot start a second loop."""
    if os.name != "nt":
        return object()
    name = "Local\\itantra-listener-" + hashlib.sha1(str(REPO_ROOT).lower().encode()).hexdigest()[:16]
    handle = ctypes.windll.kernel32.CreateMutexW(None, False, name)
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        return None
    return handle


def listener_python() -> str:
    exe = Path(sys.executable)
    pyw = exe.with_name("pythonw.exe")
    return str(pyw if pyw.exists() else exe)


def main() -> int:
    if single_instance() is None:
        return 0
    CONSOLE_LOG.parent.mkdir(parents=True, exist_ok=True)
    py = listener_python()
    while not STOP_FLAG.exists():
        with open(CONSOLE_LOG, "ab") as out:
            code = subprocess.run([py, str(REPO_ROOT / "tools" / "listener.py")], cwd=str(REPO_ROOT), stdin=subprocess.DEVNULL,
                                  stdout=out, stderr=subprocess.STDOUT, creationflags=NO_WINDOW).returncode
        if STOP_FLAG.exists():
            break
        if code != RESTART_CODE:
            time.sleep(PAUSE_S)
    return 0


if __name__ == "__main__":
    sys.exit(main())
