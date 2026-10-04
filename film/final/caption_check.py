#!/usr/bin/env python3
"""Caption check: do the captions match the words actually heard? (spec 005 G4)

    python film/final/caption_check.py [--report RENDERS:full_film_v3_report.json]
                                       [--dialogue RENDERS:full_film_v3_stems/dx.wav]
                                       [--model local/models/faster-whisper-medium.en] [--save-words FILE]
                                       [--words FILE] [--captions-dir film/captions/v3] [--slack 0.3]

1. Transcribes the final dialogue stem with faster-whisper (word timestamps, English) - or reads a words file
   saved earlier with --save-words ([{"word", "start", "end"}] in film seconds), which also makes it testable
   without the model.
2. Captions: film/captions/v3/<segment>.json for every segment in the assembly report (segment seconds, moved to
   film time with the report's segment starts).
3. Per caption, compares its words with the words heard inside its window (+/- --slack s), after normalising
   case, punctuation and hyphens. Prints every caption that is not word for word, with what is missing / extra.
Exit code 1 if any caption mismatches (or has no speech under it).
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def resolve(ref: str, root: Path) -> Path:
    return root / ref[len("RENDERS:"):] if ref.startswith("RENDERS:") else Path(ref)


def norm(text: str) -> list[str]:
    text = text.lower().replace("’", "'").replace("-", " ").replace("—", " ")
    return [w for w in re.sub(r"[^a-z0-9'~.%× ]+", " ", text).replace(". ", " ").split() if w.strip(".")]


def clean(tokens: list[str]) -> list[str]:
    return [t.strip(".'") for t in tokens if t.strip(".'")]


def transcribe(audio: Path, model_dir: Path) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("caption_check.py: faster-whisper is not installed (pip install faster-whisper), or pass --words")
    model = WhisperModel(str(model_dir) if model_dir.is_dir() else "medium.en", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio), language="en", word_timestamps=True, vad_filter=True,
                                   condition_on_previous_text=False)
    return [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
            for seg in segments for w in (seg.words or [])]


def load_captions(report: dict, cap_dir: Path) -> list[dict]:
    caps = []
    for s in report["segments"]:
        p = cap_dir / f"{s['name']}.json"
        if s.get("slate") or not p.is_file():
            continue
        for c in json.loads(p.read_text(encoding="utf-8")):
            caps.append({"segment": s["name"], "start": float(s["start"]) + float(c["start"]),
                         "end": float(s["start"]) + float(c["end"]), "text": c["text"]})
    return sorted(caps, key=lambda c: c["start"])


def assign(caps: list[dict], words: list[dict], slack: float) -> list[list[dict]]:
    """Each heard word belongs to exactly one caption: the one containing its midpoint, else the nearest within slack."""
    out = [[] for _ in caps]
    for w in words:
        m = (w["start"] + w["end"]) / 2
        best, dist = None, slack
        for i, c in enumerate(caps):
            d = 0.0 if c["start"] <= m <= c["end"] else min(abs(m - c["start"]), abs(m - c["end"]))
            if d < dist or (d == 0.0 and best is None):
                best, dist = i, d
            if d == 0.0:
                break
        if best is not None:
            out[best].append(w)
    return out


def compare(caps: list[dict], words: list[dict], slack: float) -> list[dict]:
    rows = []
    for c, heard in zip(caps, assign(caps, words, slack)):
        want, got = clean(norm(c["text"])), clean(norm(" ".join(w["word"] for w in heard)))
        sm = difflib.SequenceMatcher(a=want, b=got, autojunk=False)
        missing, extra = [], []
        for op, a0, a1, b0, b1 in sm.get_opcodes():
            if op in ("replace", "delete"):
                missing += want[a0:a1]
            if op in ("replace", "insert"):
                extra += got[b0:b1]
        rows.append(dict(c, heard=" ".join(w["word"] for w in heard), ok=want == got and bool(got),
                         ratio=round(sm.ratio(), 3), missing=missing, extra=extra))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", default="RENDERS:full_film_v3_report.json")
    ap.add_argument("--dialogue", default="RENDERS:full_film_v3_stems/dx.wav")
    ap.add_argument("--model", default=str(REPO / "local/models/faster-whisper-medium.en"))
    ap.add_argument("--words", help="use a saved words file instead of transcribing")
    ap.add_argument("--save-words", help="write the transcribed words here (film seconds)")
    ap.add_argument("--captions-dir", default=str(REPO / "film/captions/v3"))
    ap.add_argument("--slack", type=float, default=0.3, help="seconds of tolerance around each caption window")
    ap.add_argument("--renders-dir", type=Path, help="override renders_dir (tests)")
    args = ap.parse_args()
    root = args.renders_dir or Path(json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))["renders_dir"])
    report = json.loads(resolve(args.report, root).read_text(encoding="utf-8"))
    if args.words:
        words = json.loads(resolve(args.words, root).read_text(encoding="utf-8"))
    else:
        words = transcribe(resolve(args.dialogue, root), Path(args.model))
        if args.save_words:
            resolve(args.save_words, root).write_text(json.dumps(words, indent=1) + "\n", encoding="utf-8")
    caps = load_captions(report, Path(args.captions_dir))
    rows = compare(caps, words, args.slack)
    bad = [r for r in rows if not r["ok"]]
    for r in rows:
        mark = "OK  " if r["ok"] else "DIFF"
        print(f"{mark} {r['start']:8.2f}-{r['end']:<8.2f} {r['segment']:<5} {r['text']!r}")
        if not r["ok"]:
            print(f"       heard:   {r['heard']!r}")
            print(f"       missing: {r['missing']}   extra: {r['extra']}" if r["heard"] else "       no speech heard in this window")
    print(f"\n{len(rows) - len(bad)}/{len(rows)} captions match word for word; {len(bad)} to check")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
