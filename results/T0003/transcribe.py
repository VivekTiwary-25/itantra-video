import json
import re
import subprocess
import tempfile
import wave
from pathlib import Path

from faster_whisper import WhisperModel
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
FOOTAGE = Path(json.loads((ROOT / "machine.local.json").read_text())["footage_root"])
MODEL = ROOT / "local" / "models" / "faster-whisper-medium.en"
OUT = Path(__file__).resolve().parent


def main():
    model = WhisperModel(str(MODEL), device="cpu", compute_type="int8", cpu_threads=6)
    sources = [("cam", p) for p in sorted((FOOTAGE / "Video").glob("*.mp4"), key=lambda p: p.name.lower())]
    sources += [("clean", FOOTAGE / "Audio" / n) for n in (
        "normalpart1.mp3", "Normalpart6.mp3", "sospart1.mp3", "sospart2.mp3"
    )]
    summaries = []
    for kind, source in sources:
        name = source.stem
        with tempfile.TemporaryDirectory(dir=ROOT / "local" / "tmp") as temp:
            wav = Path(temp) / "audio.wav"
            args = ["ffmpeg", "-v", "error", "-y", "-i", str(source)]
            if kind == "cam":
                args += ["-map", "0:a:0?"]
            args += ["-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)]
            subprocess.run(args, check=True)
            if not wav.exists() or wav.stat().st_size == 0:
                segments, duration = [], 0.0
            else:
                with wave.open(str(wav)) as f:
                    duration = f.getnframes() / f.getframerate()
                    audio = np.frombuffer(f.readframes(f.getnframes()), dtype="<i2").astype(np.float32) / 32768
                segs, info = model.transcribe(audio, language="en", word_timestamps=True,
                                               vad_filter=True, beam_size=5)
                duration = info.duration
                segments = []
                for s in segs:
                    segments.append({
                        "start": s.start, "end": s.end, "text": s.text,
                        "avg_logprob": s.avg_logprob, "no_speech_prob": s.no_speech_prob,
                        "words": [{"start": w.start, "end": w.end,
                                   "word": w.word, "probability": w.probability}
                                  for w in (s.words or [])],
                    })
        stem = f"{kind}__{name.replace(' ', '_')}"
        (OUT / f"{stem}.json").write_text(json.dumps(segments, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (OUT / f"{stem}.txt").write_text("".join(f"[{s['start']:.2f}-{s['end']:.2f}] {s['text'].strip()}\n" for s in segments), encoding="utf-8")
        marked = []
        for s in segments:
            text = s["text"].strip()
            for w in s["words"]:
                if w["probability"] < 0.5:
                    token = w["word"].strip()
                    if token:
                        text = re.sub(r"(?<!\w)" + re.escape(token) + r"(?!\w)", f"[?{token}]", text, count=1, flags=re.I)
            marked.append(text)
        full = " ".join(marked)
        summaries.append((kind, name, duration, bool(full.strip()), full))
    lines = ["# Transcripts", ""]
    for kind, name, duration, speech, full in summaries:
        notes = {
            ("cam", "normalpart2"): "Background conversation is audible; transcript includes production/setup talk. No clear TTS identified.",
            ("cam", "vachna part2"): "Spoken product explanation; possible second voice is not distinguishable from transcript alone. No clear TTS identified.",
            ("cam", "sospart1"): "Speech matches the SOS phrase in the clean recording; app tones cannot be identified from ASR output.",
            ("cam", "sospart2"): "Only a faint/unclear speech-like fragment was recognized; app sounds may be present but are not identifiable from ASR output.",
        }.get((kind, name), "No clear TTS or app sound identified from the transcript; brief speech fragments may be background talk.")
        lines += [f"## {kind} — {name}", f"Duration: {duration:.2f} seconds", f"Speech: {'yes' if speech else 'no'}",
                  f"Text: {full or '(none detected)'}", f"Notes: {notes}", ""]
    (OUT / "transcripts.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
