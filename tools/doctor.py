"""doctor.py - report what this machine has, write machines/<machine>/capabilities.json.

Installs nothing. Prints install commands for the machine owner to approve.
Usage: python tools/doctor.py
"""
from __future__ import annotations

import ctypes
import os
import platform
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, load_machine_config, now_iso, run, which, write_json  # noqa: E402

TOOLS = {
    "git": ["git", "--version"],
    "python": [sys.executable, "--version"],
    "node": ["node", "--version"],
    "npm": ["npm", "--version"],
    "ffmpeg": ["ffmpeg", "-version"],
    "ffprobe": ["ffprobe", "-version"],
    "codex": ["codex", "--version"],
    "claude": ["claude", "--version"],
}

INSTALL_HINTS = {
    "git": "winget install --id Git.Git -e",
    "python": "winget install --id Python.Python.3.12 -e",
    "node": "winget install --id OpenJS.NodeJS.LTS -e   (HyperFrames needs Node 22+)",
    "npm": "comes with Node",
    "ffmpeg": "winget install --id Gyan.FFmpeg -e   (then open a new terminal)",
    "ffprobe": "comes with ffmpeg",
    "codex": "npm i -g @openai/codex",
    "claude": "see https://docs.claude.com/en/docs/claude-code (native installer)",
    "hyperframes": "npm i -g hyperframes   (or let npx fetch it on first use)",
    "browser": "install Google Chrome or Microsoft Edge (HyperFrames renders through one of them)",
}

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def ram_gb() -> float | None:
    if os.name != "nt":
        return None

    class MEMSTAT(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]

    m = MEMSTAT()
    m.dwLength = ctypes.sizeof(MEMSTAT)
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        return round(m.ullTotalPhys / 1024 ** 3, 1)
    return None


def free_gb(path: Path) -> float | None:
    p = Path(path)
    while not p.exists() and p != p.parent:
        p = p.parent
    try:
        return round(shutil.disk_usage(p).free / 1024 ** 3, 1)
    except OSError:
        return None


def main() -> None:
    cfg = load_machine_config()
    machine = cfg["machine"]
    caps: dict = {"machine": machine, "checked_at": now_iso(), "os": platform.platform(), "tools": {}}
    missing: list[str] = []

    for name, cmd in TOOLS.items():
        exe = which(cmd[0]) if cmd[0] != sys.executable else sys.executable
        if not exe:
            caps["tools"][name] = None
            missing.append(name)
            continue
        code, out = run([exe, *cmd[1:]], timeout=30)
        caps["tools"][name] = {"version": first_line(out) if code == 0 else f"error: {first_line(out)}"}  # no paths: they contain the Windows account name

    # HyperFrames: --no-install so this never downloads anything.
    npx = which("npx")
    hf = None
    if npx:
        code, out = run([npx, "--no-install", "hyperframes", "--version"], timeout=60)
        if code == 0 and out.strip():
            hf = {"version": first_line(out)}
    caps["tools"]["hyperframes"] = hf
    if not hf:
        missing.append("hyperframes")

    browsers = [b for b in BROWSERS if Path(b).exists()]
    caps["browsers"] = browsers
    if not browsers:
        missing.append("browser")

    # GPU
    gpu = None
    smi = which("nvidia-smi")
    if smi:
        code, out = run([smi, "--query-gpu=name,memory.total", "--format=csv,noheader"], timeout=20)
        if code == 0 and out.strip():
            gpu = [line.strip() for line in out.strip().splitlines()]
    caps["gpu"] = gpu

    caps["cpu_cores"] = os.cpu_count()
    caps["ram_gb"] = ram_gb()
    caps["free_disk_gb"] = {
        "repo_drive": free_gb(REPO_ROOT),
        "footage_drive": free_gb(Path(cfg["footage_root"])),
        "renders_drive": free_gb(Path(cfg["renders_dir"])),
    }
    caps["codex_sandbox"] = cfg.get("codex_sandbox", "workspace-write")
    caps["codex_add_dirs"] = cfg.get("codex_add_dirs", [])
    caps["missing"] = missing

    out_path = REPO_ROOT / "machines" / machine / "capabilities.json"
    write_json(out_path, caps)

    print(f"Machine: {machine}")
    for name, info in caps["tools"].items():
        print(f"  {name:<12} {info['version'] if info else 'MISSING'}")
    print(f"  browser      {', '.join(browsers) if browsers else 'MISSING'}")
    print(f"  GPU          {gpu if gpu else 'none found'}")
    print(f"  CPU cores    {caps['cpu_cores']}   RAM {caps['ram_gb']} GB")
    print(f"  free disk    {caps['free_disk_gb']}")
    print(f"Wrote {out_path}")
    if missing:
        print("\nMISSING (nothing was installed; ask the PC's owner before running these):")
        for m in missing:
            print(f"  {m}: {INSTALL_HINTS.get(m, '')}")


if __name__ == "__main__":
    main()
