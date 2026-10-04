"""Prepare a portrait recording for a scene 3 app slot."""
import argparse
import json
import math
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
RENDERS = HERE.parents[2] / "local/renders"


def probe(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)["streams"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slot", choices=json.loads((HERE / "slots.json").read_text(encoding="utf-8")))
    parser.add_argument("raw", type=Path, help="source .mkv or .mp4 under local/renders/")
    parser.add_argument("--in", dest="start", type=float, required=True)
    parser.add_argument("--dur", type=float)
    parser.add_argument("--crop-top", type=int, default=0)
    parser.add_argument("--audio", choices=("keep", "drop"), default="keep")
    parser.add_argument("--hold-last", type=float, default=0)
    args = parser.parse_args()
    raw = args.raw.resolve()
    if not raw.is_relative_to(RENDERS.resolve()) or raw.suffix.lower() not in (".mkv", ".mp4") or not raw.is_file():
        parser.error("raw must be an existing .mkv or .mp4 under local/renders/")
    duration = args.dur if args.dur is not None else json.loads((HERE / "slots.json").read_text(encoding="utf-8"))[args.slot]["duration"]
    if not math.isfinite(args.start) or not math.isfinite(duration) or not math.isfinite(args.hold_last) or args.start < 0 or duration <= 0 or args.crop_top < 0 or args.hold_last < 0 or args.hold_last >= duration or round(duration * 30) < 1:
        parser.error("--in and --crop-top must be nonnegative; duration must be positive")
    streams = probe(raw)
    video = next((s for s in streams if s["codec_type"] == "video"), None)
    if not video or video["width"] < 2 or video["height"] - args.crop_top < 2:
        parser.error("source video is missing or crop leaves no picture")
    if args.audio == "keep" and not any(s["codec_type"] == "audio" for s in streams):
        parser.error("source has no audio; use --audio drop")
    frames = round(duration * 30)
    output = RENDERS / "scene3/v3/app" / f"{args.slot}.mp4"
    if raw == output.resolve():
        parser.error("raw source cannot be the prepared slot output")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{args.slot}.prep.mp4")
    vf = (f"trim=start={args.start}:duration={duration - args.hold_last},setpts=PTS-STARTPTS,"
          f"crop=iw-mod(iw\\,2):ih-{args.crop_top}-mod(ih-{args.crop_top}\\,2):0:{args.crop_top},"
          f"fps=30,tpad=stop_mode=clone:stop_duration={args.hold_last},format=yuv420p")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-map", "0:v:0", "-vf", vf,
           "-frames:v", str(frames), "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p"]
    if args.audio == "keep":
        cmd += ["-map", "0:a:0", "-af", f"atrim=start={args.start}:duration={duration},asetpts=PTS-STARTPTS,aresample=48000",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    else:
        cmd += ["-an"]
    cmd += ["-movflags", "+faststart", str(temporary)]
    subprocess.run(cmd, check=True)
    result = probe(temporary)
    v = next(s for s in result if s["codec_type"] == "video")
    assert (v["width"] % 2, v["height"] % 2, v["codec_name"], v["pix_fmt"], v["r_frame_rate"], int(v["nb_frames"])) == (0, 0, "h264", "yuv420p", "30/1", frames)
    assert any(s["codec_type"] == "audio" for s in result) == (args.audio == "keep")
    temporary.replace(output)
    print(output.relative_to(RENDERS).as_posix())


if __name__ == "__main__":
    main()
