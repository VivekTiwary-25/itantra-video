"""Scene 2 v3a build entry point. Requires Node.js, FFmpeg and HyperFrames.

Run: python film/scene2/v3a/build.py [--prepare|--render|--preview].
Set YASH_REPLY=true to retain Yash's reply; default is false.
Set S2A_RENDER_ROOT=local/renders for a workspace-local preview output.
"""
import subprocess
import sys
from pathlib import Path


if __name__ == "__main__":
    raise SystemExit(subprocess.call(["node", str(Path(__file__).with_name("build.js")), *sys.argv[1:]]))
