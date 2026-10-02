"""Shared helpers for the video production tools. Python 3.11+, stdlib only, Windows-friendly."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MEDIA_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm",
             ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus"}
SAFE_TOKEN = re.compile(r"^[A-Za-z0-9._:\-]+$")


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return default


def write_json(path: Path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def load_machine_config() -> dict:
    """Read machine.local.json (git-ignored). Exits with a clear message if it is missing or wrong."""
    cfg_path = REPO_ROOT / "machine.local.json"
    cfg = read_json(cfg_path)
    if not cfg:
        sys.exit(f"machine.local.json is missing or unreadable at {cfg_path}. Create it first (see PROTOCOL.md section 1).")
    for key in ("machine", "workers", "footage_root", "renders_dir"):
        if key not in cfg:
            sys.exit(f"machine.local.json is missing the '{key}' field.")
    registry = read_json(REPO_ROOT / "machines" / "registry.json", {})
    if cfg["machine"] not in registry.get("machines", {}):
        sys.exit(f"Machine name '{cfg['machine']}' is not in machines/registry.json. Names must match exactly.")
    return cfg


NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)  # the listener runs without a console (pythonw): every child would otherwise open a window


def which(name: str) -> str | None:
    """shutil.which finds .cmd/.exe shims on Windows via PATHEXT."""
    return shutil.which(name)


def run(cmd: list[str], timeout: int = 30, cwd: Path | None = None) -> tuple[int, str]:
    """Run a command, return (exit code, combined output). Never raises."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, cwd=str(cwd) if cwd else None, creationflags=NO_WINDOW)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timed out"
    except OSError as e:
        return 127, str(e)


def git(*args: str, timeout: int = 120) -> tuple[int, str]:
    return run(["git", *args], timeout=timeout, cwd=REPO_ROOT)


def push_files_direct(files: dict[str, bytes | None], message: str, branch: str = "main", tries: int = 5,
                      net_timeout: int = 45) -> bool:
    """Commit these repo-relative files (None = delete) on top of origin/<branch> and push, WITHOUT touching
    HEAD, the index or the working tree. Used for heartbeats and supervisor commits, so they can never stash,
    rebase or overwrite anyone's uncommitted work (an autostash swallowed the film v2 fixes on 30 Sep).
    Returns True when the change is on GitHub (or there was nothing to change)."""
    import random
    import time
    idx = REPO_ROOT / "local" / "tmp" / f"direct-{os.getpid()}.index"
    idx.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, GIT_INDEX_FILE=str(idx))

    def g(*args, inp: bytes | None = None, timeout: int = 60):
        try:
            p = subprocess.run(["git", *args], cwd=REPO_ROOT, env=env, input=inp, capture_output=True,
                               timeout=timeout, creationflags=NO_WINDOW)
            return p.returncode, (p.stdout or b"").decode("utf-8", "replace").strip(), (p.stderr or b"").decode("utf-8", "replace").strip()
        except subprocess.TimeoutExpired:
            return 124, "", "timed out"

    try:
        for attempt in range(1, tries + 1):
            rc, _, err = g("fetch", "-q", "origin", branch, timeout=net_timeout)
            if rc == 0:
                base = g("rev-parse", "FETCH_HEAD")[1]
                g("read-tree", base)
                for rel, data in files.items():
                    if data is None:
                        g("update-index", "--force-remove", "--", rel)
                    else:
                        blob = g("hash-object", "-w", "--stdin", inp=data)[1]
                        g("update-index", "--add", "--cacheinfo", f"100644,{blob},{rel}")
                tree = g("write-tree")[1]
                if tree == g("rev-parse", f"{base}^{{tree}}")[1]:
                    return True
                commit = g("commit-tree", tree, "-p", base, "-m", message)[1]
                rc, _, err = g("push", "-q", "origin", f"{commit}:refs/heads/{branch}", timeout=net_timeout)
                if rc == 0:
                    g("update-ref", f"refs/remotes/origin/{branch}", commit)
                    return True
            if attempt < tries:
                time.sleep(random.uniform(2, 8))
        return False
    finally:
        idx.unlink(missing_ok=True)


def fresh_windows_path() -> list[str]:
    """PATH as Windows gives a NEW terminal: machine + user values read from the registry.
    A listener started from an old terminal has a stale PATH and misses tools installed since
    (ffmpeg on yash-pc and utkarsh-pc, installed during bootstrap)."""
    if os.name != "nt":
        return []
    try:
        import winreg
    except ImportError:
        return []
    keys = ((winreg.HKEY_LOCAL_MACHINE, chr(92).join(["SYSTEM", "CurrentControlSet", "Control", "Session Manager", "Environment"])),
            (winreg.HKEY_CURRENT_USER, "Environment"))
    out: list[str] = []
    for hive, sub in keys:
        try:
            with winreg.OpenKey(hive, sub) as k:
                value, _ = winreg.QueryValueEx(k, "Path")
        except OSError:
            continue
        out += [os.path.expandvars(x.strip()) for x in str(value).split(";") if x.strip()]
    return out


def worker_path(cfg: dict, current: str) -> str:
    """PATH for a worker: owner's path_prepend, then a fresh-terminal PATH, this Python's folder, then the inherited PATH."""
    parts = list(cfg.get("path_prepend", [])) + fresh_windows_path() + [str(Path(sys.executable).parent)] + current.split(os.pathsep)
    seen, out = set(), []
    for x in parts:
        x = x.strip()
        key = x.rstrip(chr(92) + "/").lower()
        if x and key not in seen:
            seen.add(key)
            out.append(x)
    return os.pathsep.join(out)


# ---------------------------------------------------------------- sync state (what this PC can and cannot do with GitHub)
SYNC_FILE = REPO_ROOT / "local" / "sync-state.json"


def update_sync_state(**fields) -> None:
    st = read_json(SYNC_FILE, {}) or {}
    st.update(fields)
    try:
        write_json(SYNC_FILE, st)
    except OSError:
        pass


def _t(s):
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def sync_warnings(now=None, pull_stale_min: int = 3, push_stale_min: int = 10) -> tuple[bool, list[str]]:
    """What this PC's own listener knows about its connection to GitHub, from local/sync-state.json.
    Returns (pull_is_stale, warning lines). pull_is_stale means: this PC's copy of the heartbeats is out of date, so
    'OFFLINE' for other machines cannot be trusted (show UNKNOWN). Nothing is reported if the file does not exist yet."""
    st = read_json(SYNC_FILE)
    if not st:
        return False, []
    now = now or dt.datetime.now(dt.timezone.utc)
    msgs: list[str] = []
    seen = _t(st.get("listener_seen"))
    listener_alive = bool(seen and (now - seen).total_seconds() < 15 * 60)
    if not listener_alive:
        return False, ["⚠ The listener on this PC is not running, so this view is not being refreshed."]
    busy = st.get("listener_status") == "busy"  # during a long task the listener deliberately does not pull
    pull = _t(st.get("last_pull_ok"))
    pull_stale = bool(pull and not busy and (now - pull).total_seconds() > pull_stale_min * 60)
    if pull_stale:
        msgs.append(f"⚠ This PC has not synced with GitHub for {(now - pull).total_seconds() / 60:.0f} min. "
                    "Machines shown as UNKNOWN may actually be online.")
    push = _t(st.get("last_push_ok"))
    waiting = st.get("unpushed") or 0
    if waiting and (not push or (now - push).total_seconds() > push_stale_min * 60):
        ago = f"{(now - push).total_seconds() / 60:.0f} min ago" if push else "never today"
        msgs.append(f"⚠ This PC cannot push to GitHub ({waiting} commit(s) waiting, last push OK {ago}). "
                    "Other machines see this PC as OFFLINE.")
    return pull_stale, msgs
