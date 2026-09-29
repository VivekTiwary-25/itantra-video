"""fix_ffmpeg_path.py - make ffmpeg/ffprobe usable by Codex workers on this machine.

Problem seen on yash-pc and utkarsh-pc: the owner's shell finds a proper ffmpeg, but a worker inside the Codex sandbox
does not (it either finds nothing or a stripped-down ffmpeg from another program such as KeyShot).
Fix that worked on yash-pc: copy the ffmpeg programs to a plain folder (default C:\\Tools\\ffmpeg\\bin) and put that folder
in "path_prepend" in machine.local.json. The listener reads path_prepend for every task, so no restart is needed.

What it does:
  1. Looks through every folder on the PATH (fresh-terminal PATH included) for ffmpeg.exe and ffprobe.exe.
  2. Tests each candidate FOR REAL (makes a tiny lavfi test pattern; probes a footage audio file). It picks the first that works.
  3. With --apply: copies that folder's .exe/.dll files to --dest and adds --dest to path_prepend. It never deletes or changes the original.
Without --apply it only shows the plan.

Usage: python tools/fix_ffmpeg_path.py [--apply] [--dest C:\\Tools\\ffmpeg\\bin]
Output shows local folders on your screen only. Do not paste it into the (public) repo.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, load_machine_config, worker_path  # noqa: E402


def works(ffmpeg: Path, ffprobe: Path, sample_audio: Path | None) -> tuple[bool, str]:
    try:
        r = subprocess.run([str(ffmpeg), "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=64x64:rate=1",
                            "-t", "1", "-f", "null", "-"], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            return False, "cannot make a lavfi test pattern"
        if sample_audio:
            p = subprocess.run([str(ffprobe), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(sample_audio)],
                               capture_output=True, text=True, timeout=60)
            if p.returncode != 0 or not p.stdout.strip():
                return False, "ffprobe cannot read the sample audio file"
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)
    return True, "ok"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="really copy and edit machine.local.json (default: only show the plan)")
    ap.add_argument("--dest", default=os.path.join("C:" + os.sep, "Tools", "ffmpeg", "bin"))
    args = ap.parse_args()

    cfg = load_machine_config()
    audio_dir = Path(cfg["footage_root"]) / "Audio"
    sample = next(iter(sorted(audio_dir.glob("*.mp3"))), None) if audio_dir.is_dir() else None
    dirs = [d for d in worker_path(cfg, os.environ.get("PATH", "")).split(os.pathsep) if d]
    chosen = None
    print("Looking for a working ffmpeg + ffprobe pair ...")
    for d in dirs:
        ff, fp = Path(d) / "ffmpeg.exe", Path(d) / "ffprobe.exe"
        if ff.is_file() and fp.is_file():
            ok, why = works(ff, fp, sample)
            print(f"  candidate: {d}  ->  {'WORKS' if ok else 'rejected: ' + why}")
            if ok and chosen is None:
                chosen = Path(d)
    if not chosen:
        sys.exit("No working ffmpeg/ffprobe pair found on this PC. Install one (winget install --id Gyan.FFmpeg -e) and run this again.")

    dest = Path(args.dest)
    print(f"\nPlan: copy the programs from  {chosen}\n      to                       {dest}\n      and add that folder to path_prepend in machine.local.json.")
    if not args.apply:
        print("(dry run: nothing changed. Run again with --apply to do it.)")
        return
    dest.mkdir(parents=True, exist_ok=True)
    for f in chosen.iterdir():
        if f.is_file() and f.suffix.lower() in (".exe", ".dll"):
            shutil.copy2(f, dest / f.name)
    ok, why = works(dest / "ffmpeg.exe", dest / "ffprobe.exe", sample)
    print(f"Copied. Test of the copy: {'OK' if ok else 'FAILED: ' + why}")
    if not ok:
        sys.exit(1)
    cfg_path = REPO_ROOT / "machine.local.json"
    data = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
    pp = data.setdefault("path_prepend", [])
    if str(dest) not in pp:
        pp.insert(0, str(dest))
    cfg_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("machine.local.json updated (path_prepend). The listener reads it for every task, no restart needed.")
    print("Check it as a worker sees it with:  python tools/sandbox_check.py")


if __name__ == "__main__":
    main()
