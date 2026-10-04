"""Prepare the cards_v3 composition: copy GSAP and the glass kit (fallback if the kit is absent).

    python film/cards_v3/build.py            # copy assets only
    python film/cards_v3/build.py --render   # copy, then render RENDERS:cards_v3/cards_v3.mp4 (render machines only)
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
GLASS_SRC = REPO / "film/common/glass"
GLASS = HERE / "assets/glass"
GLASS.mkdir(parents=True, exist_ok=True)

shutil.copyfile(REPO / "film/vendor/gsap/gsap.min.js", HERE / "gsap.min.js")

# Minimal stand-in with the same class names and tokens, used only if the shared kit is missing.
FALLBACK_CSS = """
:root { --glass-tint: rgba(14,18,26,.48); --glass-blur: 28px; --glass-border: rgba(255,255,255,.18);
  --glass-shadow: 0 24px 60px rgba(0,0,0,.35); --text: #f3f5f8; --text-dim: rgba(243,245,248,.7);
  --blue: #4da3ff; --red: #ff4d5e; --gold: #f5c451; }
.glass-card { box-sizing: border-box; position: relative; color: var(--text);
  font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif; border-radius: 28px; padding: 56px 64px;
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,0) 27%), var(--glass-tint);
  border: 1px solid var(--glass-border); box-shadow: var(--glass-shadow), inset 0 1px 0 rgba(255,255,255,.08);
  backdrop-filter: blur(var(--glass-blur)) saturate(1.4); }
"""

if (GLASS_SRC / "glass.css").exists():
    for name in ("glass.css", "glass.js", "noise.png"):
        if (GLASS_SRC / name).exists():
            shutil.copyfile(GLASS_SRC / name, GLASS / name)
    print("Glass kit copied from film/common/glass/.")
else:
    (GLASS / "glass.css").write_text(FALLBACK_CSS, encoding="utf-8")
    print("Glass kit not found; wrote the minimal fallback glass.css.")

if "--render" in sys.argv:
    cfg = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
    out = Path(cfg["renders_dir"]) / "cards_v3" / "cards_v3.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    exe = "hyperframes.cmd" if sys.platform == "win32" else "hyperframes"
    sys.exit(subprocess.call([exe, "render", str(HERE), "-o", str(out), "--fps", "30"]))
