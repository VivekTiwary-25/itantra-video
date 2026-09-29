"""sandbox_check.py - show what a Codex worker really sees on this machine (PATH, ffmpeg, footage access).

Why: the doctor runs in your normal shell, but workers run inside Codex's sandbox with a different user and PATH.
On yash-pc ffmpeg was fine for the doctor but invisible to the worker, so a task failed. This runs one tiny
Codex task (gpt-6-luna, low effort) with the same sandbox settings the listener uses and prints what it reports.
Output goes to the screen only (it can contain your folder names): do not paste it into the repo.

Usage: python tools/sandbox_check.py
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, load_machine_config, which  # noqa: E402

PROMPT = """This is a diagnostic, not a film task. Ignore any AGENTS.md. Run these PowerShell commands and print each result exactly as it appears, then one final line 'DONE'. Do not fix anything.
1) where.exe ffmpeg
2) where.exe ffprobe
3) ffmpeg -hide_banner -version | Select-Object -First 1
4) $a = Get-ChildItem -LiteralPath (Join-Path $env:FOOTAGE_ROOT 'Audio') -File | Select-Object -First 1; ffprobe -v error -show_entries format=duration -of csv=p=0 $a.FullName
5) ffmpeg -hide_banner -loglevel error -f lavfi -i testsrc=size=64x64:rate=1 -t 1 -f null -   (print OK if it succeeds, or the exact error)
6) $env:PATH -split ';' | Select-Object -First 25
"""


def main() -> None:
    cfg = load_machine_config()
    codex = which("codex")
    if not codex:
        sys.exit("codex not found on PATH.")
    tmp_root = REPO_ROOT / "local" / "tmp"  # the normal Windows temp folder is blocked inside workspace-write
    tmp_root.mkdir(parents=True, exist_ok=True)
    work = tempfile.mkdtemp(prefix="sandbox-check-", dir=str(tmp_root))
    out = os.path.join(work, "last.md")
    env = dict(os.environ, FOOTAGE_ROOT=cfg["footage_root"], RENDERS_DIR=cfg["renders_dir"], MACHINE=cfg["machine"])
    env.update(TEMP=str(tmp_root), TMP=str(tmp_root), TMPDIR=str(tmp_root))
    if cfg.get("path_prepend"):
        env["PATH"] = os.pathsep.join(cfg["path_prepend"]) + os.pathsep + env.get("PATH", "")
    cmd = [codex, "exec", "-m", "gpt-6-luna", "-c", 'model_reasoning_effort="low"', "--sandbox", cfg.get("codex_sandbox", "workspace-write"),
           "--cd", work, "--skip-git-repo-check", "--ephemeral", "-o", out, "-"]
    print(f"Running a tiny Codex diagnostic with sandbox '{cfg.get('codex_sandbox', 'workspace-write')}' ...")
    p = subprocess.run(cmd, input=PROMPT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=300)
    print(f"codex exit code: {p.returncode}")
    try:
        print(Path(out).read_text(encoding="utf-8", errors="replace"))
    except OSError:
        print("(no answer file) stderr tail:", (p.stderr or "")[-800:])
    print("Read it like this: steps 1-2 must show ONE proper ffmpeg/ffprobe, step 4 a number, step 5 OK (or no output at all, which also means success).")
    print("If ffmpeg/ffprobe are missing or point at a different program (e.g. KeyShot), install ffmpeg somewhere the sandbox can read")
    print("(for example C:\\Tools\\ffmpeg\\bin, not inside your user folder) and add that folder to \"path_prepend\": [\"C:\\\\Tools\\\\ffmpeg\\\\bin\"] in machine.local.json.")


if __name__ == "__main__":
    main()
