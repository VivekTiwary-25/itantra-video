"""Write the cards' narration stem RENDERS:cards_v3/cards_dx.wav (mono 48 kHz, segment length).

N8 starts over the Works now / Coming next card, N9 over the closing card; times and the stem length
come from cards_timing.py (film/common/narration_v4.json). The takes are the RENDERS: wavs named in the
manifest (stand-ins, silent, until the real takes arrive). Takes are placed as they are (no gain change).
"""
import json
import struct
import wave
from pathlib import Path

import numpy as np

import cards_timing

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
config = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
renders = Path(config["renders_dir"])
RATE = 48000


def read_take(ref):
    """RENDERS:<rel> -> float mono samples at 48 kHz."""
    with wave.open(str(renders / ref.split(":", 1)[1]), "rb") as w:
        ch, width, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if width != 2:
        raise SystemExit(f"{ref}: expected 16-bit PCM")
    x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    x = x.reshape(-1, ch).mean(axis=1)
    if rate != RATE:
        t_new = np.arange(int(len(x) * RATE / rate)) / RATE
        x = np.interp(t_new, np.arange(len(x)) / rate, x)
    return x


T = cards_timing.load()
out = np.zeros(round(T["end"] * RATE))
for key in ("n8", "n9"):
    take = read_take(T[key]["file"])
    start = round(T[key]["start"] * RATE)
    n = min(len(take), len(out) - start)
    out[start:start + n] += take[:n]
    print(f"{key.upper()}: take {len(take) / RATE:.3f} s (manifest {T[key]['duration']} s) at {T[key]['start']} s")

destination = renders / "cards_v3" / "cards_dx.wav"
destination.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(destination), "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(RATE)
    f.writeframes(np.clip(np.round(out * 32767), -32768, 32767).astype("<i2").tobytes())
print("RENDERS:cards_v3/cards_dx.wav", f"{T['end']} s")
