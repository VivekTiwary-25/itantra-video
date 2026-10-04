"""Duck the music bed under speech and the app's TTS.

    python film/music/duck.py --bed <bed_v3.wav> --dialogue <dialogue_stem.wav> [--cues film/music/cues.json] [--out <wav>]

- Speech is detected from the dialogue stem's envelope (10 ms RMS, threshold in cues.json `duck.threshold_dbfs`,
  with a short hold so the bed does not pump between words).
- Under speech the bed drops by `duck.speech_db` (default -10 dB); inside each `tts_windows` entry it drops a further
  `duck.tts_extra_db` (default -4 dB).
- The gain moves with a 150 ms attack (going down) and 600 ms release (coming back up), applied in dB.
Default output: RENDERS:music/bed_v3_ducked.wav. Both inputs must be 48 kHz; the dialogue may be mono or stereo and is
padded or trimmed to the bed's length (a warning is printed if the lengths differ by more than 0.1 s).
"""
from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CUES = Path(__file__).with_name("cues.json")
SR = 48000
FRAME = 0.010  # control rate: 10 ms


def read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        if w.getframerate() != SR:
            raise ValueError(f"{path.name}: {w.getframerate()} Hz, expected {SR}")
        if w.getsampwidth() != 2:
            raise ValueError(f"{path.name}: only 16-bit PCM is supported")
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32768
        return x.reshape(-1, w.getnchannels())


def write_wav(path: Path, x: np.ndarray):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).round().astype("<i2").tobytes())


def speech_mask(dialogue: np.ndarray, threshold_dbfs: float, hold_s: float) -> np.ndarray:
    """True per 10 ms frame where speech is present (RMS over threshold, then held)."""
    mono = dialogue.mean(axis=1)
    hop = int(FRAME * SR)
    n = len(mono) // hop
    rms = np.sqrt((mono[: n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-20)
    on = 20 * np.log10(rms) > threshold_dbfs
    hold = int(round(hold_s / FRAME))
    if hold:
        idx = np.where(on)[0]
        held = np.zeros_like(on)
        for i in idx:  # extend each active frame forward by the hold time
            held[i : i + hold + 1] = True
        on = held[:n]
    return on


def smooth_db(target_db: np.ndarray, attack_s: float, release_s: float) -> np.ndarray:
    """One-pole smoothing in dB: attack when the gain falls, release when it rises."""
    a = np.exp(-FRAME / max(attack_s, 1e-4))
    r = np.exp(-FRAME / max(release_s, 1e-4))
    out = np.empty_like(target_db)
    g = 0.0
    for i, tgt in enumerate(target_db):
        c = a if tgt < g else r
        g = c * g + (1 - c) * tgt
        out[i] = g
    return out


def duck(bed: np.ndarray, dialogue: np.ndarray, cues: dict) -> tuple[np.ndarray, dict]:
    d = cues.get("duck", {})
    speech_db = float(d.get("speech_db", -10.0))
    tts_db = float(d.get("tts_extra_db", -4.0))
    attack = float(d.get("attack_ms", 150)) / 1000
    release = float(d.get("release_ms", 600)) / 1000
    hold = float(d.get("hold_ms", 250)) / 1000
    thr = float(d.get("threshold_dbfs", -45.0))

    if abs(len(dialogue) - len(bed)) > 0.1 * SR:
        print(f"warning: dialogue is {len(dialogue) / SR:.2f} s, bed is {len(bed) / SR:.2f} s; padding/trimming")
    if len(dialogue) < len(bed):
        dialogue = np.vstack([dialogue, np.zeros((len(bed) - len(dialogue), dialogue.shape[1]))])
    dialogue = dialogue[: len(bed)]

    frames = int(np.ceil(len(bed) / (FRAME * SR)))
    mask = speech_mask(dialogue, thr, hold)
    mask = np.concatenate([mask, np.zeros(frames - len(mask), bool)])
    target = np.where(mask, speech_db, 0.0)
    times = np.arange(frames) * FRAME
    for w in cues.get("tts_windows", []):
        target[(times >= float(w["start"])) & (times < float(w["end"]))] += tts_db
    gain_db = smooth_db(target, attack, release)
    # control rate -> sample rate
    gain = 10 ** (np.interp(np.arange(len(bed)) / SR, times, gain_db) / 20)
    stats = {"speech_seconds": float(mask.sum() * FRAME), "min_gain_db": float(gain_db.min())}
    return bed * gain[:, None], stats


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bed", type=Path, help="default RENDERS:music/bed_v3.wav")
    ap.add_argument("--dialogue", type=Path, required=True, help="dialogue stem, 48 kHz 16-bit, same length as the bed")
    ap.add_argument("--cues", type=Path, default=DEFAULT_CUES)
    ap.add_argument("--out", type=Path, help="default RENDERS:music/bed_v3_ducked.wav")
    args = ap.parse_args()
    cfg = json.loads((ROOT / "machine.local.json").read_text(encoding="utf-8"))
    music = Path(cfg["renders_dir"]) / "music"
    bed_path = args.bed or music / "bed_v3.wav"
    out = args.out or music / "bed_v3_ducked.wav"
    cues = json.loads(args.cues.read_text(encoding="utf-8"))
    ducked, stats = duck(read_wav(bed_path), read_wav(args.dialogue), cues)
    write_wav(out, ducked)
    print(f"wrote {out.name}: speech detected {stats['speech_seconds']:.1f} s, deepest duck {stats['min_gain_db']:.1f} dB")


if __name__ == "__main__":
    main()
