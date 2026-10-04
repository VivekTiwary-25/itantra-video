"""Encode the transparent Blender PNG shots for HyperFrames seeking."""
import json
import math
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RENDERS = Path(json.loads((ROOT / "machine.local.json").read_text())["renders_dir"])
OUT = RENDERS / "scene4/blender"
beats = json.loads((HERE / "timeline.json").read_text())["beats"]
duration = json.loads((HERE / "timeline.json").read_text())["duration"]
shots = (("lift", .7, 1.4), ("spin", 1.4, beats["open"][0]),
         ("processor", beats["open"][0], beats["close"][0]),
         ("close", beats["close"][0], beats["pair"][0]),
         ("pair", beats["pair"][0], duration))

# The source teardown's opening is too sparse to read at phone size. Hold the
# last closed frame beneath the accepted image-layer opening in the composite.
hold = OUT / "spin" / f"{math.ceil(beats['open'][0] * 30) - 1:06d}.png"
processor_start = math.ceil(beats["open"][0] * 30)
processor_end = math.ceil(beats["close"][0] * 30)
if not hold.is_file():
    raise FileNotFoundError(f"missing spin hold: {hold}")
(OUT / "processor").mkdir(parents=True, exist_ok=True)
for frame in range(processor_start, processor_end):
    path = OUT / "processor" / f"{frame:06d}.png"
    if path.exists():
        path.unlink()
    os.link(hold, path)

cmd = ["ffmpeg", "-v", "error", "-y"]
for name, start, end in shots:
    first, last = math.ceil(start * 30), math.ceil(end * 30)
    if not all((OUT / name / f"{frame:06d}.png").is_file() for frame in range(first, last)):
        raise FileNotFoundError(f"incomplete Blender shot: {name}")
    cmd += ["-framerate", "30", "-start_number", str(first), "-i", str(OUT / name / "%06d.png")]
inputs = "".join(f"[{i}:v]" for i in range(len(shots)))
cmd += ["-filter_complex", f"{inputs}concat=n={len(shots)}:v=1:a=0,format=yuva420p[v]",
        "-map", "[v]", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
        "-auto-alt-ref", "0", "-b:v", "0", "-crf", "29", "-deadline", "good",
        "-cpu-used", "4", str(OUT / "phone.webm")]
subprocess.run(cmd, check=True)
print("RENDERS:scene4/blender/phone.webm")
