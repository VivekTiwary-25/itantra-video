"""Shared helpers for the video production tools. Python 3.11+, stdlib only, Windows-friendly."""
from __future__ import annotations

import datetime as dt
import json
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
        return json.loads(Path(path).read_text(encoding="utf-8"))
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


def which(name: str) -> str | None:
    """shutil.which finds .cmd/.exe shims on Windows via PATHEXT."""
    return shutil.which(name)


def run(cmd: list[str], timeout: int = 30, cwd: Path | None = None) -> tuple[int, str]:
    """Run a command, return (exit code, combined output). Never raises."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, cwd=str(cwd) if cwd else None)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timed out"
    except OSError as e:
        return 127, str(e)


def git(*args: str, timeout: int = 120) -> tuple[int, str]:
    return run(["git", *args], timeout=timeout, cwd=REPO_ROOT)
