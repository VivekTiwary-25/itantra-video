"""T0040 checks: transcribe an audio layer with faster-whisper (word times) and measure energy at cue times.

python results/T0040/check_audio.py transcribe <audio or video under local/renders>
python results/T0040/check_audio.py bursts <wav> <t1> <t2> ...
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]


def decode(path, rate):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(rate), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<f4").copy()


def transcribe(path):
    from faster_whisper import WhisperModel
    model = WhisperModel(str(REPO / "local/models/faster-whisper-medium.en"), device="cpu", compute_type="int8")
    segments, _ = model.transcribe(decode(path, 16000), language="en", word_timestamps=True, vad_filter=False,
                                   condition_on_previous_text=False)
    for seg in segments:
        print(f"[{seg.start:7.2f}-{seg.end:7.2f}] {seg.text.strip()}")
        print("     " + " ".join(f"{w.word.strip()}@{w.start:.2f}" for w in seg.words))


def bursts(path, times):
    x = decode(path, 48000)
    def db(a, b):
        part = x[max(0, round(a * 48000)):round(b * 48000)]
        return -120.0 if not len(part) else 20 * np.log10(max(float(np.sqrt(np.mean(part ** 2))), 1e-6))
    for t in times:
        print(f"{t:8.3f}s  before(-0.35..-0.05) {db(t - .35, t - .05):7.1f} dB   cue(0..+0.30) {db(t, t + .30):7.1f} dB   peak {20*np.log10(max(float(np.abs(x[round(t*48000):round((t+.3)*48000)]).max()),1e-6)):6.1f} dBFS")


if __name__ == "__main__":
    if sys.argv[1] == "transcribe":
        transcribe(sys.argv[2])
    else:
        bursts(sys.argv[2], [float(v) for v in sys.argv[3:]])
