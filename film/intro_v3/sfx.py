"""Quiet deterministic glass ticks and one soft card whoosh."""
import json
import math
import struct
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
timings = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
config = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
out = Path(config["renders_dir"]) / "intro_v3/sfx.wav"
out.parent.mkdir(parents=True, exist_ok=True)
rate = 48000
samples = [0.0] * round(timings["end"] * rate)
ticks = [timings["panel"] + .38, timings["no"] + .04,
         timings["network"] + .02, timings["needed"] + .02,
         timings["needed"] + .20]
for start in ticks:
    pos = round(start * rate)
    for j in range(round(.22 * rate)):
        t = j / rate
        samples[pos + j] += .014 * min(1, t / .004) * math.exp(-t * 24) * (
            math.sin(2 * math.pi * 2450 * t) + .35 * math.sin(2 * math.pi * 3320 * t))
start = timings["lets"]
for j in range(round(1.2 * rate)):
    t = j / rate
    phase = j * (2 * math.pi / rate)
    # Two low sines with a slow envelope give motion without a trailer-like sweep.
    samples[round(start * rate) + j] += .008 * math.sin(math.pi * t / 1.2) ** 2 * (
        math.sin(85 * phase) + .3 * math.sin(133 * phase))
with wave.open(str(out), "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(rate)
    wav.writeframes(b"".join(struct.pack("<h", round(max(-1, min(1, x)) * 32767)) for x in samples))
print("RENDERS:intro_v3/sfx.wav")
