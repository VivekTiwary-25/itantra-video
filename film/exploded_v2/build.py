"""Stage local assets for the exploded view v2 (F0031). Nothing staged here is committed.

    python film/exploded_v2/build.py [--placeholders]

- Layers: RENDERS:exploded_v2/layer_screen.png, layer_mid.png, layer_back.png -> assets/
  (--placeholders first runs make_placeholders.py, which never overwrites real layers).
- Part map: results/F0030/parts.json if it exists, else RENDERS:exploded_v2/parts_placeholder.json.
  Accepted shapes: {"parts": {name: {...}}} or {name: {...}}; per part any of
  "center"/"centre": [x, y], "bbox"/"box": [x, y, w, h] or [x0, y0, x1, y1], or "x","y","w","h" / "cx","cy".
  Coordinates are pixels in layer_mid.png.
- Writes assets/data.js (window.EXPLODED = timeline + normalised parts + layer size), copies the glass kit and GSAP.
"""
import json
import shutil
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RENDERS = Path(json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))["renders_dir"])
SRC = RENDERS / "exploded_v2"
ASSETS = HERE / "assets"
NEEDED = ("microphone", "processor", "bluetooth_chip", "antenna", "loudspeaker")


def png_size(path: Path):
    with path.open("rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path.name} is not a PNG")
    return struct.unpack(">II", head[16:24])


def normalise(raw: dict, size):
    parts = raw.get("parts", raw)
    out = {}
    for name, p in parts.items():
        if not isinstance(p, dict):
            continue
        c = p.get("center") or p.get("centre")
        if c is None and "cx" in p:
            c = [p["cx"], p["cy"]]
        b = p.get("bbox") or p.get("box")
        if b is None and all(k in p for k in ("x", "y", "w", "h")):
            b = [p["x"], p["y"], p["w"], p["h"]]
        if b is not None:
            x, y, a, d = map(float, b)
            xyxy = a > x and d > y and (c is None or abs((x + a) / 2 - c[0]) < abs(x + a / 2 - c[0]))
            w, h = (a - x, d - y) if xyxy else (a, d)
            if c is None:
                c = [x + w / 2, y + h / 2]
        else:
            w = h = 0.04 * size[0]
        if c is None:
            raise ValueError(f"part {name}: no centre or box")
        out[name] = {"cx": float(c[0]), "cy": float(c[1]), "w": float(w), "h": float(h)}
    missing = [n for n in NEEDED if n not in out]
    if missing:
        raise ValueError(f"parts.json is missing {missing}")
    return out


def main():
    if "--placeholders" in sys.argv:
        subprocess.run([sys.executable, str(HERE / "make_placeholders.py")], check=True)
    (ASSETS / "glass").mkdir(parents=True, exist_ok=True)
    for name in ("glass.css", "glass.js", "noise.png"):
        shutil.copyfile(REPO / "film/common/glass" / name, ASSETS / "glass" / name)
    shutil.copyfile(REPO / "film/vendor/gsap/gsap.min.js", HERE / "gsap.min.js")
    for name in ("layer_screen.png", "layer_mid.png", "layer_back.png"):
        src = SRC / name
        if not src.is_file():
            sys.exit(f"missing RENDERS:exploded_v2/{name} (run with --placeholders to stage placeholders)")
        shutil.copyfile(src, ASSETS / name)
    real = REPO / "results/F0030/parts.json"
    parts_src = real if real.is_file() else SRC / "parts_placeholder.json"
    if not parts_src.is_file():
        sys.exit("no parts.json (results/F0030/parts.json or RENDERS:exploded_v2/parts_placeholder.json)")
    size = png_size(ASSETS / "layer_mid.png")
    sizes = {n: png_size(ASSETS / n) for n in ("layer_screen.png", "layer_back.png")}
    if any(s != size for s in sizes.values()):
        print(f"WARNING: layer sizes differ {sizes} vs mid {size}; layers are drawn at the same square box")
    raw = json.loads(parts_src.read_text(encoding="utf-8"))
    data = {"timeline": json.loads((HERE / "timeline.json").read_text(encoding="utf-8")),
            "size": list(size), "parts": normalise(raw, size),
            "placeholder": parts_src != real}
    (ASSETS / "data.js").write_text("window.EXPLODED = " + json.dumps(data) + ";\n", encoding="utf-8")
    print(f"staged layers ({size[0]}x{size[1]}) and parts from "
          f"{'results/F0030/parts.json' if parts_src == real else 'PLACEHOLDER parts'}")


if __name__ == "__main__":
    main()
