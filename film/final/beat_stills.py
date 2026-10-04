#!/usr/bin/env python3
"""Beat stills for an assembled film: every beat at full size and at phone size, plus the joins.

    python film/final/beat_stills.py [--film RENDERS:full_film_v3_draft.mp4] [--report <assembly report json>]
                                     [--out <dir>] [--beats-only] [--renders-dir DIR]

- Segments and their film start times come from the assembly report (`<film>_report.json` by default).
- Beats come from each segment's own timeline.json (folder from film/final/v3_segments.json):
  `segments` lists (s2a/s2b/s3), `tech_lines`/`techlines`, `labels` + `explode`/`close` (exploded_v2),
  flat {cue: time} maps (intro_v3), and built-in beats for cards_v3 (it has no timeline file).
  One frame per beat (its middle), plus the first and last frame of every segment.
- Writes, by default to RENDERS:review/<film name>/:
  frames/*.jpg (full size, q2), beats_full.jpg (960 px tiles), beats_phone.jpg (480 px tiles), joins.jpg.
- Slate segments (draft) get only first/last frames.
Needs ffmpeg/ffprobe and Pillow.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FPS = 30
FOLDER_DEFAULTS = {"intro": "film/intro_v3", "s2a": "film/scene2/v3a", "s2b": "film/scene2/v3b",
                   "s3": "film/scene3/v3", "exploded": "film/exploded_v2", "cards": "film/cards_v3"}
CARDS_BEATS = [("items in", 1.6), ("works now hold", 5.0), ("transition", 8.4), ("closing card", 11.0)]


def resolve(ref: str, root: Path) -> Path:
    return root / ref[len("RENDERS:"):] if ref.startswith("RENDERS:") else Path(ref)


def seg_folders() -> dict:
    out = dict(FOLDER_DEFAULTS)
    p = REPO / "film/final/v3_segments.json"
    if p.is_file():
        for s in json.loads(p.read_text(encoding="utf-8")).get("segments", []):
            if s.get("folder"):
                out[s["name"]] = s["folder"].rstrip("/")
    return out


def mid(a, b):
    return (float(a) + float(b)) / 2


def beats_from_timeline(name: str, folder: str, duration: float) -> list[tuple[str, float]]:
    """(beat name, segment-relative time) pairs, before clamping."""
    if name == "cards" or folder.endswith("cards_v3"):
        return list(CARDS_BEATS)
    p = REPO / folder / "timeline.json"
    if not p.is_file():
        return [(f"t {t:g}", float(t)) for t in range(3, int(duration), 3)]  # unknown: every 3 s
    d = json.loads(p.read_text(encoding="utf-8"))
    beats = []
    for s in d.get("segments", []) if isinstance(d.get("segments"), list) else []:
        if "start" in s and "end" in s:
            beats.append((s.get("name", "segment"), mid(s["start"], s["end"])))
    for key in ("tech_lines", "techlines"):
        for s in d.get(key, []) or []:
            beats.append(("tech: " + str(s.get("text", ""))[:28], mid(s["start"], s["end"])))
    for s in d.get("labels", []) or []:
        if "start" in s and "end" in s:
            beats.append(("label: " + str(s.get("title", ""))[:28], mid(s["start"], s["end"])))
    for key in ("explode", "close", "sweep"):
        v = d.get(key)
        if isinstance(v, list) and len(v) == 2:
            beats.append((key, mid(*v)))
    el = d.get("end_line")
    if isinstance(el, dict) and "start" in el:
        beats.append(("end line", float(el["start"]) + 0.6))
    if not beats:  # flat {cue: seconds} map (intro_v3): a moment just after each cue
        for k, v in d.items():
            if isinstance(v, (int, float)) and not k.startswith("_") and k not in ("fps", "duration"):
                beats.append((k, float(v) + 0.4))
    return beats


def build_beats(report: dict) -> list[dict]:
    folders = seg_folders()
    rows = []
    for s in report["segments"]:
        start, dur = float(s["start"]), float(s["duration"])
        last = max(0.0, dur - 1 / FPS)
        inner = [] if s.get("slate") else beats_from_timeline(s["name"], folders.get(s["name"], ""), dur)
        items = [("first frame", 0.0)] + [(n, t) for n, t in inner if 0 < t < last] + [("last frame", last)]
        seen = set()
        for n, t in sorted(items, key=lambda x: x[1]):
            frame = round(t * FPS)
            if frame in seen:
                continue
            seen.add(frame)
            rows.append({"segment": s["name"], "beat": n, "seg_time": frame / FPS,
                         "film_time": round(start + frame / FPS, 3), "join": n in ("first frame", "last frame"),
                         "slate": bool(s.get("slate"))})
    return rows


def extract(film: Path, t: float, out: Path):
    # ffmpeg's -ss takes the first frame at or after t; aim a quarter frame early so a rounded time
    # (e.g. 13.767 for frame 413 at 13.7667) still lands on the intended frame, not the next one.
    t = max(0.0, round(t * FPS) / FPS - 0.25 / FPS)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-ss", f"{t:.4f}",
                    "-i", str(film), "-frames:v", "1", "-q:v", "2", str(out)], check=True)


def sheet(items, width, out: Path, cols: int):
    from PIL import Image, ImageDraw, ImageFont
    h = round(width * 9 / 16)
    lab = max(18, width // 30)
    try:
        font = ImageFont.truetype("segoeui.ttf" if sys.platform == "win32" else "DejaVuSans.ttf", lab)
    except OSError:
        font = ImageFont.load_default()
    pad, cap = 8, lab + 14
    rows = (len(items) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * (width + pad) + pad, rows * (h + cap + pad) + pad), (22, 22, 22))
    d = ImageDraw.Draw(canvas)
    for i, (img_path, label) in enumerate(items):
        x, y = pad + (i % cols) * (width + pad), pad + (i // cols) * (h + cap + pad)
        canvas.paste(Image.open(img_path).convert("RGB").resize((width, h), Image.LANCZOS), (x, y + cap))
        d.text((x + 2, y + 4), label, fill=(235, 235, 235), font=font)
    canvas.save(out, quality=88)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--film", default="RENDERS:full_film_v3_draft.mp4")
    ap.add_argument("--report", help="assembly report json (default: <film>_report.json next to the film)")
    ap.add_argument("--out", help="output folder (default: RENDERS:review/<film name>/)")
    ap.add_argument("--renders-dir", type=Path, help="override renders_dir (tests)")
    ap.add_argument("--beats-only", action="store_true", help="print the beat table and exit")
    args = ap.parse_args()
    root = args.renders_dir or Path(json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))["renders_dir"])
    film = resolve(args.film, root)
    report_path = resolve(args.report, root) if args.report else film.with_name(film.stem + "_report.json")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    rows = build_beats(report)
    print(f"{'film s':>8}  {'segment':<9} {'seg s':>7}  beat")
    for r in rows:
        print(f"{r['film_time']:8.3f}  {r['segment']:<9} {r['seg_time']:7.3f}  {r['beat']}{'  [slate]' if r['slate'] else ''}")
    if args.beats_only:
        return 0
    if not film.is_file():
        sys.exit(f"beat_stills.py: film not found: {film}")
    out = resolve(args.out, root) if args.out else root / "review" / film.stem
    frames = out / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    items = []
    for i, r in enumerate(rows):
        p = frames / f"{i:03d}_{r['film_time']:08.3f}_{r['segment']}.jpg"
        extract(film, r["film_time"], p)
        r["file"] = p.name
        items.append((p, f"{r['film_time']:.2f}s  {r['segment']}  {r['beat']}"))
    sheet(items, 960, out / "beats_full.jpg", cols=3)
    sheet(items, 480, out / "beats_phone.jpg", cols=4)
    joins = []
    by_seg = [r for r in rows if r["join"]]
    for a, b in zip(by_seg, by_seg[1:]):
        if a["beat"] == "last frame" and b["beat"] == "first frame":
            joins += [(frames / a["file"], f"{a['segment']} last  {a['film_time']:.2f}s"),
                      (frames / b["file"], f"{b['segment']} first  {b['film_time']:.2f}s")]
    if joins:
        sheet(joins, 960, out / "joins.jpg", cols=2)
    (out / "beats.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    for name in ("beats_full.jpg", "beats_phone.jpg", "joins.jpg", "beats.json"):
        if (out / name).exists():
            print(out / name)
    print(f"{len(rows)} frames in {frames}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
