"""Build intro30. `python build.py --preview` makes labelled placeholders; plain build requires media."""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ASSETS = HERE / "assets"
SLOTS = HERE / "shots.json"
GRADE_FILE = REPO / "film/scene1/grades.sh"
CHAIN = (
    "pan=mono|c0=0.5*c0+0.5*c1,highpass=f=100:poles=2,highpass=f=100:poles=2,"
    "arnndn=m=local/models/rnnoise/cb.rnnn,arnndn=m=local/models/rnnoise/sh.rnnn:mix=0.6,"
    "afftdn=nr=18:nf=-45:tn=0,agate=threshold=0.025:ratio=3:range=0.1:attack=5:release=200:knee=4,"
    "equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3000:t=q:w=1.0:g=2,deesser=i=0.3:m=0.5:f=0.5,"
    "acompressor=threshold=-20dB:ratio=2:attack=10:release=150"
)


def run(*args):
    result = subprocess.run([str(x) for x in args], cwd=REPO, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed: {result.stderr[-1800:]}")
    return result.stdout


def validate(data, preview):
    shots = data["shots"]
    if data["fps"] != 30 or data["duration"] != 30 or len(shots) != 8:
        raise ValueError("Expected eight 30 fps shots totalling 30 seconds")
    end = 0
    for shot in shots:
        if shot["start"] != end or shot["dur"] <= 0 or shot["grade"] != "V1":
            raise ValueError(f"Bad timing or grade: {shot['id']}")
        end += shot["dur"]
    if end != 30:
        raise ValueError("Shots must fill exactly 30 seconds")
    slots = shots + [data["screen"]] + data["sound"]
    missing = [s["id"] for s in slots if (s not in data["sound"] or s["required"])
               and (not s["clip"] or s["in"] is None or s["out"] is None)]
    if missing and not preview:
        raise ValueError("Production render blocked; empty clip or in/out: " + ", ".join(missing))
    for s in slots:
        if s["clip"] and (s["in"] is None or s["out"] is None or s["in"] < 0 or
                          abs(s["out"] - s["in"] - s["dur"]) > 1 / 30):
            raise ValueError(f"{s['id']}: out minus in must match its scheduled duration")
    if not preview and len(data["screen"]["corners"]) != 4:
        raise ValueError("phone_screen needs four measured corners")


def source_path(slot, root):
    clip = slot["clip"]
    kind = "Audio" if slot.get("required") is not None else "Video"
    prefix = f"FOOTAGE:{kind}/"
    if not clip.startswith(prefix):
        raise ValueError(f"{slot['id']}: expected {prefix}<original filename>")
    name = clip[len(prefix):]
    if not name or Path(name).name != name:
        raise ValueError(f"{slot['id']}: clip must be one original filename")
    path = root / kind / name
    if not path.is_file():
        raise FileNotFoundError(f"{slot['id']}: {clip} is absent from footage_root")
    return path


def grade_filter():
    match = re.search(r'^GRADE_V1="(.*)"$', GRADE_FILE.read_text(encoding="utf-8"), re.M)
    if not match:
        raise ValueError("GRADE_V1 missing from scene 1")
    return match.group(1)


def prep_video(slot, src, dst, screen=False):
    probe = json.loads(run("ffprobe", "-v", "error", "-select_streams", "v:0",
                           "-show_entries", "stream=color_transfer", "-of", "json", src))
    transfer = probe["streams"][0].get("color_transfer", "")
    hdr = transfer in {"smpte2084", "arib-std-b67"}
    if screen and hdr:
        raise ValueError("Screen recording is HDR; supply an SDR app recording (screen is never graded)")
    vf = "fps=30"
    if hdr:
        vf += ",zscale=t=linear:npl=100,format=gbrpf32le,tonemap=tonemap=hable:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv"
    if not screen:
        vf += ",scale=1920:1080:flags=lanczos,setsar=1," + grade_filter()
    vf += ",format=yuv420p"
    run("ffmpeg", "-v", "error", "-y", "-ss", slot["in"], "-t", slot["dur"], "-i", src,
        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-movflags", "+faststart", dst)


def prep_audio(slot, src, dst):
    if slot["id"] == "short_intro_voice" and not all(
        (REPO / f"local/models/rnnoise/{name}.rnnn").is_file() for name in ("cb", "sh")
    ):
        raise FileNotFoundError("Scene 1 v3 voice chain needs local/models/rnnoise/{cb,sh}.rnnn")
    af = CHAIN if slot["id"] == "short_intro_voice" else "highpass=f=80"
    if slot["id"] != "short_intro_voice":
        af += ",volume=0.45"
    run("ffmpeg", "-v", "error", "-y", "-ss", slot["in"], "-t", slot["dur"], "-i", src,
        "-af", af, "-ar", "48000", "-ac", "1", dst)


def matrix3d(corners):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = corners
    dx1, dx2, dx3 = x1-x2, x3-x2, x0-x1+x2-x3
    dy1, dy2, dy3 = y1-y2, y3-y2, y0-y1+y2-y3
    den = dx1*dy2-dx2*dy1
    if abs(den) < 1e-9:
        raise ValueError("phone_screen corners form a degenerate quadrilateral")
    g = (dx3*dy2-dx2*dy3)/den
    h = (dx1*dy3-dx3*dy1)/den
    a, b = x1-x0+g*x1, x3-x0+h*x3
    d, e = y1-y0+g*y1, y3-y0+h*y3
    return ",".join(f"{v:.8f}" for v in (
        a/360, d/360, 0, g/360, b/800, e/800, 0, h/800,
        0, 0, 1, 0, x0, y0, 0, 1))


def build(preview):
    data = json.loads(SLOTS.read_text(encoding="utf-8"))
    validate(data, preview)
    ASSETS.mkdir(exist_ok=True)
    shutil.copyfile(REPO / "film/vendor/gsap/gsap.min.js", HERE / "gsap.min.js")
    root = Path(json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))["footage_root"])
    for slot in data["shots"] + [data["screen"]]:
        slot["asset"] = ""
        if not preview and slot["clip"]:
            dest = ASSETS / f"{slot['id']}.mp4"
            prep_video(slot, source_path(slot, root), dest, slot is data["screen"])
            slot["asset"] = f"./assets/{dest.name}"
    for slot in data["sound"]:
        slot["asset"] = ""
        if not preview and slot["clip"]:
            dest = ASSETS / f"{slot['id']}.wav"
            prep_audio(slot, source_path(slot, root), dest)
            slot["asset"] = f"./assets/{dest.name}"
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    page = (HERE / "index.html.tpl").read_text(encoding="utf-8")
    page = page.replace("{{DATA}}", payload).replace("{{PREVIEW}}", "true" if preview else "false")
    page = page.replace("{{MATRIX}}", matrix3d(data["screen"]["corners"]))
    (HERE / "index.html").write_text(page, encoding="utf-8")
    print("Built " + ("placeholder preview" if preview else "production") + " composition")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        sample = json.loads(SLOTS.read_text(encoding="utf-8"))
        sample["shots"][0]["clip"] = ""
        try:
            validate(sample, False)
        except ValueError as exc:
            assert "Production render blocked" in str(exc), str(exc)
            print("Production guard: PASS")
        else:
            raise AssertionError("Production guard did not reject empty slots")
    else:
        build(args.preview)
