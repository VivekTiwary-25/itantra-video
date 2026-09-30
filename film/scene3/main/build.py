"""Build the approved SOS cut: python film/scene3/main/build.py."""
import html
import json
import os
import re
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = REPO / "local/renders/scene3"
SR = 48000
FPS = 30
SONAR = {"sos_in": 2.0, "sos_sonar": 9.0, "sos_dive": 1.5}
CHAIN = ("pan=mono|c0=0.5*c0+0.5*c1,highpass=f=100:poles=2,highpass=f=100:poles=2,"
         "arnndn=m=local/models/rnnoise/cb.rnnn,arnndn=m=local/models/rnnoise/sh.rnnn:mix=0.6,"
         "afftdn=nr=18:nf=-45:tn=0,agate=threshold=0.025:ratio=3:range=0.1:attack=5:release=200:knee=4,"
         "equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3000:t=q:w=1.0:g=2,deesser=i=0.3:m=0.5:f=0.5,"
         "acompressor=threshold=-20dB:ratio=2:attack=10:release=150")


def run(*args, cwd=REPO):
    p = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"{' '.join(map(str, args))[:220]}\n{p.stdout[-1800:]}\n{p.stderr[-1800:]}")
    return p


def render_path(value):
    if not value.startswith("RENDERS:"):
        raise ValueError("expected RENDERS: path")
    relative = Path(value[8:])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("render path must be relative")
    return REPO / "local/renders" / relative


def timeline(slots):
    rows = []
    frames = 0

    def add(name, duration, **extra):
        nonlocal frames
        count = round(duration * FPS)
        rows.append({"name": name, "start": round(frames / FPS, 3),
                     "end": round((frames + count) / FPS, 3), **extra})
        frames += count

    add("s3_open", 4.1, source="FOOTAGE:Video/sospart1.mp4", source_in=0)
    add("vachana_sos", slots["vachana_sos"]["duration"])
    for name, duration in (list(SONAR.items())[:2]):
        add(name, duration)
    add("sos_dive", SONAR["sos_dive"])
    add("lab_a", 1.6, source="FOOTAGE:Video/sospart2.mp4", source_in=3.0)
    add("vivek_sos", slots["vivek_sos"]["duration"])
    add("lab_b", 3.5, source="FOOTAGE:Video/sospart2.mp4", source_in=7.3)
    add("vivek_reply", slots["vivek_reply"]["duration"])
    add("vachana_response", slots["vachana_response"]["duration"])
    add("end_hold", 0.5)
    by = {r["name"]: r for r in rows}
    return {"fps": FPS, "duration": round(frames / FPS, 3), "segments": rows,
            "narration_starts": {"N5": 0.3, "N6": round(by["sos_sonar"]["start"] + 1.0, 3)}}


def grade():
    s = (REPO / "film/scene1/grades.sh").read_text(encoding="utf-8")
    return re.search(r'^GRADE_V1="(.*)"$', s, re.M).group(1)


def plate(source, output, start, duration):
    if output.exists() and output.stat().st_mtime >= max(source.stat().st_mtime, (REPO / "film/scene1/grades.sh").stat().st_mtime):
        return
    run("ffmpeg", "-v", "error", "-y", "-ss", start, "-t", duration, "-i", source,
        "-vf", f"fps=30,scale=1920:1080:flags=lanczos,{grade()},format=yuv420p", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", output)


def still(source, output, at=0):
    if not output.exists() or output.stat().st_mtime < source.stat().st_mtime:
        run("ffmpeg", "-v", "error", "-y", "-ss", at, "-i", source, "-frames:v", "1", "-q:v", "3", output)


def asset(source, name=None):
    folder = HERE / "assets"
    folder.mkdir(exist_ok=True)
    target = folder / (name or source.name)
    if target.exists():
        if os.path.samefile(source, target):
            return "assets/" + target.name
        target.unlink()
    try:
        os.link(source, target)
    except OSError:
        shutil.copyfile(source, target)
    return "assets/" + target.name


def sonar_assets():
    source = REPO / "film/scene3/sonar"
    videos = {}
    if source.exists():
        stage = OUT / "sonar_work"
        shutil.copytree(source, stage / "film/scene3/sonar", dirs_exist_ok=True)
        for relative in ("film/scene1/grades.sh", "machine.local.json"):
            dest = stage / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relative, dest)
        for relative in ("film/scene2/geo", "film/vendor"):
            if (REPO / relative).exists():
                shutil.copytree(REPO / relative, stage / relative, dirs_exist_ok=True)
        builder = stage / "film/scene3/sonar/build.py"
        if builder.exists():
            run("python", builder, cwd=stage)
        for name in SONAR:
            comp = stage / "film/scene3/sonar" / name
            if (comp / "index.html").exists():
                run("hyperframes.cmd", "check", cwd=comp)
                output = OUT / "sonar" / f"{name}.mp4"
                output.parent.mkdir(exist_ok=True)
                if not output.exists() or output.stat().st_mtime < max(p.stat().st_mtime for p in comp.rglob("*") if p.is_file()):
                    run("hyperframes.cmd", "render", "-q", "high", "-f", "30", "-o", output, cwd=comp)
    for name in SONAR:
        output = OUT / "sonar" / f"{name}.mp4"
        videos[name] = output if output.exists() else None
    return videos


def write_page(T, slots, videos):
    root = Path(json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))["footage_root"])
    plates = OUT / "plates"
    plates.mkdir(exist_ok=True)
    plate(root / "Video/sospart1.mp4", plates / "s3_open.mp4", 0, 4.1)
    plate(root / "Video/sospart2.mp4", plates / "lab_a.mp4", 3.0, 1.6)
    plate(root / "Video/sospart2.mp4", plates / "lab_b.mp4", 7.3, 3.401)
    still(plates / "s3_open.mp4", plates / "vachana_side.jpg", 4.0)
    still(plates / "lab_a.mp4", plates / "vivek_side.jpg", 1.5)
    still(plates / "lab_b.mp4", plates / "lab_b_last.jpg", 3.35)
    side = {"vachana_sos": asset(plates / "vachana_side.jpg"),
            "vivek_sos": asset(plates / "vivek_side.jpg"), "vivek_reply": asset(plates / "vivek_side.jpg")}
    rows = T["segments"]
    layers = []
    for row in rows:
        name = row["name"]
        if name in ("s3_open", "lab_a", "lab_b"):
            src = asset(plates / f"{name}.mp4")
            layers.append(f'<div class="scene" id="seg_{name}"><video id="video_{name}" class="full" src="{src}" data-start="{row["start"]}" data-duration="{row["end"]-row["start"]:.3f}" data-media-start="0" muted playsinline></video></div>')
        elif name in slots or name == "end_hold":
            slot = "vachana_response" if name == "end_hold" else name
            source = render_path(slots[slot]["path"])
            width = 486
            side_video = ""
            if source.exists():
                info = json.loads(run("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", source).stdout)["streams"][0]
                width = 1080 * info["width"] / info["height"]
                still(source, plates / f"{slot}_last.jpg", max(0, slots[slot]["duration"] - 1 / FPS))
                video = asset(source, f"{slot}{source.suffix}")
                if name == "end_hold":
                    screen = f'<div class="freeze" style="background-image:url({asset(plates / f"{slot}_last.jpg")})"></div>'
                else:
                    screen = f'<video id="video_{name}" src="{video}" data-start="{row["start"]}" data-duration="{row["end"]-row["start"]:.3f}" data-media-start="0" muted playsinline></video>'
                if slot == "vachana_response":
                    side[slot] = asset(plates / f"{slot}_last.jpg")
                    if name != "end_hold":
                        side_video = f'<video id="video_{name}_side" src="{video}" data-start="{row["start"]}" data-duration="{row["end"]-row["start"]:.3f}" data-media-start="0" muted playsinline></video>'
            else:
                screen = f'<div class="placeholder">APP: {slot}</div>'
            bg = side.get(slot, "")
            if name == "end_hold":
                bg = side.get("vachana_response", "")
            layers.append(f'<div class="scene" id="seg_{name}"><div class="sides" style="background-image:url({html.escape(bg, quote=True)})">{side_video}</div><div class="screen" style="width:{width:.2f}px;left:{(1920-width)/2:.2f}px">{screen}</div></div>')
        elif name in SONAR:
            source = videos[name]
            if source:
                src = asset(source, f"{name}.mp4")
                content = f'<video id="video_{name}" class="full" src="{src}" data-start="{row["start"]}" data-duration="{SONAR[name]}" data-media-start="0" muted playsinline></video>'
            else:
                content = f'<div class="sonar-card">SOS · {name.replace("_", " ").upper()}</div>'
            layers.append(f'<div class="scene" id="seg_{name}">{content}</div>')
    page = (HERE / "index.html.tpl").read_text(encoding="utf-8").replace("{{DURATION}}", str(T["duration"]))
    page = page.replace("{{TIMELINE}}", json.dumps(T, separators=(",", ":"))).replace("{{LAYERS}}", "\n".join(layers))
    index = HERE / "index.html"
    if not index.exists() or index.read_text(encoding="utf-8") != page:
        index.write_text(page, encoding="utf-8", newline="\n")
    (HERE / "timeline.json").write_text(json.dumps(T, indent=2) + "\n", encoding="utf-8")


def pcm(source, filt=None):
    cmd = ["ffmpeg", "-v", "error", "-i", str(source)]
    if filt:
        cmd += ["-af", filt]
    cmd += ["-ar", str(SR), "-ac", "1", "-f", "f32le", "-"]
    p = subprocess.run(cmd, cwd=REPO, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors="replace")[-1500:])
    return np.frombuffer(p.stdout, "<f4").copy()


def put(track, clip, at):
    i = round(at * SR)
    src, dest = max(0, -i), max(0, i)
    count = min(len(clip) - src, len(track) - dest)
    if count > 0:
        track[dest:dest + count] += clip[src:src + count]


def wav(path, samples):
    with wave.open(str(path), "wb") as out:
        out.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        out.writeframes((np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes())


def tone(seconds=0.24):
    t = np.arange(round(seconds * SR)) / SR
    return (0.018 * np.sin(np.pi * t / seconds) ** 2 *
            (np.sin(2 * np.pi * 740 * t) + 0.4 * np.sin(2 * np.pi * 1110 * t))).astype(np.float32)


def audio(T, slots):
    count = round(T["duration"] * SR)
    by = {row["name"]: row for row in T["segments"]}
    dialogue = np.zeros(count, np.float32)
    music = np.zeros(count, np.float32)
    missing = []
    root = Path(json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))["footage_root"])
    sos = pcm(root / "Audio/sospart1.mp3", f"atrim=start=0:end=4.72,asetpts=PTS-STARTPTS,{CHAIN},loudnorm=I=-16:TP=-1.5:LRA=11")
    put(dialogue, sos, by["vachana_sos"]["start"] + slots["vachana_sos"]["listen_at"])
    reply = pcm(root / "Audio/sospart2.mp3", f"atrim=start=7.54:end=10.34,asetpts=PTS-STARTPTS,{CHAIN},loudnorm=I=-16:TP=-1.5:LRA=11")
    put(dialogue, reply, by["lab_b"]["start"] + 0.305)
    put(dialogue, pcm(REPO / "local/renders/tts_itantra/tts_sos.wav"),
        by["vivek_sos"]["start"] + slots["vivek_sos"]["tts_at"])
    for key, start in T["narration_starts"].items():
        source = OUT / "narration/david" / f"{key}.wav"
        if source.exists():
            put(dialogue, pcm(source, "loudnorm=I=-16:TP=-1.5:LRA=11"), start)
        else:
            missing.append(f"narration/david/{key}.wav")
    put(dialogue, tone(), by["lab_a"]["start"] + 0.1)
    for name, spec in slots.items():
        source = render_path(spec["path"])
        if source.exists():
            try:
                clip = pcm(source)[:round(spec["duration"] * SR)]
                if name == "vachana_sos":
                    start = round(spec["listen_at"] * SR)
                    clip[start:start + len(sos)] = 0  # clean line replaces recording mic sound
                put(dialogue, clip, by[name]["start"])
            except RuntimeError:
                pass  # silent screen recording
        else:
            missing.append(spec["path"])
    for name in SONAR:
        candidates = list((OUT / "sonar_work/film/scene3/sonar").rglob(f"{name}_sfx.wav"))
        sfx = next(iter(candidates), OUT / "sonar" / f"{name}_sfx.wav")
        if sfx.exists():
            put(dialogue, pcm(sfx)[:round(SONAR[name] * SR)], by[name]["start"])
    source = next(iter((OUT / "sonar_work/film/scene3/sonar").rglob("sos_music.wav")), OUT / "sonar/sos_music.wav")
    if source.exists():
        bed = pcm(source)[:round(12.5 * SR)]
    else:
        t = np.arange(round(12.5 * SR)) / SR
        bed = (0.006 * (np.sin(2 * np.pi * 55 * t) + 0.22 * np.sin(2 * np.pi * 82.4 * t)) * np.sin(np.pi * t / 12.5) ** 2).astype(np.float32)
        bed[round(3 * SR):round(9.5 * SR)] *= 0.316
        missing.append("sonar/sos_music.wav (procedural temporary bed)")
    put(music, bed, by["sos_in"]["start"])
    wav(OUT / "scene3_dialogue_sfx.wav", dialogue)
    wav(OUT / "scene3_music.wav", music)
    wav(OUT / "scene3_mix.wav", dialogue + music)
    return missing


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    slots = json.loads((HERE / "slots.json").read_text(encoding="utf-8"))
    T = timeline(slots)
    videos = sonar_assets()
    write_page(T, slots, videos)
    run("hyperframes.cmd", "check", cwd=HERE)
    raw = OUT / "scene3_raw.mp4"
    if not raw.exists() or raw.stat().st_mtime < (HERE / "index.html").stat().st_mtime:
        run("hyperframes.cmd", "render", "-q", "high", "-f", "30", "-o", raw, cwd=HERE)
    missing = audio(T, slots)
    output = OUT / "scene3_draft.mp4"
    run("ffmpeg", "-v", "error", "-y", "-i", raw, "-i", OUT / "scene3_mix.wav",
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-af", "loudnorm=I=-15.1:TP=-2:LRA=11,alimiter=limit=0.78:attack=2:release=50:level=false",
        "-c:a", "aac", "-b:a", "192k", "-t", T["duration"], "-movflags", "+faststart", output)
    (OUT / "build_status.json").write_text(json.dumps({"missing": missing, "sonar": {k: bool(v) for k, v in videos.items()}}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"duration": T["duration"], "missing": missing, "sonar": {k: bool(v) for k, v in videos.items()}}))


if __name__ == "__main__":
    main()
