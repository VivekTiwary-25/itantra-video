#!/usr/bin/env python3
"""Assemble the approved four-scene film from local render stems.

Run from the repository root: python film/final/assemble.py
The optional --renders-dir is useful for an isolated synthetic test.
"""

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path


# Paths relative to machine.local.json's renders_dir. Change these if render names change.
SCENES = (
    ("scene1", "scene1/scene1_draft_v3.mp4", None, None),
    ("scene2", "scene2/scene2_draft_nomusic.mp4", "scene2/scene2_dialogue_sfx.wav", "scene2/scene2_music.wav"),
    ("scene3", "scene3/scene3_draft.mp4", "scene3/scene3_dialogue_sfx.wav", "scene3/scene3_music.wav"),
    ("title", "title/title.mp4", None, None),
)
FPS = 30
RATE = 48000
TARGET_I = -16.0
TARGET_TP = -1.8  # Leave a little margin for AAC; final export must remain <= -1.5 dBTP.


def run(args, *, capture=False):
    result = subprocess.run([str(a) for a in args], text=True, encoding="utf-8",
                            errors="replace", capture_output=True)
    if result.returncode:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(map(str, args[:5]))}\n{detail[-5000:]}")
    return result if capture else None


def probe(path, *, count_frames=False):
    args = ["ffprobe", "-v", "error", "-of", "json", "-show_format", "-show_streams",
            "-show_data_hash", "sha256"]
    if count_frames:
        args.append("-count_frames")
    args.append(path)
    return json.loads(run(args, capture=True).stdout)


def rate(value):
    n, d = map(int, value.split("/"))
    return n / d


def media_duration(info, stream):
    return float(stream.get("duration") or info["format"]["duration"])


def loudnorm(path, *, output=None, values=None):
    filt = f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA=11"
    if values:
        filt += (f":measured_I={values['input_i']}:measured_TP={values['input_tp']}"
                 f":measured_LRA={values['input_lra']}:measured_thresh={values['input_thresh']}"
                 f":offset={values['target_offset']}:linear=true")
    filt += ":print_format=json"
    args = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", path, "-vn", "-af", filt]
    if output:
        args += ["-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s24le", output]
    else:
        args += ["-f", "null", "-"]
    log = run(args, capture=True).stderr
    matches = re.findall(r"\{\s*\"input_i\".*?\}", log, re.DOTALL)
    if not matches:
        raise RuntimeError("Could not parse loudnorm measurements.\n" + log[-3000:])
    return json.loads(matches[-1])


def make_stem(paths, durations, output, music):
    inputs = []
    filters = []
    for i, (video, dialogue, tune) in enumerate(paths):
        source = tune if music else (dialogue or video)
        if source:
            inputs += ["-i", source]
            filters.append(
                f"[{i}:a:0]aresample={RATE},aformat=channel_layouts=stereo,"
                f"atrim=duration={durations[i]:.9f},apad,"
                f"atrim=duration={durations[i]:.9f},asetpts=PTS-STARTPTS[a{i}]"
            )
        else:
            inputs += ["-f", "lavfi", "-i", f"anullsrc=r={RATE}:cl=stereo"]
            filters.append(f"[{i}:a:0]atrim=duration={durations[i]:.9f},asetpts=PTS-STARTPTS[a{i}]")
    filters.append("".join(f"[a{i}]" for i in range(len(paths))) +
                   f"concat=n={len(paths)}:v=0:a=1[out]")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", *inputs,
         "-filter_complex", ";".join(filters), "-map", "[out]", "-c:a", "pcm_s24le", output])


def video_signature(v):
    fields = ("codec_name", "profile", "level", "pix_fmt", "sample_aspect_ratio",
              "field_order", "color_range", "color_space", "color_transfer",
              "color_primaries", "time_base", "extradata_hash")
    return tuple(v.get(k) for k in fields)


def make_video(paths, streams, frames, output):
    videos = [p[0] for p in paths]
    can_copy = (all(s["codec_name"] == "h264" for s in streams) and
                len({video_signature(s) for s in streams}) == 1)
    if can_copy:
        # The concat list lives beside the output, and holds only local, transient paths.
        listing = output.with_suffix(".concat.txt")
        listing.write_text("".join(
            "file '" + str(p.resolve()).replace("'", "'\\''").replace("\\", "/") +
            f"'\nduration {n / FPS:.9f}\n" for p, n in zip(videos, frames)
        ), encoding="utf-8")
        try:
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-f", "concat",
                 "-safe", "0", "-i", listing, "-map", "0:v:0", "-an", "-c:v", "copy", output])
            info = probe(output, count_frames=True)
            outv = next(s for s in info["streams"] if s["codec_type"] == "video")
            if int(outv["nb_read_frames"]) == sum(frames) and abs(media_duration(info, outv) - sum(frames) / FPS) < 1 / FPS:
                return "stream_copy"
            print("Stream copy did not preserve exact frame count/timing; encoding once instead.")
            output.unlink()
        finally:
            listing.unlink(missing_ok=True)
    inputs = [x for p in videos for x in ("-i", p)]
    filters = [f"[{i}:v:0]setpts=PTS-STARTPTS,setsar=1[v{i}]" for i in range(len(videos))]
    filters.append("".join(f"[v{i}]" for i in range(len(videos))) +
                   f"concat=n={len(videos)}:v=1:a=0,format=yuv420p[out]")
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", *inputs,
         "-filter_complex", ";".join(filters), "-map", "[out]", "-an",
         "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
         "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", output])
    return "libx264_crf16"


def mux(video, audio, output, duration):
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
         "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", str(RATE),
         "-ac", "2", "-t", f"{duration:.9f}", "-movflags", "+faststart", output])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renders-dir", type=Path, help="override local renders folder for testing")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    config = json.loads((repo / "machine.local.json").read_text(encoding="utf-8"))
    root = args.renders_dir or Path(config["renders_dir"])
    root.mkdir(parents=True, exist_ok=True)
    paths = [(root / v, root / d if d else None, root / m if m else None)
             for _, v, d, m in SCENES]
    missing = [str(p.relative_to(root)) for group in paths for p in group if p and not p.is_file()]
    if missing:
        raise ValueError("Missing required inputs under renders_dir:\n  " + "\n  ".join(missing))

    frames, streams, scene_report = [], [], []
    start_frame = 0
    for (name, *_), (video, dialogue, music) in zip(SCENES, paths):
        info = probe(video, count_frames=True)
        vs = [s for s in info["streams"] if s["codec_type"] == "video"]
        if len(vs) != 1:
            raise ValueError(f"{name}: expected exactly one video stream")
        v = vs[0]
        fps = rate(v["avg_frame_rate"])
        nominal_fps = rate(v["r_frame_rate"])
        if ((v["width"], v["height"]) != (1920, 1080)
                or not math.isclose(fps, FPS, abs_tol=0.001)
                or not math.isclose(nominal_fps, FPS, abs_tol=0.001)):
            raise ValueError(f"{name}: expected 1920x1080 at 30 fps; got {v['width']}x{v['height']} at {fps:g} average / {nominal_fps:g} nominal fps")
        count = int(v["nb_read_frames"])
        if count < 1:
            raise ValueError(f"{name}: video has no frames")
        if abs(media_duration(info, v) - count / FPS) > 1 / FPS + 0.001:
            raise ValueError(f"{name}: frame count and stream duration disagree; constant 30 fps is required")
        if (dialogue is None and not any(s["codec_type"] == "audio" for s in info["streams"])):
            raise ValueError(f"{name}: video needs embedded audio")
        for label, path in (("dialogue_sfx", dialogue), ("music", music)):
            if path and not any(s["codec_type"] == "audio" for s in probe(path)["streams"]):
                raise ValueError(f"{name}: {label} has no audio stream")
        duration = count / FPS
        scene_report.append({"scene": name, "start_seconds": round(start_frame / FPS, 6),
                             "end_seconds": round((start_frame + count) / FPS, 6),
                             "duration_seconds": round(duration, 6), "frames": count,
                             "source_video_duration_seconds": round(media_duration(info, v), 6),
                             "resolution": "1920x1080", "fps": fps})
        print(f"{name}: {count} frames, {duration:.3f}s; source {media_duration(info, v):.3f}s, 1920x1080, {fps:g} fps")
        for label, path in (("dialogue_sfx", dialogue), ("music", music)):
            if path:
                print(f"  {label}: {float(probe(path)['format']['duration']):.3f}s")
        frames.append(count)
        streams.append(v)
        start_frame += count

    total = sum(frames) / FPS
    dialogue = root / "full_film_v1_dialogue_sfx.wav"
    music = root / "full_film_v1_music_only.wav"
    raw_dialogue = root / "full_film_v1_dialogue_raw.tmp.wav"
    raw_music = root / "full_film_v1_music_raw.tmp.wav"
    raw_mix = root / "full_film_v1_mix_raw.tmp.wav"
    mix = root / "full_film_v1_mix.wav"
    temp_video = root / "full_film_v1_video.tmp.mp4"
    method = make_video(paths, streams, frames, temp_video)
    make_stem(paths, [n / FPS for n in frames], raw_dialogue, False)
    make_stem(paths, [n / FPS for n in frames], raw_music, True)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-i", raw_dialogue,
         "-i", raw_music, "-filter_complex", "[0:a][1:a]amix=inputs=2:normalize=0:duration=first[out]",
         "-map", "[out]", "-c:a", "pcm_s24le", raw_mix])
    first_pass = loudnorm(raw_mix)
    second_pass = loudnorm(raw_mix, output=mix, values=first_pass)
    if second_pass.get("normalization_type") != "linear":
        raise ValueError("Mix cannot meet -16 LUFS and -1.5 dBTP with linear loudnorm; inspect the input peaks.")
    gain = float(second_pass["output_i"]) - float(second_pass["input_i"])
    for source, destination in ((raw_dialogue, dialogue), (raw_music, music)):
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-i", source,
             "-af", f"volume={gain:.6f}dB", "-c:a", "pcm_s24le", destination])
    # Confirm that the applied dialogue gain matches the measured linear mix gain.
    raw_dialogue_loudness = loudnorm(raw_dialogue)
    normalized_dialogue_loudness = loudnorm(dialogue)
    actual_gain = float(normalized_dialogue_loudness["input_i"]) - float(raw_dialogue_loudness["input_i"])
    if abs(actual_gain - gain) > 0.15:
        raise RuntimeError(f"Dialogue gain check failed: requested {gain:.2f} dB, observed {actual_gain:.2f} dB")
    with_music = root / "full_film_v1.mp4"
    no_music = root / "full_film_v1_nomusic.mp4"
    mux(temp_video, mix, with_music, total)
    mux(temp_video, dialogue, no_music, total)
    for path in (with_music, no_music):
        data = probe(path, count_frames=True)
        video = next(s for s in data["streams"] if s["codec_type"] == "video")
        if int(video["nb_read_frames"]) != sum(frames):
            raise RuntimeError(f"Frame count mismatch in {path.name}")
        if abs(float(data["format"]["duration"]) - total) > 0.04:
            raise RuntimeError(f"Duration mismatch in {path.name}")
    music_duration = float(probe(music)["format"]["duration"])
    if abs(music_duration - total) > 1 / RATE:
        raise RuntimeError("Music-only duration differs from picture timeline")
    final_loudness = loudnorm(with_music)
    if abs(float(final_loudness["input_i"]) - TARGET_I) > 0.3 or float(final_loudness["input_tp"]) > -1.5:
        raise RuntimeError("Encoded film missed -16 LUFS +/-0.3 or -1.5 dBTP; inspect final AAC loudness")
    for i in range(len(scene_report) - 1):
        left, right = scene_report[i:i + 2]
        print(f"Boundary {left['scene']} -> {right['scene']}: last frame {left['end_seconds'] - 1/FPS:.6f}s; first next frame {right['start_seconds']:.6f}s")
    report = {"total_duration_seconds": round(total, 6), "total_frames": sum(frames),
              "video_assembly": method, "scenes": scene_report,
              "loudness": {"mix_first_pass": first_pass, "mix_second_pass": second_pass,
                           "encoded_film": final_loudness,
                           "dialogue_gain_db": round(gain, 6),
                           "dialogue_before": raw_dialogue_loudness,
                           "dialogue_after": normalized_dialogue_loudness},
              "outputs": [p.name for p in (with_music, no_music, music, dialogue, mix)]}
    (root / "full_film_v1_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for temp in (raw_mix, raw_dialogue, raw_music, temp_video):
        temp.unlink(missing_ok=True)
    print(f"Done: {total:.3f}s; mix {second_pass['output_i']} LUFS, {second_pass['output_tp']} dBTP; video {method}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f"assemble.py: {exc}", file=sys.stderr)
        sys.exit(1)
