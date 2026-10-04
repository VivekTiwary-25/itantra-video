#!/usr/bin/env python3
"""Assemble film v3: rendered segments -> RENDERS:full_film_v3.mp4 with dialogue, sfx and the ducked music bed.

    python film/final/assemble_v3.py [--segments film/final/v3_segments.json] [--draft] [--renders-dir DIR]
                                     [--reuse-bed] [--bed-trim-db N] [--no-qc]

Steps:
1. Resolve every segment's picture and stems (RENDERS: paths, via machine.local.json). Check that each file exists and
   that its length matches expected_duration. A missing file is an error; --draft puts a 2 s dark slate with the
   segment name in its place and lists it.
2. Pictures: stream-copy concat if every file matches exactly, otherwise one H.264 encode
   (yuv420p, 1920x1080, 30 fps, CRF 18).
3. Dialogue (dx) and sfx stems are laid on the film timeline, each segment trimmed or padded to its own picture length.
   Speech is never stretched or cut; any audio past a segment's last frame is reported.
4. Music: a film-level cue sheet (section starts = real segment starts, TTS windows moved to film time) is written to
   the work folder, then film/music/make_bed.py renders the bed and film/music/duck.py ducks it under the dx stem.
   The committed film/music/cues.json is only read, never changed.
5. The bed is trimmed so it keeps MIX.md's distance to the dialogue (bed sections are set for dialogue at -18 LUFS).
   The mix is dx + sfx + ducked bed, mastered to -16 LUFS integrated, true peak <= -1.5 dBTP (linear gain; a limiter
   only if the peak needs it), then muxed as AAC 48 kHz stereo 256 kbps.
Outputs (a --draft run adds "_draft" to every name so it can never replace a real assembly):
  RENDERS:full_film_v3.mp4, RENDERS:full_film_v3_nomusic.mp4, RENDERS:full_film_v3_stems/{dx,sfx,music}.wav,
  RENDERS:full_film_v3_report.json; work files in RENDERS:full_film_v3_work/. Then film/final/qc.py --v3 runs.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FPS = 30
RATE = 48000
TARGET_I = -16.0
TARGET_TP = -1.8          # margin for AAC; the encoded film must stay <= -1.5 dBTP
DIALOGUE_REF = -18.0      # MIX.md: dialogue about -18 LUFS; bed section levels assume it
SLATE_S = 2.0
MIN_MUSIC_SECTION = 6.0   # shorter segments (slates) are merged into a neighbour for the music cue sheet
WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    print("WARNING: " + msg)


def run(args, *, capture=False, cwd=None):
    r = subprocess.run([str(a) for a in args], text=True, encoding="utf-8", errors="replace",
                       capture_output=True, cwd=cwd)
    if r.returncode:
        detail = (r.stderr or r.stdout or "").strip()
        raise RuntimeError(f"command failed ({r.returncode}): {' '.join(map(str, args[:6]))}\n{detail[-4000:]}")
    return r


def ffmpeg(*args):
    return run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", *args])


def rate(v: str) -> float:
    n, d = v.split("/")
    return float(n) / float(d) if float(d) else 0.0


def probe(path: Path) -> dict:
    info = json.loads(run(["ffprobe", "-v", "error", "-count_packets", "-of", "json", "-show_format",
                           "-show_streams", path], capture=True).stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    return {"info": info, "video": v, "audio": a, "duration": float(info["format"].get("duration", 0))}


def loudness(path: Path) -> dict:
    log = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", path, "-vn", "-af",
               f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA=11:print_format=json", "-f", "null", "-"],
              capture=True).stderr
    m = re.findall(r"\{\s*\"input_i\".*?\}", log, re.S)
    if not m:
        raise RuntimeError("could not read loudnorm output\n" + log[-2000:])
    d = json.loads(m[-1])
    return {"integrated_lufs": float(d["input_i"]), "true_peak_dbtp": float(d["input_tp"]),
            "lra": float(d["input_lra"])}


def slate_font() -> str | None:
    """A system font for the slate text, found at run time (never a committed absolute path)."""
    windir = os.environ.get("WINDIR")
    for cand in ([Path(windir) / "Fonts" / f for f in ("segoeui.ttf", "arial.ttf")] if windir else []) + \
            [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]:
        if cand.is_file():
            return cand.as_posix().replace(":", r"\:")
    return None


def make_slate(name: str, out: Path) -> None:
    font = slate_font()
    text = f"MISSING SEGMENT\\: {name}"
    vf = "format=yuv420p"
    if font:
        vf = (f"drawtext=fontfile='{font}':text='{text}':fontcolor=0xf3f5f8:fontsize=64:"
              f"x=(w-text_w)/2:y=(h-text_h)/2,format=yuv420p")
    ffmpeg("-f", "lavfi", "-i", f"color=c=0x0a0d12:s=1920x1080:r={FPS}:d={SLATE_S}",
           "-f", "lavfi", "-i", f"anullsrc=r={RATE}:cl=stereo", "-t", f"{SLATE_S}",
           "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", out)


# ---------------------------------------------------------------- segments
def load_segments(path: Path, resolve, draft: bool, work: Path) -> list[dict]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    out, start, missing = [], 0, []
    for s in spec["segments"]:
        seg = {"name": s["name"], "spec": s, "slate": False}
        video = resolve(s["video"])
        if video is None or not video.is_file():
            if not draft:
                missing.append(f"{s['name']}: {s['video']}")
                continue
            video = work / f"slate_{s['name']}.mp4"
            make_slate(s["name"], video)
            seg["slate"] = True
            warn(f"{s['name']}: {s['video']} missing; using a {SLATE_S:g} s slate")
        p = probe(video)
        v = p["video"]
        if v is None:
            raise ValueError(f"{s['name']}: no video stream in {s['video']}")
        frames = int(v.get("nb_read_packets") or round(p["duration"] * FPS))
        fps = rate(v["avg_frame_rate"])
        ok_format = (v["width"], v["height"]) == (1920, 1080) and math.isclose(fps, FPS, abs_tol=0.01)
        if not ok_format:
            msg = f"{s['name']}: {v['width']}x{v['height']} at {fps:g} fps (expected 1920x1080 at {FPS})"
            if not draft:
                raise ValueError(msg)
            warn(msg + "; will be conformed")
        duration = frames / FPS
        exp = s.get("expected_duration")
        if not seg["slate"]:
            if exp is None:
                warn(f"{s['name']}: no expected_duration in the segments file; accepted {duration:.3f} s")
            elif abs(duration - float(exp)) > 2 / FPS + 0.02:
                msg = f"{s['name']}: picture is {duration:.3f} s, expected {float(exp):.3f} s"
                if not draft:
                    raise ValueError(msg)
                warn(msg)
        stems = {}
        for kind in ("dx", "sfx"):
            ref = (s.get("stems") or {}).get(kind)
            if ref == "embedded":
                if p["audio"] is None:
                    warn(f"{s['name']}: {kind} is 'embedded' but the picture has no audio; silence used")
                    stems[kind] = None
                else:
                    stems[kind] = (video, True)
            elif ref:
                f = resolve(ref)
                if f is None or not f.is_file():
                    if seg["slate"] or draft:
                        warn(f"{s['name']}: {kind} stem {ref} missing; silence used")
                        stems[kind] = None
                    else:
                        missing.append(f"{s['name']} {kind}: {ref}")
                        continue
                else:
                    stems[kind] = (f, False)
                    sd = probe(f)["duration"]
                    if sd > duration + 0.05 and not seg["slate"]:
                        warn(f"{s['name']}: {kind} stem is {sd:.3f} s, {sd - duration:.3f} s longer than the picture; "
                             "the tail after the last frame is dropped (check it holds no speech)")
            else:
                stems[kind] = None
        if seg["slate"]:
            stems = {"dx": None, "sfx": stems.get("sfx")}
        seg.update(video=video, probe=p, frames=frames, duration=duration, start=start / FPS,
                   stems=stems, format_ok=ok_format)
        start += frames
        out.append(seg)
    if missing:
        raise ValueError("missing inputs (use --draft to substitute slates):\n  " + "\n  ".join(missing))
    return out


def tts_windows(seg: dict, resolve) -> list[list[float]]:
    """Segment-time TTS windows: from the build's events log if present, else from the segments file."""
    s = seg["spec"]
    if seg["slate"]:
        return []
    ev = resolve(s["tts_events"]) if s.get("tts_events") else None
    if ev and ev.is_file():
        rows = [[float(a), float(b)] for a, b, label in
                re.findall(r"^\s*([\d.]+)\s+([\d.]+)\s+(.*)$", ev.read_text(encoding="utf-8"), re.M)
                if "app TTS" in label]
        if rows:
            return rows
    out = []
    for a, b in s.get("tts_windows", []):
        a = a + seg["duration"] if a < 0 else a
        b = b + seg["duration"] if b < 0 else b
        if 0 <= a < b <= seg["duration"] + 1e-6:
            out.append([a, b])
        else:
            warn(f"{seg['name']}: TTS window {a:.2f}-{b:.2f} s is outside the segment; skipped")
    return out


# ---------------------------------------------------------------- picture
def signature(v):
    keys = ("codec_name", "profile", "level", "pix_fmt", "width", "height", "avg_frame_rate", "r_frame_rate",
            "time_base", "color_space", "color_primaries", "color_transfer", "sample_aspect_ratio")
    return tuple(v.get(k) for k in keys)


def make_picture(segs, out: Path, draft: bool) -> str:
    total = sum(s["frames"] for s in segs)
    sigs = {signature(s["probe"]["video"]) for s in segs}
    if len(sigs) == 1 and segs[0]["probe"]["video"]["codec_name"] == "h264" and not any(s["slate"] for s in segs):
        listing = out.with_suffix(".concat.txt")
        listing.write_text("".join("file '" + s["video"].resolve().as_posix().replace("'", "'\\''") + "'\n"
                                   for s in segs), encoding="utf-8")
        try:
            ffmpeg("-f", "concat", "-safe", "0", "-i", listing, "-map", "0:v:0", "-an", "-c:v", "copy", out)
            v = probe(out)["video"]
            if int(v.get("nb_read_packets", 0)) == total:
                return "stream_copy"
            print("stream copy changed the frame count; encoding once instead")
        finally:
            listing.unlink(missing_ok=True)
    inputs = [x for s in segs for x in ("-i", s["video"])]
    chains = [f"[{i}:v:0]fps={FPS},scale=1920:1080:force_original_aspect_ratio=decrease,"
              f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,setpts=PTS-STARTPTS,"
              f"trim=end_frame={s['frames']}[v{i}]" for i, s in enumerate(segs)]
    chains.append("".join(f"[v{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0,format=yuv420p[out]")
    ffmpeg(*inputs, "-filter_complex", ";".join(chains), "-map", "[out]", "-an", "-c:v", "libx264",
           "-preset", "veryfast" if draft else "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-frames:v", str(total), "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", out)
    return "libx264_crf18"


# ---------------------------------------------------------------- audio
def make_stem(segs, kind: str, out: Path) -> None:
    """Concatenate one stem kind across segments; each piece is trimmed or padded to its segment's picture length."""
    inputs, chains = [], []
    for i, s in enumerate(segs):
        src = s["stems"].get(kind)
        d = s["frames"] / FPS
        if src:
            inputs += ["-i", src[0]]
            chains.append(f"[{i}:a:0]aresample={RATE},aformat=sample_fmts=fltp:channel_layouts=stereo,"
                          f"atrim=duration={d:.9f},apad=whole_dur={d:.9f},asetpts=PTS-STARTPTS[a{i}]")
        else:
            inputs += ["-f", "lavfi", "-t", f"{d:.9f}", "-i", f"anullsrc=r={RATE}:cl=stereo"]
            chains.append(f"[{i}:a:0]aformat=sample_fmts=fltp:channel_layouts=stereo,"
                          f"atrim=duration={d:.9f},asetpts=PTS-STARTPTS[a{i}]")
    chains.append("".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[out]")
    ffmpeg(*inputs, "-filter_complex", ";".join(chains), "-map", "[out]", "-ar", str(RATE), "-ac", "2",
           "-c:a", "pcm_f32le", out)


def music_cues(segs, resolve, total: float) -> dict:
    base = json.loads((REPO / "film/music/cues.json").read_text(encoding="utf-8"))
    targets = {s["name"]: s for s in base.get("sections", [])}
    sections = []
    for s in segs:
        name = (s["spec"].get("music") or {}).get("section", s["name"])
        row = {"name": name, "start": round(s["start"], 6), "end": round(s["start"] + s["duration"], 6),
               "lufs": float(targets.get(name, {}).get("lufs", -25.0))}
        chord = (s["spec"].get("music") or {}).get("closing_chord_at")
        if chord is not None:
            row["closing_chord_at"] = round(s["start"] + min(float(chord), 0.57 * s["duration"]), 6)
        sections.append(row)
    # merge sections too short for the bed's crossfades (draft slates) into a neighbour
    merged = []
    for row in sections:
        if merged and row["end"] - row["start"] < MIN_MUSIC_SECTION:
            merged[-1]["end"] = row["end"]
        elif merged and merged[-1]["end"] - merged[-1]["start"] < MIN_MUSIC_SECTION:
            row["start"] = merged[-1]["start"]
            merged[-1] = row
        else:
            merged.append(row)
    if len(merged) > 1 and merged[-1]["end"] - merged[-1]["start"] < MIN_MUSIC_SECTION:
        merged[-2]["end"] = merged.pop()["end"]
    for row in merged:
        c = row.get("closing_chord_at")
        if c is not None and not row["start"] < c < row["end"]:
            row.pop("closing_chord_at")
        if row["name"] not in targets:
            warn(f"music: no section '{row['name']}' in film/music/cues.json; using {row['lufs']} LUFS")
    if len(merged) < len(sections):
        warn(f"music: {len(sections) - len(merged)} short section(s) merged for the bed "
             f"(anything under {MIN_MUSIC_SECTION:g} s)")
    windows = []
    for s in segs:
        s["tts"] = tts_windows(s, resolve)
        for a, b in s["tts"]:
            windows.append({"start": round(s["start"] + a, 3), "end": round(s["start"] + b, 3), "note": s["name"]})
    cues = {k: v for k, v in base.items() if k not in ("sections", "tts_windows")}
    cues.update(sections=merged, tts_windows=windows)
    merged[-1]["end"] = round(total, 6)
    return cues


def make_music(cues: dict, work: Path, dx: Path, reuse: bool, draft: bool) -> Path | None:
    cue_path = work / "cues_film.json"
    cue_path.write_text(json.dumps(cues, indent=2) + "\n", encoding="utf-8")
    bed, ducked = work / "bed.wav", work / "bed_ducked.wav"
    maker = REPO / "film/music/make_bed.py"
    if not maker.is_file():
        warn("film/music/make_bed.py not found: no music bed")
        return None
    try:
        if not (reuse and bed.is_file()):
            print("music: rendering the bed (about 1.5 min for the full film)")
            run([sys.executable, maker, "--cues", cue_path, "--output", bed])
        dx16 = work / "dx_16bit.wav"
        ffmpeg("-i", dx, "-c:a", "pcm_s16le", "-ar", str(RATE), "-ac", "2", dx16)
        run([sys.executable, REPO / "film/music/duck.py", "--bed", bed, "--dialogue", dx16,
             "--cues", cue_path, "--out", ducked])
        return ducked
    except RuntimeError as exc:
        if not draft:
            raise
        warn(f"music failed in draft mode, continuing without it: {str(exc)[:300]}")
        return None


def master(raw: Path, out: Path) -> tuple[float, str, dict]:
    first = loudness(raw)
    if first["integrated_lufs"] < -70:
        warn("mix is silent; no mastering gain applied")
        ffmpeg("-i", raw, "-c:a", "pcm_s24le", out)
        return 0.0, "silent", first
    gain = TARGET_I - first["integrated_lufs"]
    if first["true_peak_dbtp"] + gain > TARGET_TP:
        ffmpeg("-i", raw, "-af", f"volume={gain:.6f}dB,alimiter=limit={10 ** (TARGET_TP / 20):.4f}:attack=2:release=50:level=false",
               "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s24le", out)
        return gain, "linear_gain_plus_limiter", first
    ffmpeg("-i", raw, "-af", f"volume={gain:.6f}dB", "-c:a", "pcm_s24le", out)
    return gain, "linear_gain", first


def mux(video: Path, audio: Path, out: Path, total: float) -> None:
    ffmpeg("-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
           "-b:a", "256k", "-ar", str(RATE), "-ac", "2", "-t", f"{total:.9f}", "-movflags", "+faststart", out)


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--segments", type=Path, default=REPO / "film/final/v3_segments.json")
    ap.add_argument("--draft", action="store_true", help="slates for missing segments, faster encode, _draft names")
    ap.add_argument("--renders-dir", type=Path, help="override renders_dir (tests)")
    ap.add_argument("--reuse-bed", action="store_true", help="reuse the work folder's bed.wav (same cue sheet only)")
    ap.add_argument("--bed-trim-db", type=float, help="fixed bed trim instead of matching the dialogue level")
    ap.add_argument("--no-qc", action="store_true")
    args = ap.parse_args()

    cfg = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
    root = (args.renders_dir or Path(cfg["renders_dir"])).resolve()
    tag = "full_film_v3" + ("_draft" if args.draft else "")
    work = root / f"{tag}_work"
    stems_dir = root / f"{tag}_stems"
    work.mkdir(parents=True, exist_ok=True)
    stems_dir.mkdir(parents=True, exist_ok=True)

    def resolve(ref):
        if not ref or ref == "embedded":
            return None
        if not ref.startswith("RENDERS:"):
            raise ValueError(f"paths must start with RENDERS: ({ref})")
        return root / ref[len("RENDERS:"):]

    def rel(p: Path) -> str:
        return "RENDERS:" + p.resolve().relative_to(root).as_posix()

    segs = load_segments(args.segments, resolve, args.draft, work)
    total_frames = sum(s["frames"] for s in segs)
    total = total_frames / FPS
    for s in segs:
        print(f"{s['name']:<9} start {s['start']:8.3f}  {s['duration']:7.3f} s  {s['frames']:5d} frames"
              f"{'  [SLATE]' if s['slate'] else ''}")
    print(f"film: {total:.3f} s, {total_frames} frames")

    picture = work / "picture.mp4"
    method = make_picture(segs, picture, args.draft)
    dx_raw, sfx_raw = work / "dx_raw.wav", work / "sfx_raw.wav"
    make_stem(segs, "dx", dx_raw)
    make_stem(segs, "sfx", sfx_raw)

    cues = music_cues(segs, resolve, total)
    bed = make_music(cues, work, dx_raw, args.reuse_bed, args.draft)

    dx_loud = loudness(dx_raw)
    if args.bed_trim_db is not None:
        trim = args.bed_trim_db
    elif dx_loud["integrated_lufs"] > -70:
        trim = max(-10.0, min(10.0, dx_loud["integrated_lufs"] - DIALOGUE_REF))
    else:
        trim = 0.0
    music_raw = work / "music_raw.wav"
    if bed:
        ffmpeg("-i", bed, "-af", f"volume={trim:.4f}dB,apad=whole_dur={total:.9f},atrim=duration={total:.9f}",
               "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_f32le", music_raw)
    else:
        ffmpeg("-f", "lavfi", "-t", f"{total:.9f}", "-i", f"anullsrc=r={RATE}:cl=stereo", "-c:a", "pcm_f32le", music_raw)

    def mix(inputs, out):
        args_ = [x for p in inputs for x in ("-i", p)]
        ffmpeg(*args_, "-filter_complex", "".join(f"[{i}:a]" for i in range(len(inputs))) +
               f"amix=inputs={len(inputs)}:normalize=0:duration=first[out]", "-map", "[out]",
               "-c:a", "pcm_f32le", out)

    mix_raw, nomusic_raw = work / "mix_raw.wav", work / "nomusic_raw.wav"
    mix([dx_raw, sfx_raw, music_raw], mix_raw)
    mix([dx_raw, sfx_raw], nomusic_raw)
    mix_master = work / "mix_master.wav"
    gain, method_audio, first = master(mix_raw, mix_master)

    # stems and the no-music mix carry exactly the same master gain, so they line up with the mix
    limiter = f",alimiter=limit={10 ** (TARGET_TP / 20):.4f}:attack=2:release=50:level=false"
    for src, name in ((dx_raw, "dx"), (sfx_raw, "sfx"), (music_raw, "music")):
        ffmpeg("-i", src, "-af", f"volume={gain:.6f}dB", "-c:a", "pcm_s24le", stems_dir / f"{name}.wav")
    nomusic_master = work / "nomusic_master.wav"
    ffmpeg("-i", nomusic_raw, "-af", f"volume={gain:.6f}dB" + limiter, "-c:a", "pcm_s24le", nomusic_master)

    film, nomusic = root / f"{tag}.mp4", root / f"{tag}_nomusic.mp4"
    mux(picture, mix_master, film, total)
    mux(picture, nomusic_master, nomusic, total)
    checks = {}
    for p in (film, nomusic):
        pr = probe(p)
        frames = int(pr["video"].get("nb_read_packets", 0))
        ad = float(pr["audio"].get("duration") or pr["duration"])
        checks[p.name] = {"frames": frames, "audio_duration": round(ad, 3)}
        if frames != total_frames:
            raise RuntimeError(f"{p.name}: {frames} frames, expected {total_frames}")
        if abs(ad - total) > 0.05:
            raise RuntimeError(f"{p.name}: audio {ad:.3f} s vs picture {total:.3f} s")
    final = loudness(film)
    ok = abs(final["integrated_lufs"] - TARGET_I) <= 0.5 and final["true_peak_dbtp"] <= -1.5
    if not ok and first["integrated_lufs"] > -70:
        msg = f"encoded film is {final['integrated_lufs']} LUFS / {final['true_peak_dbtp']} dBTP"
        if not args.draft:
            raise RuntimeError(msg + " (target -16 +/-0.5 LUFS, <= -1.5 dBTP)")
        warn(msg)

    report = {
        "draft": args.draft, "total_seconds": round(total, 6), "total_frames": total_frames,
        "video_assembly": method,
        "segments": [{"name": s["name"], "start": round(s["start"], 6), "end": round(s["start"] + s["duration"], 6),
                      "duration": round(s["duration"], 6), "frames": s["frames"], "slate": s["slate"],
                      "source": "slate" if s["slate"] else s["spec"]["video"],
                      "dx": "embedded" if (s["stems"].get("dx") or (None, False))[1] else
                            (rel(s["stems"]["dx"][0]) if s["stems"].get("dx") else None),
                      "sfx": rel(s["stems"]["sfx"][0]) if s["stems"].get("sfx") else None,
                      "tts_windows": s.get("tts", [])} for s in segs],
        "music": {"cue_sheet": rel(work / "cues_film.json"), "sections": cues["sections"],
                  "tts_windows": cues["tts_windows"], "bed": bool(bed), "bed_trim_db": round(trim, 2)},
        "loudness": {"dialogue_stem": dx_loud, "mix_before_master": first, "master_gain_db": round(gain, 3),
                     "master_method": method_audio, "encoded_film": final,
                     "stems": {n: loudness(stems_dir / f"{n}.wav") for n in ("dx", "sfx", "music")}},
        "checks": checks,
        "outputs": [rel(film), rel(nomusic)] + [rel(stems_dir / f"{n}.wav") for n in ("dx", "sfx", "music")],
        "warnings": WARNINGS,
    }
    report_path = root / f"{tag}_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"done: {rel(film)}  {total:.3f} s, {final['integrated_lufs']} LUFS, {final['true_peak_dbtp']} dBTP, "
          f"video {method}, audio {method_audio}")
    print(f"report: {rel(report_path)}  ({len(WARNINGS)} warning(s))")
    for p in (dx_raw, sfx_raw, music_raw, mix_raw, nomusic_raw, work / "dx_16bit.wav"):
        p.unlink(missing_ok=True)
    if not args.no_qc:
        qc_args = [sys.executable, REPO / "film/final/qc.py", "--v3", film, "--segments-report", report_path,
                   "--report", root / f"{tag}_qc.json", "--contact", root / f"{tag}_contact.jpg"]
        r = subprocess.run([str(a) for a in qc_args])
        print(f"QC exit code {r.returncode} (report {rel(root / f'{tag}_qc.json')})")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f"assemble_v3.py: {exc}", file=sys.stderr)
        sys.exit(1)
