"""Write a deterministic, very quiet tick stem for the title card (48 kHz stereo)."""
from pathlib import Path
import math
import random
import struct
import wave

SR = 48000
DURATION = 20.0
LANDINGS = (0.6, 4.0, 7.4, 10.8, 14.5)


def make_tick():
    rng = random.Random(777)
    length = int(0.11 * SR)
    raw = []
    for i in range(length):
        t = i / SR
        attack = min(1.0, t / 0.002)
        sound = (math.sin(2 * math.pi * 1080 * t) * math.exp(-t * 75)
                 + 0.12 * (rng.random() * 2 - 1) * math.exp(-t * 170))
        raw.append(sound * attack * 0.012)
    return raw


def main():
    path = Path(__file__).resolve().parent / "assets" / "title_sfx.wav"
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = [0.0] * int(DURATION * SR)
    tick = make_tick()
    for landing in LANDINGS:
        start = round(landing * SR)
        for i, sample in enumerate(tick):
            frames[start + i] += sample
    pcm = bytearray()
    for sample in frames:
        value = round(max(-1.0, min(1.0, sample)) * 32767)
        pcm.extend(struct.pack("<hh", value, value))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        wav.writeframes(pcm)
    print(f"Wrote {path.name}: {DURATION:.1f}s, {len(LANDINGS)} quiet ticks")


if __name__ == "__main__":
    main()
