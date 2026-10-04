"""Prepare F0005's measured word timings and cleaned voice.

Run from any clone with Python, NumPy, faster-whisper, the local medium.en model,
and the two scene-1 RNNoise models installed. No footage or private paths are
written into tracked outputs. ``--alignment-only`` works without ASR/models.
"""
import argparse
import json
import math
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CONFIG = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
VIDEO = Path(CONFIG["footage_root"]) / "Video/20261002_081346_short_intro.mp4"
AUDIO = Path(CONFIG["footage_root"]) / "Audio/vacchna_short_intro.mp3"
REFERENCE = Path(CONFIG["footage_root"]) / "Audio/vachna part1.mp3"
RENDERS = Path(CONFIG["renders_dir"]) / "intro_v3"
MODEL = REPO / "local/models/faster-whisper-medium.en"
CB = REPO / "local/models/rnnoise/cb.rnnn"
SH = REPO / "local/models/rnnoise/sh.rnnn"
PROMPT = ("I'm Vachana from team chmod 777 for ISRO's problem statement, "
          "SIH26173. We built iTantra, speak, message travels from phone to "
          "phone, no network needed. Let's see how it works.")
SR = 48000


def run(command, cwd=REPO):
    p = subprocess.run([str(x) for x in command], cwd=cwd, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode("utf-8", "replace")[-2200:])
    return p.stdout


def pcm(path, rate=16000, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "1", "-ar", rate, "-f", "f32le", "-"]
    return np.frombuffer(run(cmd), dtype="<f4").astype(np.float64)


def alignment():
    """Return video_time - clean_audio_time, from band-limited waveform correlation."""
    rate = 8000
    filt = "highpass=f=250,lowpass=f=3000"
    camera = pcm(VIDEO, rate, filt)
    clean = pcm(AUDIO, rate, filt)
    camera -= camera.mean()
    clean -= clean.mean()
    size = 1 << math.ceil(math.log2(len(camera) + len(clean) - 1))
    corr = np.fft.irfft(np.fft.rfft(camera, size) *
                        np.conj(np.fft.rfft(clean, size)), size)
    limit = min(4 * rate, len(clean) - 1, len(camera) - 1)
    lags = np.arange(-limit, limit + 1)
    candidates = corr[lags % size]
    # Remove the overlap bias: compare like-for-like signal power at each lag.
    cam_energy = np.r_[0, np.cumsum(camera * camera)]
    cln_energy = np.r_[0, np.cumsum(clean * clean)]
    scores = np.empty(len(lags))
    for i, lag in enumerate(lags):
        ca = max(lag, 0)
        aa = max(-lag, 0)
        length = min(len(camera) - ca, len(clean) - aa)
        denom = math.sqrt((cam_energy[ca + length] - cam_energy[ca]) *
                          (cln_energy[aa + length] - cln_energy[aa]))
        scores[i] = abs(candidates[i]) / denom if denom > 0 else 0
    index = int(np.argmax(scores))
    return {"offset_s": round(float(lags[index] / rate), 4),
            "correlation_peak": round(float(scores[index]), 5),
            "correlation_sign": int(np.sign(candidates[index])),
            "method": "250-3000 Hz normalized waveform cross-correlation at 8 kHz"}


def word_timing():
    if not MODEL.is_dir():
        raise FileNotFoundError("Required local ASR model absent: local/models/faster-whisper-medium.en")
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("faster-whisper Python package is unavailable") from exc
    model = WhisperModel(str(MODEL), device="auto", compute_type="auto", local_files_only=True)
    segments, _ = model.transcribe(str(AUDIO), language="en", beam_size=5,
                                   word_timestamps=True, initial_prompt=PROMPT)
    words = [{"w": w.word.strip(), "s": round(w.start, 3),
              "e": round(w.end, 3), "p": round(w.probability, 3)}
             for segment in segments for w in segment.words]
    if not words:
        raise RuntimeError("ASR returned no words")
    (HERE / "words.json").write_text(json.dumps(words, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return words


def scene1_chain():
    if not CB.is_file() or not SH.is_file():
        raise FileNotFoundError("Required scene-1 RNNoise models absent: local/models/rnnoise/{cb,sh}.rnnn")
    source = (REPO / "film/scene1/build.py").read_text(encoding="utf-8")
    match = re.search(r'^CHAIN = \((.*?)^\)', source, re.M | re.S)
    if not match:
        raise RuntimeError("Scene-1 CHAIN definition not found")
    # Keep the exact current scene-1 chain as the reference, not a drifting copy.
    import ast
    chain = ast.literal_eval("(" + match.group(1) + ")")
    return chain


def spectral_metrics(signal, sample_rate=SR):
    frame = 4096
    signal = signal[:len(signal) // frame * frame].reshape(-1, frame)
    power = np.abs(np.fft.rfft(signal * np.hanning(frame), axis=1)) ** 2
    freqs = np.fft.rfftfreq(frame, 1 / sample_rate)
    mean = power.mean(axis=0)
    total = mean.sum()
    return {"below_300": round(float(mean[freqs < 300].sum() / total), 4),
            "300_to_3000": round(float(mean[(freqs >= 300) & (freqs <= 3000)].sum() / total), 4),
            "above_3000": round(float(mean[freqs > 3000].sum() / total), 4),
            "centroid_hz": round(float((mean * freqs).sum() / total), 1)}


def process_voice(words, offset):
    chain = scene1_chain()
    RENDERS.mkdir(parents=True, exist_ok=True)
    raw = pcm(AUDIO, SR)
    ref = pcm(REFERENCE, SR, chain)
    clean = pcm(AUDIO, SR, chain)
    metrics = {"short_raw": spectral_metrics(raw),
               "short_clean": spectral_metrics(clean),
               "scene1_reference_clean": spectral_metrics(ref)}
    short, scene1 = metrics["short_clean"], metrics["scene1_reference_clean"]
    short_ratio = short["below_300"] / max(short["300_to_3000"], 1e-10)
    scene1_ratio = scene1["below_300"] / max(scene1["300_to_3000"], 1e-10)
    deficit_db = 10 * math.log10(max(short_ratio, 1e-10) / max(scene1_ratio, 1e-10))
    metrics["low_to_mid_deficit_db"] = round(deficit_db, 2)
    metrics["shelf_applied"] = deficit_db < -3 and short["centroid_hz"] > scene1["centroid_hz"] * 1.15
    if metrics["shelf_applied"]:
        clean = pcm(AUDIO, SR, chain + ",bass=f=200:w=0.8:g=2.5")
        metrics["short_after_shelf"] = spectral_metrics(clean)
    (HERE / "voice_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    first, last = words[0]["s"], words[-1]["e"]
    start, end = max(0.0, first - 0.12), last + 0.30
    video_duration = float(json.loads(run(["ffprobe", "-v", "error", "-show_entries",
                                           "format=duration", "-of", "json", VIDEO]))["format"]["duration"])
    if end + offset > video_duration:
        raise RuntimeError(f"Speech window reaches video {end + offset:.3f}s, beyond clip {video_duration:.3f}s")
    left, right = round(start * SR), round(end * SR)
    voice = clean[left:right].copy()
    fade = round(.03 * SR)
    voice[:fade] *= np.linspace(0, 1, fade)
    voice[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(RENDERS / "voice_pre.wav"), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SR)
        output.writeframes((np.clip(voice, -1, 1) * 32767).astype("<i2").tobytes())
    measure = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(RENDERS / "voice_pre.wav"),
                              "-af", "ebur128", "-f", "null", "-"], cwd=REPO,
                             capture_output=True, text=True)
    loudness = re.findall(r"I:\s+(-?[\d.]+) LUFS", measure.stderr)
    if measure.returncode or not loudness:
        raise RuntimeError("Could not measure integrated loudness of prepared voice")
    gain = -16 - float(loudness[-1])
    run(["ffmpeg", "-v", "error", "-y", "-i", RENDERS / "voice_pre.wav",
         "-af", f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=2:release=50:level=false",
         "-ar", SR, RENDERS / "voice.wav"])
    voice = pcm(RENDERS / "voice.wav", SR)
    # Envelope time zero is the rendered audio's first sample.
    envelopes = []
    for i in range(math.ceil(len(voice) / (SR / 30))):
        block = voice[i * 1600:(i + 1) * 1600]
        envelopes.append(round(float(np.sqrt(np.mean(block * block))), 5) if len(block) else 0)
    (HERE / "envelope.json").write_text(json.dumps(envelopes) + "\n", encoding="utf-8")
    return {"window_clean_s": [round(start, 3), round(end, 3)],
            "window_video_s": [round(start + offset, 3), round(end + offset, 3)],
            "metrics": metrics, "pre_gain_lufs": float(loudness[-1]),
            "gain_db": round(gain, 2), "words": words}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alignment-only", action="store_true")
    args = parser.parse_args()
    result = alignment()
    print(json.dumps(result, indent=2))
    if args.alignment_only:
        return
    words = word_timing()
    report = process_voice(words, result["offset_s"])
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
