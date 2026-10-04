"""Build intro v4 from the lead's prepared cuts, voice, words and envelope."""
import json
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ASSETS = HERE / "assets"
FPS = 30
BENCH_START = 32.6
DURATION = 33.6
DISSOLVE = 0.35


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def media(ref, config):
    if ref.startswith("FOOTAGE:"):
        return Path(config["footage_root"]) / ref.removeprefix("FOOTAGE:")
    if ref.startswith("RENDERS:"):
        return Path(config["renders_dir"]) / ref.removeprefix("RENDERS:")
    raise ValueError(f"Unknown media reference: {ref}")


def build():
    config = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
    cuts = json.loads((HERE / "cuts_v4.json").read_text(encoding="utf-8"))
    words = json.loads((HERE / "words_v4.json").read_text(encoding="utf-8"))
    envelope = json.loads((HERE / "envelope_v4.json").read_text(encoding="utf-8"))
    captions = json.loads((REPO / "film/captions/v3/intro.json").read_text(encoding="utf-8"))
    opening, explain = cuts["pieces"]
    assert opening["film_out"] < explain["film_in"] < 7
    dissolve_start = round(explain["film_in"] - DISSOLVE / 2, 4)
    dissolve_end = round(explain["film_in"] + DISSOLVE / 2, 4)
    explain_camera_start = round(explain["camera_in"] - DISSOLVE / 2, 4)
    if explain_camera_start < 0:
        raise ValueError("Long take has no footage for the dissolve")
    assert words[-1]["e"] < BENCH_START and captions[-1]["end"] < BENCH_START
    assert len(envelope["rms"]) > 900 and envelope["fps"] == FPS
    source = [media(p["camera"], config) for p in cuts["pieces"]]
    bench = Path(config["footage_root"]) / "Video/normalpart1.mp4"
    home = REPO / "local/private-in/F0046/home.png"
    voice = media(cuts["voice_wav"], config)
    for path in (*source, bench, home, voice):
        if not path.is_file():
            raise FileNotFoundError(path)

    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "glass").mkdir(exist_ok=True)
    for name in ("glass.css", "glass.js", "noise.png"):
        shutil.copy2(REPO / "film/common/glass" / name, ASSETS / "glass" / name)
    shutil.copy2(REPO / "film/vendor/gsap/gsap.min.js", HERE / "gsap.min.js")
    shutil.copy2(home, ASSETS / "home.png")
    shutil.copy2(voice, ASSETS / "voice.wav")

    grade = re.search(r'^GRADE_V1="(.*)"$', (REPO / "film/scene1/grades.sh").read_text(encoding="utf-8"), re.M)
    if not grade:
        raise ValueError("GRADE_V1 missing")
    for name, src, length in (
        ("opening", source[0], dissolve_end),
        ("explain", source[1], BENCH_START - dissolve_start),
        ("bench", bench, DURATION - BENCH_START),
    ):
        dst = ASSETS / f"{name}.mp4"
        if dst.is_file() and dst.stat().st_mtime >= src.stat().st_mtime:
            old_length = float(json.loads(subprocess.check_output([
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "json", str(dst)], text=True))["format"]["duration"])
            if abs(old_length - length) < 1 / FPS:
                continue
        probe = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=color_transfer", "-of", "json", str(src)], text=True))
        vf = "fps=30"
        if probe["streams"][0].get("color_transfer") in {"smpte2084", "arib-std-b67"}:
            vf += ",zscale=t=linear:npl=100,format=gbrpf32le,tonemap=tonemap=hable:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv"
        vf += ",scale=1920:1080:flags=lanczos,setsar=1," + grade.group(1) + ",format=yuv420p"
        offset = explain_camera_start if name == "explain" else 0
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", offset,
            "-i", src, "-t", length, "-vf", vf, "-an", "-c:v", "libx264",
            "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", dst)

    timeline = {
        "fps": FPS, "duration": DURATION, "cut": explain["film_in"],
        "dissolve": {"start": dissolve_start, "end": dissolve_end},
        "beats": {"bridge": 6.962, "badges": 8.522, "wave": 15.682,
                  "message": 20.702, "read": 25.262, "title": 31.2,
                  "title_hold": 31.4, "bench": BENCH_START},
        "end_state": {"normalpart1_src": round(DURATION - 1 / FPS - BENCH_START, 6)},
    }
    (HERE / "timeline.json").write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")
    payload = json.dumps({"timeline": timeline, "words": words, "envelope": envelope,
                          "captions": captions}, ensure_ascii=False)
    page = (HERE / "index.html.tpl").read_text(encoding="utf-8")
    page = page.replace("{{DATA}}", payload)
    page = page.replace("{{OPENING_END}}", str(dissolve_end))
    page = page.replace("{{EXPLAIN_START}}", str(dissolve_start))
    page = page.replace("{{EXPLAIN_DURATION}}", str(round(BENCH_START - dissolve_start, 4)))
    (HERE / "index.html").write_text(page, encoding="utf-8")
    print("Intro v4 built:", DURATION, "s, bench last frame:", timeline["end_state"]["normalpart1_src"])


if __name__ == "__main__":
    build()
