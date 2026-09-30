"""Generate the fifteen iTantra sound options as deterministic 48 kHz stereo WAVs.

Requires numpy. Run from any directory:
    python film/sound/make_options.py
    python film/sound/make_options.py --out path/to/output

The default destination is renders_dir/sound_options from machine.local.json.
No audio samples, network resources, or random values are used.
"""

from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path

import numpy as np


RATE = 48_000
TARGET_PEAK = 10 ** (-12 / 20)
HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def default_output() -> Path:
    machine = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
    return Path(machine["renders_dir"]) / "sound_options"


def synthesize(spec: dict) -> np.ndarray:
    count = round(spec["duration"] * RATE)
    mono = np.zeros(count, dtype=np.float64)
    for start, duration, low, high, level, harmonic in spec["notes"]:
        first = round(start * RATE)
        length = min(round(duration * RATE), count - first)
        if length <= 0:
            continue
        t = np.arange(length, dtype=np.float64) / RATE
        phase = 2 * np.pi * (low * t + (high - low) * t * t / (2 * duration))
        attack = min(spec["attack"], duration / 3)
        release = min(spec["release"], duration / 2)
        fade_in = np.clip(t / attack, 0, 1)
        fade_out = np.clip((duration - t) / release, 0, 1)
        envelope = np.sin(fade_in * np.pi / 2) ** 2 * np.sin(fade_out * np.pi / 2) ** 2
        envelope *= np.exp(-1.2 * t / duration)
        mono[first:first + length] += level * envelope * (
            np.sin(phase) + harmonic * np.sin(2 * phase)
        )

    # Nine samples of right-channel delay add slight width without a stereo effect.
    stereo = np.stack((mono, np.pad(mono[:-9], (9, 0))), axis=1)
    peak = float(np.max(np.abs(stereo)))
    if peak == 0:
        raise ValueError(f"Silent sound: {spec['id']}")
    stereo *= TARGET_PEAK / peak
    # TPDF dither is deliberately omitted so repeat renders are byte-identical.
    pcm = np.rint(stereo * 32767).astype("<i2")
    return pcm


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Override the default RENDERS:sound_options/ directory")
    args = parser.parse_args()
    destination = args.out if args.out is not None else default_output()
    destination.mkdir(parents=True, exist_ok=True)
    specs = json.loads((HERE / "designs.json").read_text(encoding="utf-8"))
    for spec in specs:
        pcm = synthesize(spec)
        path = destination / (spec["id"] + ".wav")
        with wave.open(str(path), "wb") as output:
            output.setnchannels(2)
            output.setsampwidth(2)
            output.setframerate(RATE)
            output.writeframes(pcm.tobytes())
        print(f"{spec['id']}: {len(pcm) / RATE:.3f} s")


if __name__ == "__main__":
    main()
