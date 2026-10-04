"""Stage the local fallback scene 4 composition and its duration-driven timeline.

Usage: python film/scene4/build.py
All staged media remains under ignored assets/ or RENDERS:scene4/.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MACHINE = json.loads((ROOT / "machine.local.json").read_text(encoding="utf-8"))
RENDERS = Path(MACHINE["renders_dir"])
OUT = RENDERS / "scene4"
ASSETS = HERE / "assets"
FPS = 30
ORDER = ("N7", "N7a", "N7b", "N7c", "N7d")


def run(*args):
    subprocess.run([str(x) for x in args], check=True, cwd=ROOT)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "glass").mkdir(exist_ok=True)
    for n in ("glass.css", "glass.js", "noise.png"):
        shutil.copyfile(ROOT / "film/common/glass" / n, ASSETS / "glass" / n)
    shutil.copyfile(ROOT / "film/vendor/three/three.min.js", HERE / "three.min.js")
    shutil.copyfile(ROOT / "film/vendor/gsap/gsap.min.js", HERE / "gsap.min.js")
    home = ROOT / "local/private-in/F0044/home.png"
    if not home.is_file():
        raise FileNotFoundError("local/private-in/F0044/home.png is needed for the phone screen")
    shutil.copyfile(home, ASSETS / "home.png")
    for n in ("layer_screen.png", "layer_mid.png", "layer_back.png"):
        src = RENDERS / "exploded_v2" / n
        if not src.is_file():
            raise FileNotFoundError(f"RENDERS:exploded_v2/{n}")
        shutil.copyfile(src, ASSETS / n)

    # The previous scene's last moving camera frame is source 10.667 s. The
    # source ends at 10.701 s, so this fallback uses its final moving section.
    footage = Path(MACHINE["footage_root"]) / "Video/sospart2.mp4"
    if not footage.is_file():
        raise FileNotFoundError("FOOTAGE:Video/sospart2.mp4")
    grade_source = (ROOT / "film/scene1/grades.sh").read_text(encoding="utf-8")
    match = re.search(r'^GRADE_V1="(.*)"$', grade_source, re.M)
    if not match:
        raise RuntimeError("GRADE_V1 missing from film/scene1/grades.sh")
    run("ffmpeg", "-v", "error", "-y", "-ss", "9.333333", "-t", "1.333334", "-i", footage,
        "-vf", f"fps=30,scale=1920:1080:flags=lanczos,{match.group(1)},format=yuv420p", "-an", "-c:v", "libx264",
        "-preset", "fast", "-crf", "18", ASSETS / "lab_bridge.mp4")

    narration = json.loads((ROOT / "film/common/narration_v4.json").read_text(encoding="utf-8"))["lines"]
    starts = {}
    cursor = 1.4  # bridge is moving and clears before the first spoken beat
    for key in ORDER:
        line = narration[key]
        if line["segment"] != "s4":
            raise ValueError(f"{key} is not assigned to s4")
        duration = float(line["duration"])
        if duration <= 0:
            raise ValueError(f"{key} has an invalid duration")
        starts[key] = {"start": round(cursor, 6), "duration": duration, "end": round(cursor + duration, 6)}
        cursor += duration + .4
    total = round(cursor + .4, 6)
    page = (HERE / "index.html.tpl").read_text(encoding="utf-8").replace("{{DURATION}}", f"{total:.6f}")
    beats = {
        "bridge": [0, 1.4],
        "turntable": [starts["N7"]["start"], starts["N7"]["end"] + .4],
        "open": [starts["N7a"]["start"], starts["N7a"]["start"] + 1.0],
        "numbers": [starts["N7a"]["start"] + .5, starts["N7c"]["start"] - .35],
        "close": [starts["N7c"]["start"] - .35, starts["N7c"]["start"] + .4],
        "pair": [starts["N7c"]["start"], starts["N7c"]["end"] + .4],
        "end": [starts["N7d"]["start"], total],
    }
    number_starts = [round(beats["numbers"][0] + .22 * i, 6) for i in range(5)]
    if beats["numbers"][1] - .18 - number_starts[-1] - .18 < 2.5:
        raise ValueError("scene 4 number labels cannot each hold for 2.5 s with these narration durations")
    timeline = {"fps": FPS, "duration": total, "narration": starts, "beats": beats,
                "number_starts": number_starts,
                "lab_source": "FOOTAGE:Video/sospart2.mp4", "lab_source_in": 9.333333,
                "fallback": "Three.js primitive plus existing image-layer teardown"}
    (HERE / "timeline.json").write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")
    (ASSETS / "timeline.js").write_text("window.SCENE4=" + json.dumps(timeline, separators=(",", ":")) + ";\n", encoding="utf-8")
    captions = []
    for key in ORDER:
        text = narration[key].get("text", "").strip()
        if text:
            captions.append({"start": starts[key]["start"], "end": starts[key]["end"], "text": text})
    (ASSETS / "captions.js").write_text("window.SCENE4_CAPTIONS=" + json.dumps(captions, ensure_ascii=False) + ";\n", encoding="utf-8")
    video = OUT / "blender_f0064/phone.webm"
    stamp = OUT / "blender_f0064/phone.json"
    complete = video.is_file() and stamp.is_file() and json.loads(stamp.read_text())["duration"] == total
    if complete:
        shutil.copyfile(video, ASSETS / "blender.webm")
    page = page.replace("{{BLENDER_ENABLED}}", "true" if complete else "false")
    page = page.replace("{{FALLBACK_LAYERS}}", (
        '<img class="layer" id="layerBack" src="./assets/layer_back.png" alt="">'
        '<img class="layer" id="layerMid" src="./assets/layer_mid.png" alt="">'
        '<img class="layer" id="layerScreen" src="./assets/layer_screen.png" alt="">'))
    page = page.replace("{{BLENDER_VIDEO}}", (
        f'<video id="blenderPhone" src="./assets/blender.webm" data-start="0.7" '
        f'data-duration="{total - .7:.6f}" data-media-start="0" muted playsinline></video>'
        if complete else ""))
    (HERE / "index.html").write_text(page, encoding="utf-8", newline="\n")
    print("phone:", "licensed Blender teardown" if complete else "accepted fallback")
    print(f"staged scene 4: {total:.2f} s; {len(captions)} narration captions")


if __name__ == "__main__":
    main()
