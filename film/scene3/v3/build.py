"""Build scene 3 v3: python film/scene3/v3/build.py [--page-only].

App slots are swappable RENDERS: media. A final render refuses missing slots.
"""
import argparse
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
MACHINE = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
RENDERS = Path(MACHINE["renders_dir"])
try:
    OUT = RENDERS / "scene3/v3"
    OUT.mkdir(parents=True, exist_ok=True)
except PermissionError:
    # Existing scene3/ is read-only in this worker sandbox; new render subtrees are writable.
    OUT = RENDERS / "F0060/scene3/v3"
    OUT.mkdir(parents=True, exist_ok=True)
FPS = 30
SR = 48000
# Source times in the uncut vivek_app slot. All cuts are idle frames; each join
# dissolves for three frames. Keep the entire 7.78-11.63 s TTS playback.
VIVEK_CUTS = ((1.0, 2.2), (3.7, 4.5), (5.5, 7.2),
              (11 + 22 / FPS, 12 + 8 / FPS), (17 + 20 / FPS, 19 + 14 / FPS))
DISSOLVE = 3 / FPS
SONAR = {"sos_dive": 1.5}
NARRATION = REPO / "film/common/narration_v4.json"
CAPTION_DIALOGUE = (
    ("vachana_sos", 1.400333, 4.000333, "I'm lost somewhere near\nthe construction site."),
    ("vachana_sos", 4.320333, 5.060333, "Please reach me out."),
    ("vachana_sos", 5.500333, 6.120333, "Help me anyone."),
    ("vivek_app", 7.779667, 9.726667, "I'm lost somewhere near\nthe construction site."),
    ("vivek_app", 9.726667, 11.634667, "Please reach me out.\nHelp me anyone."),
    ("vivek_app", 12.859667, 13.339667, "Wait,"),
    ("vivek_app", 13.339667, 14.419667, "I'm in the chemistry lab."),
    ("vivek_app", 14.419667, 15.659667, "I'll come get you, wait."),
)


def narration_lines():
    lines = json.loads(NARRATION.read_text(encoding="utf-8"))["lines"]
    required = ("N5", "N5a", "N5b", "N6")
    for key in required:
        if float(lines[key]["duration"]) <= 0:
            raise ValueError(f"invalid narration duration: {key}")
    return lines


def trimmed_time(source_time):
    if any(a < source_time < b for a, b in VIVEK_CUTS):
        raise ValueError(f"event inside an idle cut: {source_time}")
    return source_time - sum(b - a + DISSOLVE for a, b in VIVEK_CUTS if source_time >= b)


def trimmed_slots(slots):
    result = {key: value.copy() for key, value in slots.items()}
    item = result["vivek_app"]
    for key in ("accept_at", "play_at", "ptt_down", "ptt_up", "sent_at", "duration"):
        item[key] = trimmed_time(item[key])
    return result


def trim_vivek_slot(source, output):
    ends = (0.0,) + tuple(b for _, b in VIVEK_CUTS)
    starts = tuple(a for a, _ in VIVEK_CUTS) + (21.366667,)
    spans = list(zip(ends, starts))
    filters = []
    for i, (a, b) in enumerate(spans):
        filters.append(f"[0:v]trim=start_frame={round(a*FPS)}:end_frame={round(b*FPS)},setpts=PTS-STARTPTS,fps={FPS}[v{i}]")
    duration = spans[0][1] - spans[0][0]
    previous = "v0"
    for i, (a, b) in enumerate(spans[1:], 1):
        next_name = f"x{i}"
        filters.append(f"[{previous}][v{i}]xfade=transition=fade:duration={DISSOLVE}:offset={duration-DISSOLVE:.6f}[{next_name}]")
        duration += b - a - DISSOLVE
        previous = next_name
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(".vivek_app.trim.mp4")
    run("ffmpeg", "-v", "error", "-y", "-i", source, "-filter_complex", ";".join(filters),
        "-map", f"[{previous}]", "-frames:v", round(duration * FPS), "-an", "-c:v", "libx264",
        "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", temporary)
    temporary.replace(output)
    check_video(output, duration - 1 / FPS)
# T0040 camera windows. App-only takeover replaces every former held frame.
LAB_OPEN_FRAMES = 39
VIVEK_HOLD_A, VIVEK_HOLD_B, VIVEK_LAST = 39, 78, 230
VIVEK_M1_AT = 225          # slot frame where the first motion starts (7.5 s, just before Play at 7.63 s)
VIVEK_LINE_PLATE = 4.606   # first word of his line, seconds into the plate
CHAIN = ("pan=mono|c0=0.5*c0+0.5*c1,highpass=f=100:poles=2,highpass=f=100:poles=2,"
         "arnndn=m=local/models/rnnoise/cb.rnnn,"
         "afftdn=nr=18:nf=-45:tn=0,agate=threshold=0.025:ratio=3:range=0.1:attack=5:release=200:knee=4,"
         "equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3000:t=q:w=1.0:g=2,deesser=i=0.3:m=0.5:f=0.5,"
         "acompressor=threshold=-20dB:ratio=2:attack=10:release=150,loudnorm=I=-16:TP=-1.5:LRA=11")


def run(*args, cwd=REPO):
    p = subprocess.run([str(x) for x in args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode:
        raise RuntimeError(f"{args[0]} failed:\n{p.stdout[-1500:]}\n{p.stderr[-2000:]}")
    return p.stdout


def render_path(ref):
    if not ref.startswith("RENDERS:"):
        raise ValueError("slot path must start RENDERS:")
    relative = Path(ref[8:])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("slot path must be relative to renders_dir")
    if relative.parts[:2] == ("scene3", "v3") and OUT != RENDERS / "scene3/v3":
        return OUT.joinpath(*relative.parts[2:])
    return RENDERS / relative


def ensure_full_slots(slots):
    """Prepare the original 2400 px app captures with their whole screen visible."""
    sources = {"vachana_sos": ("scene3/app/vachana_sos.mkv", .64),
               "vivek_app": ("scene3/app/vivek_take.mkv", 4.75)}
    for key, (relative, offset) in sources.items():
        output = render_path(slots[key]["path"])
        source = RENDERS / relative
        if not source.is_file():
            continue
        if key == "vivek_app":
            full = OUT / "app/vivek_full.mp4"
            if not full.is_file() or full.stat().st_mtime < source.stat().st_mtime:
                run(sys.executable, HERE / "prep_slot.py", key, source, "--in", offset,
                    "--dur", slots[key]["duration"], "--crop-top", 0, "--audio", "drop", "--out", full)
            marker = output.with_suffix(".cuts.json")
            spec = json.dumps(VIVEK_CUTS)
            if (not output.is_file() or output.stat().st_mtime < full.stat().st_mtime
                    or not marker.is_file() or marker.read_text(encoding="utf-8") != spec):
                trim_vivek_slot(full, output)
                marker.write_text(spec, encoding="utf-8")
        elif not output.is_file() or output.stat().st_mtime < source.stat().st_mtime:
            run(sys.executable, HERE / "prep_slot.py", key, source, "--in", offset,
                "--dur", slots[key]["duration"], "--crop-top", 0, "--audio", "drop", "--out", output)


def timeline(slots):
    lines = narration_lines()
    rows, frame = [], 0
    def add(name, seconds, **extra):
        nonlocal frame
        length = round(seconds * FPS)
        rows.append(dict(name=name, start=frame / FPS, end=(frame + length) / FPS, **extra))
        frame += length
    add("card_out", lines["N5"]["duration"] + .4, source="FOOTAGE:Video/sospart1.mp4")
    add("s3_open", 2.866667, source="FOOTAGE:Video/sospart1.mp4", source_in=0)
    add("vachana_sos", slots["vachana_sos"]["duration"], camera="FOOTAGE:Video/sospart1.mp4", camera_in=2.866667)
    add("sos_sonar", sum(lines[k]["duration"] + .4 for k in ("N5a", "N5b", "N6")))
    add("sos_dive", SONAR["sos_dive"])
    add("lab_open", LAB_OPEN_FRAMES / FPS, source="FOOTAGE:Video/sospart2.mp4", source_in=3.0)
    add("vivek_app", slots["vivek_app"]["duration"], camera="FOOTAGE:Video/sospart2.mp4", camera_in=3.0 + LAB_OPEN_FRAMES / FPS)
    # The last 0.4 s follows the visible Send tap and its sound.
    rows[-1]["end"] = rows[-1]["start"] + round((slots["vivek_app"]["sent_at"] + .4) * FPS) / FPS
    frame = round(rows[-1]["end"] * FPS)
    by = {row["name"]: row for row in rows}
    m2 = round((slots["vivek_app"]["ptt_down"] + .1 - (VIVEK_LINE_PLATE - VIVEK_HOLD_B / FPS)) * FPS)
    m1_from = trimmed_time(VIVEK_M1_AT / FPS)
    m1_end = m1_from + (VIVEK_HOLD_B - VIVEK_HOLD_A) / FPS
    if not m1_from < m1_end <= m2 / FPS:
        raise RuntimeError("vivek_app camera plan does not fit the slot timings")
    vivek_camera = {"m1_from": m1_from, "m1_to": m1_end, "m2_from": m2 / FPS,
                    "m2_to": (m2 + VIVEK_LAST - VIVEK_HOLD_B) / FPS}
    sonar_start = by["sos_sonar"]["start"]
    narration_starts = {"N5": 0.0}
    beat = []
    at = sonar_start
    for key in ("N5a", "N5b", "N6"):
        narration_starts[key] = at
        beat.append({"name": key, "start": at, "end": at + lines[key]["duration"] + .4})
        at = beat[-1]["end"]
    return {"fps": FPS, "duration": frame / FPS, "segments": rows, "vivek_camera": vivek_camera,
            "techlines": [], "sos_beats": beat,
            "narration_starts": narration_starts,
            "slot_fields": {k: {a: b for a, b in v.items() if a != "path"} for k, v in slots.items()}}


def grade():
    source = (REPO / "film/scene1/grades.sh").read_text(encoding="utf-8")
    match = re.search(r'^GRADE_V1="(.*)"$', source, re.M)
    if not match:
        raise RuntimeError("GRADE_V1 missing")
    return match.group(1)


def probe(path):
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(run("ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type,width,height,r_frame_rate", "-of", "json", path))


def check_video(path, seconds):
    info = probe(path)
    streams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    if not streams or int(streams[0].get("width", 0)) < 2 or int(streams[0].get("height", 0)) < 2:
        raise RuntimeError(f"unplayable video: {path}")
    if float(info.get("format", {}).get("duration", 0)) + .07 < seconds:
        raise RuntimeError(f"video shorter than {seconds:.3f}s: {path}")
    return streams[0]


def camera_plate(source, destination, start, seconds):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or destination.stat().st_mtime < source.stat().st_mtime:
        run("ffmpeg", "-v", "error", "-y", "-ss", start, "-t", seconds, "-i", source,
            "-vf", f"fps=30,scale=1920:1080:flags=lanczos,{grade()},format=yuv420p",
            "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", destination)
    check_video(destination, seconds - 1 / FPS)


def still(source, destination, at):
    if not destination.exists() or destination.stat().st_mtime < source.stat().st_mtime:
        run("ffmpeg", "-v", "error", "-y", "-ss", at, "-i", source,
            "-frames:v", "1", "-q:v", "3", destination)
    if not destination.is_file():
        raise RuntimeError(f"missing still: {destination}")


def placeholder_video(destination, seconds, height=2290):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
            f"color=c=0x101820:s=1080x{height}:r=30:d={seconds:.6f}",
            "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
            "-pix_fmt", "yuv420p", destination)
    check_video(destination, seconds - 1 / FPS)


def asset(source, name=None):
    target = HERE / "assets" / (name or source.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.stat().st_size != source.stat().st_size or target.stat().st_mtime < source.stat().st_mtime:
        if target.exists():
            target.unlink()
        try:
            os.link(source, target)
        except OSError:
            shutil.copyfile(source, target)
    return "assets/" + target.name


def prepare_sonar_still(slots):
    """Supply the existing sos_in builder with the slot's searching frame."""
    source = render_path(slots["vachana_sos"]["path"])
    target = OUT / "plates/vachana_sos_last.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.exists():
        info = check_video(source, slots["vachana_sos"]["duration"] - 1 / FPS)
        pad = "pad=iw:ih+110:0:110:color=black" if int(info["height"]) <= 2300 else "null"
        run("ffmpeg", "-v", "error", "-y", "-ss", slots["vachana_sos"]["duration"] - 1 / FPS,
            "-i", source, "-vf", pad, "-frames:v", "1", target)
    else:
        run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
            "color=c=0x101820:s=1080x2400", "-frames:v", "1", target)
    return target


def sonar_assets(app_still, preview_only=False):
    """Use the original three sonar compositions without changing their code."""
    source = REPO / "film/scene3/sonar"
    stage = OUT / "sonar_work"
    shutil.copytree(source, stage / "film/scene3/sonar", dirs_exist_ok=True)
    for relative in ("film/scene1/grades.sh", "machine.local.json"):
        dest = stage / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / relative, dest)
    for relative in ("film/scene2/geo", "film/vendor"):
        shutil.copytree(REPO / relative, stage / relative, dirs_exist_ok=True)
    # The v2 sos_in sides looped one blurred camera frame. Patch only the staged
    # copy so v3 keeps the same look while playing src 8.6-10.64 continuously.
    staged_sonar = stage / "film/scene3/sonar"
    cues_path = staged_sonar / "cues.py"
    cues_text = cues_path.read_text(encoding="utf-8")
    old_src = "SIDES_SRC = ('Video/sospart1.mp4', 10.5)"
    if old_src not in cues_text:
        raise RuntimeError("sos_in side source changed; review the v3 motion patch")
    still_ref = "RENDERS:" + app_still.relative_to(RENDERS).as_posix()
    cues_path.write_text(cues_text.replace(old_src, "SIDES_SRC = ('Video/sospart1.mp4', 8.6)")
                         .replace("RENDERS:scene3/app/vachana_sos_last.png", still_ref), encoding="utf-8")
    sonar_build = staged_sonar / "build.py"
    source = sonar_build.read_text(encoding="utf-8")
    old_filter = "'-frames:v', '1', '-vf',\n        f\"{grade},gblur=sigma=40,eq=brightness=-0.02,colorchannelmixer=rr=0.55:gg=0.55:bb=0.55,loop=loop={n_in}:size=1:start=0,fps={fps},setpts=N/{fps}/TB\","
    new_filter = "'-vf',\n        f\"fps={fps},{grade},gblur=sigma=40,eq=brightness=-0.02,colorchannelmixer=rr=0.55:gg=0.55:bb=0.55\","
    if old_filter not in source:
        raise RuntimeError("sos_in still loop changed; review the v3 motion patch")
    sonar_build.write_text(source.replace(old_filter, new_filter), encoding="utf-8")
    if importlib.util.find_spec("scipy") is None:
        if not preview_only:
            raise RuntimeError("SciPy is required to regenerate the sonar sound for a production render")
        cached = RENDERS / "scene3/v2/sonar"
        videos = {}
        for name, seconds in SONAR.items():
            path = cached / f"{name}.mp4"
            check_video(path, seconds - 1 / FPS)
            videos[name] = path
        print("Preview uses cached v2 sonar video; production render requires SciPy")
        return videos, stage
    run(sys.executable, stage / "film/scene3/sonar/build.py", cwd=stage)
    for name, seconds in SONAR.items():
        comp = stage / "film/scene3/sonar" / name
        output = OUT / "sonar" / f"{name}.mp4"
        stale = not output.exists() or (name == "sos_in" and output.stat().st_mtime < app_still.stat().st_mtime)
        if stale:
            run("hyperframes.cmd", "check", cwd=comp)
            output.parent.mkdir(parents=True, exist_ok=True)
            run("hyperframes.cmd", "render", "-q", "high", "-f", "30", "-o", output, cwd=comp)
        check_video(output, seconds - 1 / FPS)
    return {name: OUT / "sonar" / f"{name}.mp4" for name in SONAR}, stage


def screen(slot, name, start, seconds, missing):
    source = render_path(slot["path"])
    if not source.exists():
        source = OUT / "placeholders" / f"{name}.mp4"
        placeholder_video(source, slot["duration"])
        missing.append(slot["path"])
    # Blank preview placeholders contain no recreated app UI.
    info = check_video(source, slot["duration"] - 1 / FPS)
    width = min(560, 1000 * info["width"] / info["height"])
    video = asset(source, f"{name}{source.suffix}")
    contents = (f'<video id="video_{name}" src="{video}" data-start="{start:.6f}" '
                f'data-duration="{seconds:.6f}" data-media-start="0" muted playsinline></video>')
    # T0040: the slot's first frame sits behind the video, so the phone is never blank while it slides in.
    first = OUT / "plates" / f"{name}_first.jpg"
    still(source, first, 0)
    overflow = ' data-layout-allow-overflow' if name == 'vivek_app' else ''
    tap = '<div class="accept-tap-ring" aria-hidden="true"></div>' if name == 'vivek_app' else ''
    return f'<div class="screen"{overflow} style="width:{width:.2f}px;background:#101820 url({asset(first)}) center/100% 100% no-repeat">{contents}<div class="status-mask" aria-hidden="true"></div>{tap}</div>'


def write_page(T, slots, sonar, missing):
    root = Path(MACHINE["footage_root"])
    p = OUT / "plates"
    camera_plate(root / "Video/sospart1.mp4", p / "vachana.mp4", 0, 10.64)
    camera_plate(root / "Video/sospart2.mp4", p / "vivek.mp4", 3.0, 7.70)
    pic = {"vachana": asset(p / "vachana.mp4"), "vivek": asset(p / "vivek.mp4"),
           }
    rows = T["segments"]
    layers = []
    # F0051: frame 0 uses s2b's exact join card (film/scene2/v3b/timeline.json end_state.card_html).
    s2b_end = json.loads((REPO / "film/scene2/v3b/timeline.json").read_text(encoding="utf-8")).get("end_state", {})
    card_html = s2b_end.get("card_html") or '<div class="glass-card full"><h1 class="card-title"><span style="color:var(--red)">SOS</span></h1><p>help from anyone nearby, no saved contact needed</p></div>'
    for row in rows:
        name, start, seconds = row["name"], row["start"], row["end"] - row["start"]
        if name == "card_out":
            layers.append(f'<div class="scene" id="seg_card_out"><video id="video_card_out" class="full card-footage" src="{pic["vachana"]}" data-start="0" data-duration="{seconds:.6f}" data-media-start="0" muted playsinline></video><div class="sos-card-wrap" id="sos-card">{card_html}</div></div>')
        elif name in ("s3_open", "lab_open"):
            key = "vachana" if name == "s3_open" else "vivek"
            cover = f'<div class="sos-card-wrap" id="sos-card-clear">{card_html}</div>' if name == "s3_open" else ''
            layers.append(f'<div class="scene" id="seg_{name}"><video id="video_{name}" class="full" src="{pic[key]}" data-start="{start:.6f}" data-duration="{seconds:.6f}" data-media-start="0" muted playsinline></video>{cover}</div>')
        elif name == "vivek_app":
            C = T["vivek_camera"]
            c = "".join(
                f'<video id="video_vivek_app_camera{n}" class="camera-motion" src="{pic["vivek"]}" data-start="{start+a:.6f}" '
                f'data-duration="{b-a:.6f}" data-media-start="{m:.6f}" muted playsinline></video>'
                for n, a, b, m in ((1, C["m1_from"], C["m1_to"], VIVEK_HOLD_A / FPS), (2, C["m2_from"], C["m2_to"], VIVEK_HOLD_B / FPS)))
            layers.append(f'<div class="scene split" id="seg_{name}"><div class="camera camera-vivek">{c}<div class="feather"></div></div>'
                          f'<div class="app-field" id="vivek-field">{screen(slots[name],name,start,seconds,missing)}</div></div>')
        elif name == "vachana_sos":
            c = (f'<video id="video_vachana_sos_camera" class="camera-motion" src="{pic["vachana"]}" data-start="{start:.6f}" '
                 f'data-duration="{(10.64-2.866667):.6f}" data-media-start="2.866667" muted playsinline></video>')
            layers.append(f'<div class="scene split" id="seg_{name}"><div class="camera camera-vachana">{c}<div class="feather"></div></div><div class="app-field" id="vachana-field">{screen(slots[name],name,start,seconds,missing)}</div></div>')
        elif name == "sos_sonar":
            layers.append(f'<div class="scene" id="seg_sos_sonar"><canvas id="sos-map" width="1920" height="1080" data-layout-allow-overflow></canvas><svg id="sos-waves" viewBox="0 0 1920 1080" width="1920" height="1080" aria-hidden="true"><circle id="wave-0"/><circle id="wave-1"/></svg><div class="map-pin" id="pin-v"><i></i><span>Vachana</span></div><div id="search-dots"></div><div class="map-pin" id="pin-k"><i></i><span>Vivek</span></div><div class="map-pill" id="sos-label"></div><div class="map-pill" id="sos-timer"></div><div class="map-pill" id="sos-accept"><span>Accept</span><span>Decline</span></div></div>')
        elif name in SONAR:
            src = asset(sonar[name], f"{name}.mp4")
            check_video(sonar[name], seconds - 1 / FPS)
            layers.append(f'<div class="scene" id="seg_{name}"><video id="video_{name}" class="full" src="{src}" data-start="{start:.6f}" data-duration="{seconds:.6f}" data-media-start="0" muted playsinline></video></div>')
    page = (HERE / "index.html.tpl").read_text(encoding="utf-8")
    by = {r["name"]: r for r in rows}
    captions = []
    for name, a, b, message in CAPTION_DIALOGUE:
        if name == "vivek_app":
            a, b = trimmed_time(a), trimmed_time(b)
        captions.append({"start": round(by[name]["start"] + a, 3),
                         "end": round(by[name]["start"] + b, 3), "text": message})
    for key, start in T["narration_starts"].items():
        line = narration_lines()[key]
        if line["text"].strip():
            captions.append({"start": round(start, 3), "end": round(start + line["duration"], 3),
                             "text": line["text"]})
    captions.sort(key=lambda c: c["start"])
    (REPO / "film/captions/v3/s3.json").write_text(json.dumps(captions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not all(0 <= c["start"] < c["end"] <= T["duration"] for c in captions):
        raise RuntimeError("caption outside scene 3 duration")
    glass = HERE / "assets/glass"
    glass.mkdir(parents=True, exist_ok=True)
    for filename in ("glass.css", "glass.js", "noise.png"):
        shutil.copyfile(REPO / "film/common/glass" / filename, glass / filename)
    sonar_dir = HERE / "assets/sonar"
    sonar_dir.mkdir(parents=True, exist_ok=True)
    for source, name in ((REPO / "film/vendor/three/three.min.js", "three.min.js"),
                         (REPO / "film/scene3/sonar/shared/sonar.js", "sonar.js"),
                         (REPO / "film/scene3/sonar/sos_sonar/geo.js", "geo.js")):
        shutil.copyfile(source, sonar_dir / name)
    page = page.replace("{{DURATION}}", f'{T["duration"]:.6f}').replace("{{TIMELINE}}", json.dumps(T, separators=(",", ":")))
    page = page.replace("{{CAPTIONS}}", json.dumps(captions, separators=(",", ":")).replace("<", "\\u003c"))
    page = page.replace("{{LAYERS}}", "\n".join(layers))
    (HERE / "index.html").write_text(page, encoding="utf-8", newline="\n")
    (HERE / "timeline.json").write_text(json.dumps(T, indent=2) + "\n", encoding="utf-8")
    # Every generated media reference must exist and each video must cover its declared span.
    for src, duration in re.findall(r'<video[^>]*src="([^"]+)"[^>]*data-duration="([^"]+)"', page):
        check_video(HERE / src, float(duration) - 1 / FPS)
    for ref in re.findall(r'url\((assets/[^)]+)\)', page):
        if not (HERE / ref).is_file():
            raise RuntimeError(f"missing image asset: {ref}")


def pcm(path, filt=None):
    import numpy as np
    command = ["ffmpeg", "-v", "error", "-i", str(path)]
    if filt:
        command += ["-af", filt]
    command += ["-ar", str(SR), "-ac", "1", "-f", "f32le", "-"]
    p = subprocess.run(command, cwd=REPO, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors="replace")[-1800:])
    return np.frombuffer(p.stdout, "<f4").copy()


def put(track, clip, at):
    i = round(at * SR)
    a, b = max(0, -i), max(0, i)
    n = min(len(clip) - a, len(track) - b)
    if n > 0:
        track[b:b+n] += clip[a:a+n]


def spoken(path, first, last):
    """Only the word window is audible, with 30 ms edge fades and 0.30 s tail."""
    import numpy as np
    chain = CHAIN
    if not (REPO / "local/models/rnnoise/cb.rnnn").is_file():
        chain = chain.replace("arnndn=m=local/models/rnnoise/cb.rnnn,", "")
    source = pcm(path, chain)
    left, right = max(0, round((first - .12) * SR)), min(len(source), round((last + .30) * SR))
    clip = source[left:right].copy()
    if first < .12:
        clip = np.pad(clip, (round((.12 - first) * SR), 0))
    fade = min(round(.03 * SR), len(clip) // 2)
    if fade:
        clip[:fade] *= np.linspace(0, 1, fade)
        clip[-fade:] *= np.linspace(1, 0, fade)
    return clip


def wav(path, samples):
    import numpy as np
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        output.writeframes((np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes())


def narration_file(key):
    return render_path(narration_lines()[key]["file"])


def preview_narration_placeholders():
    import numpy as np
    for key in ("N5", "N5a", "N5b", "N6"):
        line = narration_lines()[key]
        path = narration_file(key)
        if line.get("status") == "placeholder" and not path.exists():
            wav(path, np.zeros(round(line["duration"] * SR), dtype=np.float32))


def audio(T, slots, stage):
    import numpy as np
    by = {r["name"]: r for r in T["segments"]}
    dialogue = np.zeros(round(T["duration"] * SR), dtype=np.float32)
    missing = []
    events = []
    root = Path(MACHINE["footage_root"])
    at = by["vachana_sos"]["start"] + slots["vachana_sos"]["listen_at"] - .12
    clip = spoken(root / "Audio/sospart1.mp3", 0.0, 4.72)
    put(dialogue, clip, at); events.append((at, at + len(clip) / SR, "dialogue Vachana SOS line"))
    at = by["vivek_app"]["start"] + slots["vivek_app"]["ptt_down"] + .1 - .12
    clip = spoken(root / "Audio/sospart2.mp3", 7.54, 10.34)
    put(dialogue, clip, at); events.append((at, at + len(clip) / SR, "dialogue Vivek reply line"))
    tts = RENDERS / "tts_itantra/tts_sos.wav"
    if tts.exists():
        clip = pcm(tts, "loudnorm=I=-16:TP=-1.5:LRA=11")
        at = by["vivek_app"]["start"] + slots["vivek_app"]["play_at"] + .15
        put(dialogue, clip, at); events.append((at, at + len(clip) / SR, "app TTS tts_sos"))
    else:
        missing.append("RENDERS:tts_itantra/tts_sos.wav")
    for key, at in T["narration_starts"].items():
        if narration_lines()[key].get("dropped"):
            continue
        path = narration_file(key)
        if path.exists():
            # T0040: the cleaned narration files sit at -18 LUFS; one static +2 dB gain, no per-clip loudnorm.
            clip = pcm(path) * 10 ** (2 / 20)
            limit = narration_lines()[key]["duration"] + .4
            if len(clip) / SR > limit:
                print(f"WARNING: {key} narration exceeds {limit:.1f} s", file=sys.stderr)
            put(dialogue, clip, at); events.append((at, at + len(clip) / SR, "narration " + key))
        else:
            missing.append("RENDERS:" + path.relative_to(RENDERS).as_posix())
    # T0040: production cue set from film/sound/make_set.py (T0035), at its suggested gains.
    sounds = RENDERS / "sound"
    if not all((sounds / f"{name}.wav").exists() for name in ("notify", "sent", "sos_notify", "sos_send")):
        run(sys.executable, REPO / "film/sound/make_set.py")
    cues = [("sos_send", "vachana_sos", slots["vachana_sos"]["send_at"], -11),
            ("sos_notify", "lab_open", .1, -10),
            ("sent", "vivek_app", slots["vivek_app"]["sent_at"], -10)]
    for sound, segment, offset, gain_db in cues:
        put(dialogue, pcm(sounds / f"{sound}.wav") * 10 ** (gain_db / 20), by[segment]["start"] + offset)
        events.append((by[segment]["start"] + offset, by[segment]["start"] + offset + len(pcm(sounds / f"{sound}.wav")) / SR, "sfx " + sound))
    for name, seconds in SONAR.items():
        sfx = stage / "film/scene3/sonar" / name / "assets" / f"{name}_sfx.wav"
        if not sfx.exists():
            raise FileNotFoundError(sfx)
        put(dialogue, pcm(sfx)[:round(seconds * SR)], by[name]["start"])
    # The explanatory pulse is a seamless self-rendered loop; repeat its short
    # sound bed to the new narration-driven length with quiet crossfades.
    pulse_sfx = stage / "film/scene3/sonar/sos_sonar/assets/sos_sonar_sfx.wav"
    if pulse_sfx.exists():
        bed = pcm(pulse_sfx)
        if len(bed):
            target = round((by["sos_sonar"]["end"] - by["sos_sonar"]["start"]) * SR)
            repeat = np.resize(bed, target).astype(np.float32)
            seam_fade = min(round(.05 * SR), len(bed) // 4)
            for seam in range(len(bed), target, len(bed)):
                left = min(seam_fade, seam)
                right = min(seam_fade, target - seam)
                repeat[seam-left:seam] *= np.linspace(1, 0, left)
                repeat[seam:seam+right] *= np.linspace(0, 1, right)
            fade = min(round(.15 * SR), target // 2)
            repeat[:fade] *= np.linspace(0, 1, fade)
            repeat[-fade:] *= np.linspace(1, 0, fade)
            put(dialogue, repeat, by["sos_sonar"]["start"])
    # F0024: no scene music. The film uses one film-wide bed (film/music/), so the scene's own mix is dialogue + sfx only.
    wav(OUT / "scene3_dialogue_sfx.wav", dialogue)
    events.sort()
    lines = []
    for i, (a, b, label) in enumerate(events):
        nxt = next((e for e in events[i + 1:] if not e[2].startswith("sfx")), None)
        flag = " OVERLAP" if nxt and not label.startswith("sfx") and nxt[0] < b else ""
        lines.append(f"{a:8.3f} {b:8.3f}  {label}" + (f"   next: {nxt[2]} at {nxt[0]:.3f}{flag}" if nxt else ""))
    (OUT / "audio_events.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return missing


def mux(T):
    """Playable scene file = the single picture render + the dialogue/sfx stem (no scene music, F0024)."""
    raw = OUT / "scene3_picture.mp4"
    check_video(raw, T["duration"] - 1 / FPS)
    run("ffmpeg", "-v", "error", "-y", "-i", raw, "-i", OUT / "scene3_dialogue_sfx.wav", "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000", "-ac", "2",
        "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", OUT / "scene3_v3.mp4")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page-only", action="store_true", help="write/check composition without final picture/audio render")
    parser.add_argument("--audio-only", action="store_true", help="T0040: rebuild only the audio layers and the playable mp4 from the existing picture")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    raw_slots = json.loads((HERE / "slots.json").read_text(encoding="utf-8"))
    ensure_full_slots(raw_slots)
    slots = trimmed_slots(raw_slots)
    T = timeline(slots)
    if args.page_only:
        preview_narration_placeholders()
    if not args.page_only:
        preview_narration_placeholders()  # silent wavs for lines dropped in finish mode
        placeholders = [key for key in ("N5", "N5a", "N5b", "N6")
                        if narration_lines()[key].get("status") == "placeholder"
                        and not narration_lines()[key].get("dropped")]
        if placeholders:
            sys.exit("production render needs final narration: " + ", ".join(placeholders))
        required_audio = [RENDERS / "tts_itantra/tts_sos.wav"]
        absent = ["RENDERS:" + p.relative_to(RENDERS).as_posix() for p in required_audio if not p.is_file()]
        if absent:
            sys.exit("missing required speech assets: " + ", ".join(absent))
    if args.audio_only:
        missing = audio(T, slots, OUT / "sonar_work")
        mux(T)
        print(json.dumps({"duration": T["duration"], "missing": missing}))
        return
    app_still = prepare_sonar_still(slots)
    videos, stage = sonar_assets(app_still, preview_only=args.page_only)
    missing = []
    write_page(T, slots, videos, missing)
    if missing and not args.page_only:
        sys.exit("missing app slots, refusing to render: " + ", ".join(missing))
    run("hyperframes.cmd", "check", cwd=HERE)
    if not args.page_only:
        raw = OUT / "scene3_picture.mp4"
        run("hyperframes.cmd", "render", "-q", "high", "-f", "30", "-o", raw, cwd=HERE)
        check_video(raw, T["duration"] - 1 / FPS)
        missing += audio(T, slots, stage)
        mux(T)
    (OUT / "build_status.json").write_text(json.dumps({"duration": T["duration"], "missing": missing}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"duration": T["duration"], "missing": missing}))


if __name__ == "__main__":
    main()
