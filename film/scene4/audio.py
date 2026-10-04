"""Create a scene-length narration and soft-tick mix in RENDERS:scene4/."""
import json
import math
import struct
import subprocess
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RENDERS = Path(json.loads((ROOT / "machine.local.json").read_text(encoding="utf-8"))["renders_dir"])
OUT = RENDERS / "scene4"
TIMELINE = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
LINES = json.loads((ROOT / "film/common/narration_v4.json").read_text(encoding="utf-8"))["lines"]
ORDER = ("N7", "N7a", "N7b", "N7c", "N7d")
SR = 48000


def silence(path, duration):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"\0\0" * round(duration * SR))


def ticks(path):
    duration = TIMELINE["duration"]
    pulse = [0.0] * round(duration * SR)
    a, b = TIMELINE["beats"]["numbers"]
    every = (b - a) / 5
    events = [a + i * every for i in range(5)] + [TIMELINE["narration"]["N7c"]["start"] + .35]
    for when in events:
        start = round(when * SR)
        for j in range(round(.11 * SR)):
            i = start + j
            if i < len(pulse):
                s = j / SR
                pulse[i] += .13 * math.exp(-40 * s) * math.sin(2 * math.pi * (1260 - 460 * s) * s)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(struct.pack("<" + "h" * len(pulse), *(round(max(-1, min(1, x)) * 32767) for x in pulse)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    missing = []
    sources = []
    for key in ORDER:
        line = LINES[key]
        src = RENDERS / "narration/v4" / f"{key}.wav"
        if not src.is_file():
            src = OUT / f"placeholder_{key}.wav"
            silence(src, line["duration"])
            missing.append(key)
        else:
            probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(src)], check=True, capture_output=True, text=True)
            actual = float(probe.stdout)
            if actual > float(line["duration"]) + .05:
                raise ValueError(f"{key} audio is longer than narration_v4.json; update duration before rendering")
        sources.append(src)
    tick = OUT / "ticks.wav"
    ticks(tick)
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for src in sources + [tick]:
        cmd += ["-i", str(src)]
    filters = []
    for i, key in enumerate(ORDER):
        delay = round(TIMELINE["narration"][key]["start"] * 1000)
        filters.append(f"[{i}:a]aresample={SR},aformat=sample_fmts=fltp:channel_layouts=mono,adelay={delay}|{delay}[n{i}]")
    filters.append(f"[{len(ORDER)}:a]aresample={SR},aformat=sample_fmts=fltp:channel_layouts=mono[t]")
    joined = "".join(f"[n{i}]" for i in range(len(ORDER))) + "[t]"
    filters.append(f"{joined}amix=inputs={len(ORDER)+1}:duration=longest:normalize=0,atrim=duration={TIMELINE['duration']:.6f}[mix]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "[mix]", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(OUT / "scene4_audio.wav")]
    subprocess.run(cmd, check=True)
    print("silent placeholders:", ", ".join(missing) if missing else "none")


if __name__ == "__main__":
    main()
