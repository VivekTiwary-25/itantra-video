"""Render a deterministic, offline, 48 kHz stereo PCM music bed.

Usage: python film/music/make_bed.py [--cues film/music/cues.json]
                                 [--output local/renders/music/bed_v3.wav]
The default output is resolved through machine.local.json's renders_dir.
"""

import argparse
import json
import math
import wave
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CUES = Path(__file__).with_name("cues.json")
NOTES = {
    "D2": 73.416, "F2": 87.307, "G2": 97.999, "A2": 110.0,
    "Bb2": 116.541, "C3": 130.813, "D3": 146.832,
    "E3": 164.814, "F3": 174.614, "G3": 195.998,
    "A3": 220.0, "Bb3": 233.082, "C4": 261.626,
    "D4": 293.665, "E4": 329.628, "F4": 349.228,
    "A4": 440.0, "D5": 587.330,
}
VOICES = {
    "intro": ["D3", "A3", "E4", "F4"],
    "s2a": ["D3", "F3", "A3", "E4"],
    "s2b": ["G2", "D3", "F3", "A3"],
    "s3": ["D2", "A2", "F3", "E4"],
    "exploded": ["F3", "A3", "E4", "D5"],
    "cards": ["D3", "F3", "A3", "E4"],
}


def validate(cues):
    sections = cues["sections"]
    if int(cues["sample_rate"]) != 48000:
        raise ValueError("This bed must render at 48 kHz")
    if not sections or sections[0]["start"] != 0:
        raise ValueError("Sections must begin at film second zero")
    for i, section in enumerate(sections):
        if section["name"] not in VOICES:
            raise ValueError(f"Unknown section: {section['name']}")
        if section["end"] <= section["start"]:
            raise ValueError("Each section must have positive duration")
        if i and abs(section["start"] - sections[i - 1]["end"]) > 0.00001:
            raise ValueError("Sections must be contiguous")
    if not 2 <= cues["crossfade_seconds"] <= 3:
        raise ValueError("Crossfade must be 2 to 3 seconds")
    for window in cues["tts_windows"]:
        if not 0 <= window["start"] < window["end"] <= sections[-1]["end"]:
            raise ValueError("TTS windows must be inside the film")


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def section_weight(t, section, index, sections, fade):
    start, end = section["start"], section["end"]
    weight = np.ones_like(t)
    if index:
        weight *= smoothstep((t - (start - fade / 2)) / fade)
    if index < len(sections) - 1:
        weight *= 1 - smoothstep((t - (end - fade / 2)) / fade)
    weight[(t < start - fade / 2) | (t >= end + fade / 2)] = 0
    return weight


def pulse(t, period, phase=0.0):
    # Raised, rounded throb with no sharp transient or drum-like click.
    beat = np.mod((t - phase) / period, 1.0) * period
    return np.exp(-((beat - 0.12) / 0.24) ** 2)


def section_audio(name, t, bpm):
    voices = VOICES[name]
    left = np.zeros_like(t)
    right = np.zeros_like(t)
    for i, note in enumerate(voices):
        f = NOTES[note]
        drift = 0.003 * np.sin(2 * np.pi * (0.033 + i * 0.007) * t + i)
        phase = 2 * np.pi * f * t + drift
        tone = np.sin(phase) + 0.10 * np.sin(2 * phase + 0.7)
        movement = 0.80 + 0.20 * np.sin(2 * np.pi * (0.045 + i * 0.009) * t + i)
        pan = [-0.38, 0.28, -0.15, 0.42][i]
        left += tone * movement * math.sqrt((1 - pan) / 2)
        right += tone * movement * math.sqrt((1 + pan) / 2)
    # Approximately unit RMS per stereo channel before section gain.
    stereo = np.column_stack((left, right)) / 1.20
    if name in ("s2a", "s2b", "s3"):
        period = 60 / bpm
        if name == "s2b":
            period *= 2  # sonar at half time
        elif name == "s3":
            period *= 0.8  # SOS pulse is 25% faster; still soft
        low = np.sin(2 * np.pi * (73.416 if name == "s3" else 97.999) * t)
        throb = (0.12 if name == "s2a" else 0.18) * pulse(t, period) * low
        stereo += throb[:, None]
    if name == "exploded":
        # Quiet glass sheen; three pure upper partials, no impacts.
        sheen = (np.sin(2 * np.pi * NOTES["A4"] * t)
                 + 0.5 * np.sin(2 * np.pi * NOTES["D5"] * t)) * 0.11
        stereo += np.column_stack((sheen, -sheen))
    if name == "cards":
        # Gentle swell, then a Dm(add9) cadence held through the closing fade.
        swell = 0.90 + 0.20 * smoothstep((t - 172) / 8)
        stereo *= swell[:, None]
    return stereo


def render(cues, output):
    validate(cues)
    sr = cues["sample_rate"]
    sections = cues["sections"]
    fade = float(cues["crossfade_seconds"])
    total = round(sections[-1]["end"] * sr)
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        for offset in range(0, total, sr):
            t = np.arange(offset, min(offset + sr, total), dtype=np.float64) / sr
            audio = np.zeros((len(t), 2), dtype=np.float64)
            for i, section in enumerate(sections):
                weight = section_weight(t, section, i, sections, fade)
                if not np.any(weight):
                    continue
                gain = 10 ** (section["level_dbfs"] / 20)
                audio += section_audio(section["name"], t, cues["pulse_bpm"]) * (gain * weight)[:, None]
            # No silence between cues; only the very beginning and end fade.
            fade_in = smoothstep(t / 1.5)
            fade_out = smoothstep((sections[-1]["end"] - t) / 3.0)
            audio *= (fade_in * fade_out)[:, None]
            peak = np.max(np.abs(audio))
            if peak >= 0.98:
                raise ValueError(f"Unexpected peak {peak:.3f}; lower cue levels")
            wav.writeframes((np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes())
    print(f"Wrote {output.name}: {total / sr:.3f} s, {sr} Hz stereo")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cues", type=Path, default=DEFAULT_CUES)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cues = json.loads(args.cues.read_text(encoding="utf-8"))
    config = json.loads((ROOT / "machine.local.json").read_text(encoding="utf-8"))
    output = args.output or Path(config["renders_dir"]) / "music" / "bed_v3.wav"
    render(cues, output)


if __name__ == "__main__":
    main()
