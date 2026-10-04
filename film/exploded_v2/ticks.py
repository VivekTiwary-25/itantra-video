"""Render one soft glass tick per label to RENDERS:exploded_v2/ticks.wav (same family as film/exploded/ticks.py).

Tick times are the label start times in timeline.json, so retiming the labels retimes the ticks.
"""
import json
import math
import struct
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
config = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
destination = Path(config["renders_dir"]) / "exploded_v2" / "ticks.wav"
destination.parent.mkdir(parents=True, exist_ok=True)
timeline = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))

rate = 48000
duration = int(math.ceil(timeline["duration"]))
times = [label["start"] for label in timeline["labels"]]
samples = [0.0] * (rate * duration)

for layer, start_time in enumerate(times):
    start = round(start_time * rate)
    pitch = 1 + layer * 0.035
    for j in range(round(0.27 * rate)):
        if start + j >= len(samples):
            break
        t = j / rate
        attack = min(1.0, t / 0.0035)
        envelope = attack * math.exp(-t * 22.0)
        fm = 0.2 * math.exp(-t * 35) * math.sin(2 * math.pi * 210 * t)
        value = envelope * (
            math.sin(2 * math.pi * 2460 * pitch * t + fm)
            + 0.42 * math.sin(2 * math.pi * 3330 * pitch * t)
            + 0.17 * math.sin(2 * math.pi * 4080 * pitch * t)
        )
        samples[start + j] += value

peak = max(abs(value) for value in samples)
gain = (10 ** (-18 / 20)) / peak
with wave.open(str(destination), "wb") as out:
    out.setnchannels(1)
    out.setsampwidth(2)
    out.setframerate(rate)
    out.writeframes(b"".join(struct.pack("<h", round(value * gain * 32767)) for value in samples))
print("RENDERS:exploded_v2/ticks.wav")
print("Peak: -18.0 dBFS; ticks:", ", ".join(str(t) for t in times))
