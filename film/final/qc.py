#!/usr/bin/env python3
"""Measured quality check for iTantra scene and final renders.

Usage: python film/final/qc.py VIDEO [--report REPORT.json]
       python film/final/qc.py --v3 VIDEO --segments-report full_film_v3_report.json [--report QC.json]
                               [--contact SHEET.jpg] [--contact-small SHEET_960.jpg]
Requires ffmpeg and ffprobe on PATH. No third-party Python packages.
"""

import argparse
import array
import json
import math
import re
import subprocess
import sys
import threading
from pathlib import Path


FPS = 30.0
SAMPLE_RATE = 48000
FRAME_W, FRAME_H = 64, 36
PHONE_W, PHONE_H = 243, 540


MAX_BLACK_S = 1.0


def command(args):
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"{' '.join(args[:3])} exited {result.returncode}: {result.stderr[-2000:]}")
    return result


def stream_bytes(args, item_size, visit, *, allow_partial=False):
    """Drain stderr concurrently so a long diagnostic stream cannot block stdout."""
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    errors = bytearray()

    def drain():
        while True:
            block = proc.stderr.read(65536)
            if not block:
                break
            errors.extend(block)

    thread = threading.Thread(target=drain, daemon=True)
    thread.start()
    count = 0
    try:
        while True:
            chunk = proc.stdout.read(item_size)
            if not chunk:
                break
            if len(chunk) != item_size and not allow_partial:
                raise RuntimeError("Truncated decoded frame or audio block")
            visit(chunk, count)
            count += 1
    finally:
        proc.stdout.close()
        thread.join()
    if proc.wait():
        raise RuntimeError(errors.decode("utf-8", "replace")[-2000:])
    return count, errors.decode("utf-8", "replace")


def ratio(value):
    a, b = value.split("/")
    return float(a) / float(b) if float(b) else None


def probe(path):
    info = json.loads(command(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]).stdout)
    videos = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    audios = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    return info, videos, audios


def issue(issues, name, observed, expected, fail=True):
    issues.append({"status": "FAIL" if fail else "INFO", "check": name,
                   "observed": observed, "expected": expected})


def parse_intervals(log, pattern, duration):
    starts = []
    rows = []
    # ffmpeg 7+ prints blackdetect's start and end on ONE line, so read every match on a line, not just the first
    for match in (m for line in log.splitlines() for m in re.finditer(pattern, line)):
        kind, val = match.groups()
        if kind.endswith("start"):
            starts.append(float(val))
        elif kind.endswith("end"):
            start = starts.pop(0) if starts else 0.0
            rows.append({"start": round(start, 3), "end": round(float(val), 3),
                         "duration": round(float(val) - start, 3)})
    for start in starts:
        rows.append({"start": round(start, 3), "end": round(duration, 3),
                     "duration": round(duration - start, 3)})
    return rows


def picture(path, duration, freeze_d=1.0):
    flat = []
    active = None

    def visit(frame, number):
        nonlocal active
        # A solid frame remains solid when area-scaled. Allow two RGB code values
        # for rounding, but require *each* channel to be spatially constant.
        solid = all(max(frame[c::3]) - min(frame[c::3]) <= 2 for c in range(3))
        if solid and active is None:
            active = number
        if not solid and active is not None:
            flat.append({"start": round(active / FPS, 3), "end": round(number / FPS, 3),
                         "frames": number - active})
            active = None

    # pic_th=1.0: a frame counts as black only if EVERY pixel is below pix_th. The sonar sections are mostly
    # black with thin luminous lines and points, which a 99 % rule wrongly reported as black (claude-second, T0027).
    vf = ("blackdetect=d=0:pix_th=0.02:pic_th=1.0,"
          f"freezedetect=n=-60dB:d={freeze_d},vfrdet,"
          f"scale={FRAME_W}:{FRAME_H}:flags=area,format=rgb24")
    count, log = stream_bytes(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path),
                               "-map", "0:v:0", "-an", "-vf", vf, "-fps_mode", "passthrough",
                               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                              FRAME_W * FRAME_H * 3, visit)
    if active is not None:
        flat.append({"start": round(active / FPS, 3), "end": round(count / FPS, 3),
                     "frames": count - active})
    black = parse_intervals(log, r"black_(start|end):\s*(-?[\d.]+)", duration)
    frozen = parse_intervals(log, r"freeze_(start|end):\s*(-?[\d.]+)", duration)
    vfr = re.search(r"VFR:\s*([\d.]+)\s*\((\d+)/(\d+)\)", log)
    return {"decoded_frames": count, "black": black, "frozen": frozen,
            "flat": flat, "vfr_ratio": float(vfr.group(1)) if vfr else None,
            "vfr_changed_frames": int(vfr.group(2)) if vfr else None}


def near(rgb, target, tolerance=18):
    return all(abs(a - b) <= tolerance for a, b in zip(rgb, target))


def placeholder(path):
    hits = []
    details = []
    background = (11, 16, 24)  # .placeholder #0b1018
    text = (138, 147, 158)    # .placeholder #8a939e

    def visit(frame, number):
        # Crop is exactly .screen in scene2/main/index.html.tpl, sampled at 1 fps.
        # A real card has the fixed background across the portrait panel and a
        # narrow grey glyph band near its centre. No OCR or text dependency.
        bg = 0
        text_center = 0
        text_outside = 0
        for y in range(30, PHONE_H - 30, 3):
            for x in range(20, PHONE_W - 20, 3):
                offset = (y * PHONE_W + x) * 3
                rgb = frame[offset:offset + 3]
                if near(rgb, background, 14):
                    bg += 1
                if near(rgb, text, 24):
                    if 235 <= y <= 305 and 25 <= x <= 218:
                        text_center += 1
                    else:
                        text_outside += 1
        total = len(range(30, PHONE_H - 30, 3)) * len(range(20, PHONE_W - 20, 3))
        bg_share = bg / total
        found = bg_share > 0.98 and text_center >= 8 and text_center > 3 * text_outside
        if found:
            hits.append(number)
        details.append({"second": number, "background_share": round(bg_share, 3),
                        "center_grey_pixels": text_center, "match": found})

    count, _ = stream_bytes(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-i", str(path),
                             "-map", "0:v:0", "-an", "-vf",
                             f"fps=1,scale=1920:1080,crop=486:1080:717:0,scale={PHONE_W}:{PHONE_H}:flags=area,format=rgb24",
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                            PHONE_W * PHONE_H * 3, visit)
    return {"sampled_seconds": count, "placeholder_seconds": hits, "samples": details}


def loudness(path):
    log = command(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-vn",
                   "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
                   "-f", "null", "-"]).stderr
    found = re.findall(r"\{\s*\"input_i\".*?\}", log, re.S)
    if not found:
        raise RuntimeError("Could not read loudnorm measurements")
    data = json.loads(found[-1])
    # ebur128's S is a rolling 3 s loudness. Report its median and range in
    # each non-overlapping 10 s interval, so local level changes are visible.
    log = command(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-vn",
                   "-af", "ebur128=framelog=info", "-f", "null", "-"]).stderr
    buckets = {}
    for t, s in re.findall(r"t:\s*([\d.]+).*?S:\s*(-?(?:\d+(?:\.\d+)?|inf))", log):
        if float(t) < 3.0:  # ebur128 has no full short-term window yet
            continue
        value = float(s)
        if math.isfinite(value):
            buckets.setdefault(int(float(t) // 10), []).append(value)
    windows = []
    for index, vals in sorted(buckets.items()):
        ordered = sorted(vals)
        windows.append({"start": index * 10, "end": (index + 1) * 10,
                        "median_short_term_lufs": round(ordered[len(ordered) // 2], 2),
                        "min_short_term_lufs": round(ordered[0], 2),
                        "max_short_term_lufs": round(ordered[-1], 2)})
    return {"integrated_lufs": float(data["input_i"]),
            "true_peak_dbtp": float(data["input_tp"]), "windows_10s": windows}


def audio_scan(path, duration):
    samples = 0
    clipped = 0
    sum_l = sum_r = 0.0

    def visit(block, _):
        nonlocal samples, clipped, sum_l, sum_r
        values = array.array("f")
        values.frombytes(block)
        if sys.byteorder != "little":
            values.byteswap()
        for pos in range(0, len(values), 2):
            left, right = values[pos], values[pos + 1]
            sum_l += left * left
            sum_r += right * right
            clipped += (abs(left) >= 0.999999) + (abs(right) >= 0.999999)
            samples += 1

    # 4096 interleaved stereo float sample pairs per read.
    _, _ = stream_bytes(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-i", str(path),
                         "-map", "0:a:0", "-vn", "-ac", "2", "-ar", str(SAMPLE_RATE),
                         "-f", "f32le", "-acodec", "pcm_f32le", "-"], 4096 * 2 * 4, visit,
                        allow_partial=True)
    rms_l = math.sqrt(sum_l / samples) if samples else 0
    rms_r = math.sqrt(sum_r / samples) if samples else 0
    gap = abs(20 * math.log10(max(rms_l, 1e-12) / max(rms_r, 1e-12)))
    log = command(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-vn",
                   "-af", "silencedetect=noise=-50dB:d=1.5", "-f", "null", "-"]).stderr
    silence = parse_intervals(log, r"silence_(start|end):\s*(-?[\d.]+)", duration)
    return {"decoded_sample_pairs": samples, "full_scale_samples": clipped,
            "left_rms_dbfs": round(20 * math.log10(max(rms_l, 1e-12)), 2),
            "right_rms_dbfs": round(20 * math.log10(max(rms_r, 1e-12)), 2),
            "channel_gap_db": round(gap, 2), "silence": silence}


def check(path):
    info, videos, audios = probe(path)
    issues = []
    if len(videos) != 1 or len(audios) != 1:
        issue(issues, "streams", f"{len(videos)} video / {len(audios)} audio", "1 video / 1 audio")
    if not videos or not audios:
        return {"video": path.name, "status": "FAIL", "checks": issues}
    v, a = videos[0], audios[0]
    vd = float(v.get("duration") or info["format"]["duration"])
    ad = float(a.get("duration") or info["format"]["duration"])
    media = {"container": info["format"].get("format_name"), "video_codec": v.get("codec_name"),
             "width": v.get("width"), "height": v.get("height"), "pixel_format": v.get("pix_fmt"),
             "frame_rate": v.get("avg_frame_rate"), "nominal_frame_rate": v.get("r_frame_rate"),
             "video_duration": vd, "audio_codec": a.get("codec_name"),
             "audio_sample_rate": a.get("sample_rate"), "audio_channels": a.get("channels"),
             "audio_layout": a.get("channel_layout"), "audio_duration": ad}
    requirements = [
        ("container", "mp4" in media["container"] or "mov" in media["container"], media["container"], "MP4/MOV"),
        ("dimensions", (v.get("width"), v.get("height")) == (1920, 1080),
         f"{v.get('width')}x{v.get('height')}", "1920x1080"),
        ("video codec", v.get("codec_name") == "h264", v.get("codec_name"), "H.264"),
        ("pixel format", v.get("pix_fmt") == "yuv420p", v.get("pix_fmt"), "yuv420p"),
        ("frame rate", math.isclose(ratio(v.get("avg_frame_rate", "0/1")) or 0, FPS, abs_tol=0.01)
         and ratio(v.get("r_frame_rate", "0/1")) == FPS,
         f"{v.get('avg_frame_rate')} / {v.get('r_frame_rate')}", "30/1 constant"),
        ("audio codec", a.get("codec_name") == "aac", a.get("codec_name"), "AAC"),
        ("sample rate", int(a.get("sample_rate", 0)) == SAMPLE_RATE, a.get("sample_rate"), "48000 Hz"),
        ("channels", a.get("channels") == 2, a.get("channels"), "stereo"),
        ("stream durations", abs(vd - ad) <= 0.050, round(abs(vd - ad), 3), "<= 0.050 s apart"),
    ]
    for name, ok, observed, expected in requirements:
        issue(issues, name, observed, expected, not ok)
    picture_data = picture(path, vd)
    issue(issues, "variable frame timing", picture_data["vfr_ratio"], "0 changed intervals",
          picture_data["vfr_ratio"] is None or picture_data["vfr_changed_frames"] > 0)
    # Short black/flat runs are intended fades (e.g. sonar_a opens from black); only runs of 1 s or more fail.
    long_black = [x for x in picture_data["black"] if x["duration"] >= MAX_BLACK_S]
    long_flat = [x for x in picture_data["flat"] if x["frames"] / FPS >= MAX_BLACK_S]
    issue(issues, "black frames", picture_data["black"], f"none >= {MAX_BLACK_S} s", bool(long_black))
    issue(issues, "flat colour frames", picture_data["flat"], f"none >= {MAX_BLACK_S} s", bool(long_flat))
    issue(issues, "frozen holds >1 s", picture_data["frozen"], "review intended holds", False)
    place_data = placeholder(path)
    issue(issues, "placeholder card", place_data["placeholder_seconds"], "none", bool(place_data["placeholder_seconds"]))
    loud = loudness(path)
    issue(issues, "integrated loudness", loud["integrated_lufs"], "-16 +/-1 LUFS",
          not -17 <= loud["integrated_lufs"] <= -15)
    issue(issues, "true peak", loud["true_peak_dbtp"], "<= -1.5 dBTP", loud["true_peak_dbtp"] > -1.5)
    loud_windows = [x for x in loud["windows_10s"] if x["median_short_term_lufs"] > -10 or x["median_short_term_lufs"] < -35]
    issue(issues, "10 s short-term level outliers", loud_windows, "median between -35 and -10 LUFS", bool(loud_windows))
    audio = audio_scan(path, ad)
    issue(issues, "full-scale samples", audio["full_scale_samples"], "0", audio["full_scale_samples"] > 0)
    issue(issues, "channel RMS mismatch", audio["channel_gap_db"], "<= 3 dB", audio["channel_gap_db"] > 3)
    issue(issues, "silence >1.5 s", audio["silence"], "none", bool(audio["silence"]))
    status = "FAIL" if any(x["status"] == "FAIL" for x in issues) else "PASS"
    return {"video": path.name, "status": status, "media": media, "picture": picture_data,
            "placeholder": place_data, "loudness": loud, "audio": audio, "checks": issues}


# ---------------------------------------------------------------- film v3 (F0018)
V3_HOLD_OK = ("cards", "exploded")  # graphic segments where a still hold is allowed; live camera never freezes
V3_FREEZE_S = 0.5


def contact_font():
    """System font for the contact-sheet time labels, found at run time (no committed absolute path)."""
    import os
    windir = os.environ.get("WINDIR")
    for cand in ([Path(windir) / "Fonts" / f for f in ("segoeui.ttf", "arial.ttf")] if windir else []) + \
            [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]:
        if cand.is_file():
            return cand.as_posix().replace(":", r"\:")
    return None


def contact_sheet(path, duration, out, small=None, every=5.0, cols=6):
    """One frame every `every` seconds, tiled, with the film time on each tile."""
    count = max(1, math.ceil(duration / every - 1e-6))  # frames at 0, 5, 10 ... < duration
    rows = math.ceil(count / cols)
    font = contact_font()
    label = (f",drawtext=fontfile='{font}':text='%{{pts\\:hms}}':x=8:y=h-th-8:fontsize=22:"
             "fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=4") if font else ""
    # select (not fps) keeps each tile's real timestamp: the frame AT 0, 5, 10 s, labelled with its own time
    pick = f"select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,{every - 0.5 / FPS})'"
    vf = f"{pick},scale=320:-2{label},tile={cols}x{rows}:padding=4:margin=4"
    command(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-i", str(path),
             "-vf", vf, "-fps_mode", "passthrough", "-frames:v", "1", "-q:v", "3", str(out)])
    if small:
        command(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-i", str(out),
                 "-vf", "scale=960:-2", "-q:v", "4", str(small)])
    return {"every_s": every, "tiles": count, "sheet": Path(out).name, "small": Path(small).name if small else None}


def segment_at(segments, t):
    for s in segments:
        if s["start"] - 1e-6 <= t < s["end"] - 1e-6:
            return s
    return segments[-1] if segments else None


def check_v3(path, seg_report, contact=None, contact_small=None):
    """Film v3 QC: per-segment freezes >= 0.5 s, black, loudness/peak, silence, A/V alignment, contact sheet."""
    info, videos, audios = probe(path)
    issues = []
    if len(videos) != 1 or len(audios) != 1:
        issue(issues, "streams", f"{len(videos)} video / {len(audios)} audio", "1 video / 1 audio")
        return {"video": path.name, "mode": "v3", "status": "FAIL", "checks": issues}
    v, a = videos[0], audios[0]
    vd = float(v.get("duration") or info["format"]["duration"])
    ad = float(a.get("duration") or info["format"]["duration"])
    segments = seg_report.get("segments", [])
    expected_total = seg_report.get("total_seconds")

    issue(issues, "format", f"{v.get('width')}x{v.get('height')} {v.get('codec_name')} {v.get('pix_fmt')} "
          f"{v.get('avg_frame_rate')} / {a.get('codec_name')} {a.get('sample_rate')} Hz {a.get('channels')} ch",
          "1920x1080 h264 yuv420p 30/1 / aac 48000 Hz 2 ch",
          not ((v.get("width"), v.get("height")) == (1920, 1080) and v.get("codec_name") == "h264"
               and v.get("pix_fmt") == "yuv420p" and math.isclose(ratio(v.get("avg_frame_rate", "0/1")) or 0, FPS, abs_tol=0.01)
               and a.get("codec_name") == "aac" and int(a.get("sample_rate", 0)) == SAMPLE_RATE and a.get("channels") == 2))
    issue(issues, "A/V alignment", round(abs(vd - ad), 3), "video and audio <= 0.050 s apart", abs(vd - ad) > 0.050)
    if expected_total is not None:
        issue(issues, "length vs assembly report", round(vd - expected_total, 3), "<= 0.050 s from report",
              abs(vd - expected_total) > 0.050)

    pic = picture(path, vd, freeze_d=V3_FREEZE_S)
    freezes = []
    for f in pic["frozen"]:
        seg = segment_at(segments, f["start"])
        name = seg["name"] if seg else "?"
        row = dict(f, segment=name, segment_start=round(f["start"] - (seg["start"] if seg else 0), 3),
                   segment_end=round(f["end"] - (seg["start"] if seg else 0), 3))
        freezes.append(row)
        allowed = seg is None or seg.get("slate") or name in V3_HOLD_OK
        issues.append({"status": "INFO" if allowed else "REVIEW",
                       "check": f"freeze >= {V3_FREEZE_S} s in {name}" + (" (slate)" if seg and seg.get("slate") else ""),
                       "observed": f"film {f['start']:.2f}-{f['end']:.2f} s = {name} {row['segment_start']:.2f}-{row['segment_end']:.2f} s",
                       "expected": "live camera never freezes: check this hold" if not allowed else "graphic hold, allowed"})
    if not freezes:
        issue(issues, f"freezes >= {V3_FREEZE_S} s", [], "none", False)

    black_fail, black_info = [], []
    for b in pic["black"]:
        end_fade = abs(b["end"] - vd) < 0.1 and b["duration"] <= 1.5
        (black_info if (b["duration"] < MAX_BLACK_S or end_fade) else black_fail).append(b)
    issue(issues, "black frames", black_fail or black_info, f"none >= {MAX_BLACK_S} s (end fade allowed)", bool(black_fail))

    loud = loudness(path)
    issue(issues, "integrated loudness", loud["integrated_lufs"], "-16 +/-1 LUFS", not -17 <= loud["integrated_lufs"] <= -15)
    issue(issues, "true peak", loud["true_peak_dbtp"], "<= -1.5 dBTP", loud["true_peak_dbtp"] > -1.5)

    audio = audio_scan(path, ad)
    issue(issues, "full-scale samples", audio["full_scale_samples"], "0", audio["full_scale_samples"] > 0)
    for s in audio["silence"]:
        seg = segment_at(segments, s["start"])
        name = seg["name"] if seg else "?"
        ok = seg is not None and (name == "cards" or seg.get("slate"))
        issues.append({"status": "INFO" if ok else "FAIL", "check": f"silence > 1.5 s in {name}",
                       "observed": f"film {s['start']:.2f}-{s['end']:.2f} s ({s['duration']:.2f} s)",
                       "expected": "INFO for cards/slates; elsewhere no silent stretch"})
    if not audio["silence"]:
        issue(issues, "silence > 1.5 s", [], "none", False)

    sheet = contact_sheet(path, vd, contact, contact_small) if contact else None
    status = "FAIL" if any(x["status"] == "FAIL" for x in issues) else (
        "REVIEW" if any(x["status"] == "REVIEW" for x in issues) else "PASS")
    return {"video": path.name, "mode": "v3", "status": status,
            "media": {"video_duration": vd, "audio_duration": ad, "frames_decoded": pic["decoded_frames"]},
            "freezes": freezes, "picture": pic, "loudness": loud, "audio": audio,
            "contact_sheet": sheet, "checks": issues}


def display(report):
    print(f"QC {report['status']}: {report['video']}")
    print(f"{'STATUS':<7} {'CHECK':<30} {'OBSERVED':<57} EXPECTED")
    print("-" * 116)
    for row in report["checks"]:
        value = json.dumps(row["observed"], ensure_ascii=False)
        if len(value) > 54:
            value = value[:51] + "..."
        print(f"{row['status']:<7} {row['check']:<30} {value:<57} {row['expected']}")
    if report.get("loudness"):
        print("\n10 s short-term loudness (median / min / max LUFS):")
        for w in report["loudness"]["windows_10s"]:
            print(f"  {w['start']:>4}-{w['end']:<4} {w['median_short_term_lufs']:>6.1f} / "
                  f"{w['min_short_term_lufs']:>6.1f} / {w['max_short_term_lufs']:>6.1f}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--report", type=Path, help="write full JSON report here")
    parser.add_argument("--v3", action="store_true", help="film v3 checks (needs --segments-report from assemble_v3.py)")
    parser.add_argument("--segments-report", type=Path, help="v3: full_film_v3_report.json written by assemble_v3.py")
    parser.add_argument("--contact", type=Path, help="v3: write a contact sheet (one frame every 5 s) here")
    parser.add_argument("--contact-small", type=Path, help="v3: 960 px wide copy of the contact sheet "
                                                            "(default: <contact>_960.jpg)")
    args = parser.parse_args()
    try:
        if args.v3:
            seg = json.loads(args.segments_report.read_text(encoding="utf-8")) if args.segments_report else {}
            small = args.contact_small or (args.contact.with_name(args.contact.stem + "_960.jpg") if args.contact else None)
            report = check_v3(args.video, seg, args.contact, small)
        else:
            report = check(args.video)
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        report = {"video": args.video.name, "status": "FAIL", "checks": [
            {"status": "FAIL", "check": "analysis", "observed": str(exc), "expected": "successful decode"}]}
    display(report)
    output = json.dumps(report, indent=2, ensure_ascii=False)
    if args.report:
        args.report.write_text(output + "\n", encoding="utf-8")
        print(f"JSON: {args.report}")
    else:
        print("\nJSON report:\n" + output)
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
