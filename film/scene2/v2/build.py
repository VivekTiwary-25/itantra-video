"""Scene 2 v2 build entry point. Requires Node.js, FFmpeg and HyperFrames.

Run: python film/scene2/v2/build.py [--prepare|--render|--preview]
On machines without Python: node film/scene2/v2/build.js [same flags].
"""
import subprocess
import sys
from pathlib import Path


if __name__ == "__main__":
    raise SystemExit(subprocess.call(["node", str(Path(__file__).with_name("build.js")), *sys.argv[1:]]))
