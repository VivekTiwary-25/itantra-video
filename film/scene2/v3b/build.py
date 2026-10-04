"""Build scene 2 v3b from machine.local.json. Run: python film/scene2/v3b/build.py [--preview|--render]."""
import subprocess
import sys
from pathlib import Path

if __name__ == '__main__':
    raise SystemExit(subprocess.call(['node', str(Path(__file__).with_name('build.js')), *sys.argv[1:]]))
