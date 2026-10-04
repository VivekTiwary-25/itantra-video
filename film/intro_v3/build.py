"""Build the word-timed intro from prepared audio and local footage."""
import json
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ASSETS = HERE / "assets"
OFFSET = 0.7781  # camera time = clean-audio time - OFFSET
VOICE_START = 1.24 - OFFSET  # Rule B voice.wav starts 0.12 s before first word
DURATION = 13.8


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def word_time(words, token, nth=1):
    hits = [w for w in words if re.sub(r"[^a-z0-9]", "", w["w"].lower()) == token]
    if len(hits) < nth:
        raise ValueError(f"Missing word {token} #{nth}")
    return round(hits[nth - 1]["s"] - OFFSET, 3)


def build():
    config = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
    source = Path(config["footage_root"]) / "Video" / "20261002_081346_short_intro.mp4"
    home = REPO / "local/private-in/F0023/home.png"
    voice = Path(config["renders_dir"]) / "intro_v3/voice.wav"
    if not all(p.is_file() for p in (source, home, voice)):
        raise FileNotFoundError("Missing camera, private home screen, or prepared voice.wav")
    words = json.loads((HERE / "words.json").read_text(encoding="utf-8"))
    envelope = json.loads((HERE / "envelope.json").read_text(encoding="utf-8"))
    if words[-1]["w"] != "works." or len(envelope) < 300:
        raise ValueError("Prepared words/envelope do not match the approved take")
    timings = {name: word_time(words, token, nth) for name, token, nth in (
        ("panel", "im", 1), ("built", "we", 1), ("wave", "speaker", 1),
        ("message", "message", 1), ("travels", "travels", 1),
        ("phone1", "phone", 1), ("phone2", "phone", 2),
        ("no", "no", 1), ("network", "network", 1),
        ("needed", "needed", 1), ("lets", "lets", 1))}
    timings.update(camera_end=13.16, full=13.16, end=DURATION, voice_start=round(VOICE_START, 4))
    (HERE / "timeline.json").write_text(json.dumps(timings, indent=2) + "\n", encoding="utf-8")
    groups = [(0, 6), (6, 11), (11, 14), (14, 17), (17, 22), (22, 25), (25, 30)]
    captions = [{"start": round(words[a]["s"] - OFFSET, 3),
                 "end": round(words[b - 1]["e"] - OFFSET, 3),
                 "text": " ".join(w["w"] for w in words[a:b])} for a, b in groups]
    target = REPO / "film/captions/v3/intro.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(captions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ASSETS.mkdir(exist_ok=True)
    glass = ASSETS / "glass"
    glass.mkdir(exist_ok=True)
    for name in ("glass.css", "glass.js", "noise.png"):
        shutil.copy2(REPO / "film/common/glass" / name, glass / name)
    shutil.copy2(REPO / "film/vendor/gsap/gsap.min.js", HERE / "gsap.min.js")
    shutil.copy2(home, ASSETS / "home.png")
    shutil.copy2(voice, ASSETS / "voice.wav")
    run("python", HERE / "sfx.py")
    shutil.copy2(Path(config["renders_dir"]) / "intro_v3/sfx.wav", ASSETS / "sfx.wav")
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=color_transfer", "-of", "json", str(source)], text=True))
    transfer = probe["streams"][0].get("color_transfer", "")
    vf = "fps=30"
    if transfer in {"smpte2084", "arib-std-b67"}:
        vf += ",zscale=t=linear:npl=100,format=gbrpf32le,tonemap=tonemap=hable:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv"
    grade = re.search(r'^GRADE_V1="(.*)"$', (REPO / "film/scene1/grades.sh").read_text(encoding="utf-8"), re.M)
    if not grade:
        raise ValueError("GRADE_V1 missing")
    vf += ",scale=1920:1080:flags=lanczos,setsar=1," + grade.group(1) + ",format=yuv420p"
    camera = ASSETS / "camera.mp4"
    if not camera.is_file() or camera.stat().st_mtime < source.stat().st_mtime:
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", source,
            "-t", timings["camera_end"], "-vf", vf, "-an", "-c:v", "libx264",
            "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", camera)
    payload = json.dumps({"timings": timings, "words": words, "envelope": envelope,
                          "captions": captions, "duration": DURATION}, ensure_ascii=False)
    page = (HERE / "index.html.tpl").read_text(encoding="utf-8")
    (HERE / "index.html").write_text(page.replace("{{DATA}}", payload), encoding="utf-8")
    print("Intro built: camera SDR", transfer, "duration", DURATION)


if __name__ == "__main__":
    build()
