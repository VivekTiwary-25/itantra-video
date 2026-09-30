"""Build scene 2 from the approved cut. Run from anywhere: python film/scene2/main/build.py."""
import json
import html as htmlmod
import hashlib
import math
import os
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = REPO / "local/renders/scene2"
FPS = 30
SR = 48000
CHAIN = (
    "pan=mono|c0=0.5*c0+0.5*c1,highpass=f=100:poles=2,highpass=f=100:poles=2,"
    "arnndn=m=local/models/rnnoise/cb.rnnn,arnndn=m=local/models/rnnoise/sh.rnnn:mix=0.6,"
    "afftdn=nr=18:nf=-45:tn=0,agate=threshold=0.025:ratio=3:range=0.1:attack=5:release=200:knee=4,"
    "equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3000:t=q:w=1.0:g=2,deesser=i=0.3:m=0.5:f=0.5,"
    "acompressor=threshold=-20dB:ratio=2:attack=10:release=150"
)


def run(*cmd, cwd=REPO):
    p = subprocess.run([str(x) for x in cmd], cwd=cwd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"{' '.join(map(str, cmd))[:250]}\n{p.stderr[-2500:]}")
    return p


def link_asset(path, name=None):
    assets = HERE / "assets"
    assets.mkdir(exist_ok=True)
    target = assets / (name or Path(path).name)
    if target.exists():
        if os.path.samefile(path, target):
            return f"assets/{target.name}"
        target.unlink()
    try:
        os.link(path, target)
    except OSError:
        shutil.copyfile(path, target)
    return f"assets/{target.name}"


def grade():
    s = (REPO / "film/scene1/grades.sh").read_text(encoding="utf-8")
    return re.search(r'^GRADE_V1="(.*)"$', s, re.M).group(1)


def make_plate(src, dst, start, duration):
    if dst.exists() and dst.stat().st_mtime >= max(Path(src).stat().st_mtime, (REPO / "film/scene1/grades.sh").stat().st_mtime):
        return
    run("ffmpeg", "-v", "error", "-y", "-ss", start, "-t", duration, "-i", src,
        "-vf", f"fps=30,scale=1920:1080:flags=lanczos,{grade()},format=yuv420p",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-movflags", "+faststart", dst)


def still(src, dst, at=0):
    if not dst.exists() or dst.stat().st_mtime < Path(src).stat().st_mtime:
        run("ffmpeg", "-v", "error", "-y", "-ss", at, "-i", src, "-frames:v", "1", "-q:v", "3", dst)


def stage_sonar():
    h = hashlib.sha256()
    sources = [REPO / "film/scene1/grades.sh", REPO / "film/vendor/gsap/gsap.min.js", REPO / "film/vendor/three/three.min.js"]
    sources += [p for base in (REPO / "film/scene2/sonar", REPO / "film/scene2/geo") for p in base.rglob("*") if p.is_file() and "assets" not in p.parts and "__pycache__" not in p.parts]
    for p in sorted(sources):
        h.update(str(p.relative_to(REPO)).encode())
        h.update(p.read_bytes())
    digest = h.hexdigest()
    marker = OUT / "sonar_source.json"
    prior = json.loads(marker.read_text(encoding="utf-8")) if marker.exists() else {}
    stage = OUT / prior.get("stage", "sonar_work") if prior.get("digest") == digest else OUT / f"sonar_work_{digest[:12]}"
    ready = OUT / "sonar/sonar_b.mp4"
    if prior.get("digest") == digest and stage.exists() and ready.exists():
        return stage
    if not stage.exists():
        (stage / "film/scene2").mkdir(parents=True)
        shutil.copytree(REPO / "film/scene2/sonar", stage / "film/scene2/sonar")
        shutil.copytree(REPO / "film/scene2/geo", stage / "film/scene2/geo")
        (stage / "film/scene1").mkdir(parents=True)
        shutil.copyfile(REPO / "film/scene1/grades.sh", stage / "film/scene1/grades.sh")
        shutil.copytree(REPO / "film/vendor", stage / "film/vendor")
        (stage / "machine.local.json").write_text((REPO / "machine.local.json").read_text(encoding="utf-8"), encoding="utf-8")
    run(sys.executable, stage / "film/scene2/sonar/build.py", cwd=stage)
    (OUT / "sonar").mkdir(exist_ok=True)
    for name in ("sonar_a", "relay_1", "relay_2", "relay_3", "sonar_b"):
        src = stage / "film/scene2/sonar" / name
        run("hyperframes.cmd", "check", cwd=src)
        run("hyperframes.cmd", "render", "-q", "high", "-f", "30", "-o", OUT / "sonar" / f"{name}.mp4", cwd=src)
    marker.write_text(json.dumps({"digest": digest, "stage": stage.name}), encoding="utf-8")
    return stage


def walk_plate(root):
    dest = OUT / "walk.mp4"
    inputs = [root / "Video/normalpart2.mp4", REPO / "results/T0006/ramp.json", REPO / "film/scene1/grades.sh"]
    if dest.exists() and dest.stat().st_mtime >= max(p.stat().st_mtime for p in inputs):
        return dest
    parts = json.loads((REPO / "results/T0006/ramp.json").read_text(encoding="utf-8"))["pieces"]
    filters = []
    for i, p in enumerate(parts):
        filters.append(f"[0:v]trim=start={p['src_start']}:end={p['src_end']},setpts=(PTS-STARTPTS)/{p['speed']},fps=30,scale=1920:1080,setsar=1[v{i}]")
    filters.append("".join(f"[v{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0,{grade()},format=yuv420p[out]")
    run("ffmpeg", "-v", "error", "-y", "-i", root / "Video/normalpart2.mp4", "-filter_complex", ";".join(filters),
        "-map", "[out]", "-frames:v", "180", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", dest)
    return dest


def slot_path(spec):
    value = spec["path"]
    relative = Path(value[8:])
    if not value.startswith("RENDERS:") or relative.is_absolute() or ".." in relative.parts:
        raise ValueError("slot paths must be RENDERS:<relative path>")
    return REPO / "local/renders" / relative


def timeline(slots):
    rows = []
    n = 0

    def add(name, seconds, **extra):
        nonlocal n
        count = round(seconds * FPS)
        rows.append({"name": name, "start": round(n / FPS, 3), "end": round((n + count) / FPS, 3), **extra})
        n += count

    add("doorway", 3.0)
    add("bench", 4.7, source="FOOTAGE:Video/normalpart1.mp4", source_in=0)
    add("vachana_send", slots["vachana_send"]["duration"], dissolve_in=0.5)
    add("vachana_send_freeze", 3.6)
    add("walk", 6.0, source="FOOTAGE:Video/normalpart2.mp4")
    add("maps", slots["maps"]["duration"])
    add("yash_before_notification", 2.65, source="FOOTAGE:Video/normalpart6.mp4", source_in=0)
    add("yash_receive", slots["yash_receive"]["duration"])
    add("yash_after_notification", 7.067, source="FOOTAGE:Video/normalpart6.mp4", source_in=3.6)
    add("yash_reply", slots["yash_reply"]["duration"])
    for name, dur in (("sonar_a", 7), ("relay_1", 6), ("relay_2", 6), ("relay_3", 6), ("sonar_b", 6)):
        add(name, dur)
    add("sonar_b_fade", 2.6)
    add("vachana_reply", slots["vachana_reply"]["duration"])
    add("end_hold", 0.5)
    by = {r["name"]: r for r in rows}
    narration = {"N1": round(by["vachana_send_freeze"]["start"] + 0.2, 3),
                 "N2": by["sonar_a"]["start"],
                 "N3": round(by["sonar_b"]["start"] + 4, 3),
                 "N4": round(by["sonar_b_fade"]["start"] + 0.3, 3)}
    return {"fps": FPS, "duration": round(n / FPS, 3), "segments": rows, "narration_starts": narration}


def video_assets(root, T, slots):
    P = OUT / "plates"
    P.mkdir(exist_ok=True)
    make_plate(root / "Video/normalpart1.mp4", P / "bench.mp4", 0, 5.2)
    make_plate(root / "Video/normalpart1.mp4", P / "bench_tail.mp4", 4.7, 6.1)
    make_plate(root / "Video/normalpart6.mp4", P / "yash_a.mp4", 0, 2.65)
    make_plate(root / "Video/normalpart6.mp4", P / "yash_c.mp4", 3.6, 7.067)
    still(P / "bench.mp4", P / "bench_start.jpg", 0)
    still(P / "bench_tail.mp4", P / "bench_end.jpg", 6.0)
    still(P / "yash_a.mp4", P / "yash_cut.jpg", 2.6)
    walk_plate(root)
    app = {}
    for name, spec in slots.items():
        source = slot_path(spec)
        if source.exists():
            still(source, P / f"{name}_last.jpg", max(0, spec["duration"] - 1 / FPS))
            app[name] = {"video": link_asset(source, f"{name}.mp4"), "still": link_asset(P / f"{name}_last.jpg")}
        else:
            app[name] = {"video": None, "still": None}
    return app


def write_page(T, app):
    shutil.copyfile(REPO / "film/vendor/gsap/gsap.min.js", HERE / "gsap.min.js")
    assets = {"bench": link_asset(OUT / "plates/bench.mp4"), "bench_tail": link_asset(OUT / "plates/bench_tail.mp4"), "bench_start": link_asset(OUT / "plates/bench_start.jpg"),
              "bench_end": link_asset(OUT / "plates/bench_end.jpg"), "yash_a": link_asset(OUT / "plates/yash_a.mp4"),
              "yash_c": link_asset(OUT / "plates/yash_c.mp4"), "yash_cut": link_asset(OUT / "plates/yash_cut.jpg"),
              "walk": link_asset(OUT / "walk.mp4"), "sonar_end": link_asset(OUT / "plates/sonar_end.jpg")}
    for name in ("sonar_a", "relay_1", "relay_2", "relay_3", "sonar_b"):
        assets[name] = link_asset(OUT / "sonar" / f"{name}.mp4")
    def bg(path):
        return f' style="background-image:url({htmlmod.escape(path, quote=True)})"' if path else ""

    clip_count = 0
    def clip(path, row, cls="full"):
        nonlocal clip_count
        clip_count += 1
        return (f'<video id="media_{clip_count}" class="clip {cls}" src="{htmlmod.escape(path, quote=True)}" '
                f'data-start="{row["start"]}" data-duration="{round(row["end"]-row["start"], 3)}" '
                'data-media-start="0" muted playsinline></video>')

    layers = []
    for row in T["segments"]:
        name = row["name"]
        if name in app:
            side = assets["bench_end"] if name == "vachana_send" else assets["yash_cut"] if name in ("yash_receive", "yash_reply") else None
            side_html = clip(assets["bench_tail"], {"start": row["start"], "end": row["start"] + 6.1}, "") if name == "vachana_send" else clip(app[name]["video"], row, "") if not side and app[name]["video"] else ""
            screen = clip(app[name]["video"], row, "") if app[name]["video"] else f'<div class="placeholder">APP: {name}</div>'
            layers.append(f'<div class="scene" id="seg_{name}"><div class="sides"{bg(side)}>{side_html}</div><div class="screen">{screen}</div></div>')
        elif name in ("walk", "yash_before_notification", "yash_after_notification", "sonar_a", "relay_1", "relay_2", "relay_3", "sonar_b"):
            key = "yash_a" if name == "yash_before_notification" else "yash_c" if name == "yash_after_notification" else name
            layers.append(f'<div class="scene" id="seg_{name}">{clip(assets[key], row)}</div>')
        elif name in ("vachana_send_freeze", "end_hold"):
            slot = "vachana_send" if name == "vachana_send_freeze" else "vachana_reply"
            side = assets["bench_end"] if slot == "vachana_send" else app[slot]["still"]
            screen = f'<div class="freeze"{bg(app[slot]["still"])}></div>' if app[slot]["still"] else f'<div class="placeholder">APP: {slot}</div>'
            layers.append(f'<div class="scene" id="seg_{name}"><div class="sides"{bg(side)}></div><div class="screen">{screen}</div></div>')
        elif name == "sonar_b_fade":
            layers.append(f'<div class="scene" id="seg_{name}" style="background:center/cover url({assets["sonar_end"]})"></div>')
    tpl = (HERE / "index.html.tpl").read_text(encoding="utf-8")
    html = tpl.replace("{{TIMELINE}}", json.dumps(T, separators=(",", ":")))
    html = html.replace("{{ASSETS}}", json.dumps(assets, separators=(",", ":")))
    html = html.replace("{{SLOTS}}", json.dumps(app, separators=(",", ":")))
    html = html.replace("{{BENCH}}", assets["bench"])
    html = html.replace("{{LAYERS}}", "\n".join(layers))
    html = html.replace("{{DURATION}}", str(T["duration"]))
    index = HERE / "index.html"
    if not index.exists() or index.read_text(encoding="utf-8") != html:
        index.write_text(html, encoding="utf-8", newline="\n")
    (HERE / "timeline.json").write_text(json.dumps(T, indent=2) + "\n", encoding="utf-8")


def pcm(path, filt=None):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path)]
    if filt:
        cmd += ["-af", filt]
    cmd += ["-ar", str(SR), "-ac", "1", "-f", "f32le", "-"]
    p = subprocess.run(cmd, cwd=REPO, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors="replace")[-1200:])
    return np.frombuffer(p.stdout, "<f4").copy()


def put(track, clip, at, gain=1):
    i = round(at * SR)
    src = max(0, -i)
    dst = max(0, i)
    n = min(len(clip) - src, len(track) - dst)
    if n > 0:
        track[dst:dst+n] += clip[src:src+n] * gain


def wav(path, samples):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(samples, -1, 1) * 32767).astype("<i2").tobytes())


def tone(seconds, f1, f2, gain):
    t = np.arange(round(seconds * SR)) / SR
    env = np.sin(np.pi * np.clip(t / seconds, 0, 1)) ** 2
    return gain * env * (np.sin(2 * np.pi * f1 * t) + 0.45 * np.sin(2 * np.pi * f2 * t))


def audio_tracks(root, T, slots, app, stage):
    n = round(T["duration"] * SR)
    by = {r["name"]: r for r in T["segments"]}
    tracks = {}
    dialogue = np.zeros(n, np.float32)
    normal = pcm(root / "Audio/normalpart1.mp3", CHAIN + ",loudnorm=I=-16:TP=-1.5:LRA=11")
    yash = pcm(root / "Audio/Normalpart6.mp3", CHAIN + ",loudnorm=I=-16:TP=-1.5:LRA=11")
    put(dialogue, normal, by["bench"]["start"] - 0.068)
    put(dialogue, yash[:round((2.65 + 0.37) * SR)], by["yash_before_notification"]["start"] - 0.370)
    put(dialogue, yash[round((3.6 + 0.37) * SR):], by["yash_after_notification"]["start"])
    tracks["dialogue"] = dialogue
    for key, start in T["narration_starts"].items():
        a = np.zeros(n, np.float32)
        put(a, pcm(OUT / "narration/david" / f"{key}.wav", "loudnorm=I=-16:TP=-1.5:LRA=11"), start)
        tracks[key] = a
    sfx = np.zeros(n, np.float32)
    sent_at = slots["vachana_send"].get("sent_at")
    put(sfx, tone(0.24, 670, 1005, 0.02), by["vachana_send"]["start"] + (12.5 if sent_at is None else sent_at))
    notify = OUT / "app/notify.wav"
    receive = slot_path(slots["yash_receive"])
    own_notification = receive.exists() and bool(run("ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=index", "-of", "csv=p=0", receive).stdout.strip())
    if not own_notification:
        put(sfx, pcm(notify) if notify.exists() else tone(0.22, 780, 1170, 0.02), by["yash_receive"]["start"])
    rng = np.random.default_rng(17)
    t = np.arange(round(1.8 * SR)) / SR
    whoosh = rng.standard_normal(len(t)).astype(np.float32)
    whoosh = np.convolve(whoosh, np.ones(32) / 32, "same") * (np.sin(np.pi * t / 1.8) ** 2) * 0.008
    put(sfx, whoosh, by["walk"]["start"] + 1.0)
    for name in ("sonar_a", "relay_1", "relay_2", "relay_3", "sonar_b"):
        put(sfx, pcm(stage / "film/scene2/sonar" / name / "assets" / f"{name}_sfx.wav"), by[name]["start"])
    tracks["sfx"] = sfx
    app_sound = np.zeros(n, np.float32)
    for name in slots:
        if app[name]["video"] and name != "maps":
            source = slot_path(slots[name])
            try:
                put(app_sound, pcm(source)[:round(slots[name]["duration"] * SR)], by[name]["start"])
            except RuntimeError:
                pass  # screen recordings can be silent
    tracks["app"] = app_sound
    music = np.zeros(n, np.float32)
    m = pcm(stage / "film/scene2/sonar/music/sonar_music.wav")
    m = m[:round(31 * SR)]
    # The supplied stem ducks its narration zones by about 10 dB; tighten the edges over 0.3 s.
    for start, end in ((0, 4.2), (29, 31)):
        a, b = round(start * SR), min(len(m), round(end * SR))
        ramp = max(1, round(0.3 * SR))
        floor = 10 ** (-2/20)
        env = np.full(b-a, floor)
        env[:min(ramp, len(env))] = np.linspace(1, floor, min(ramp, len(env)))
        env[-min(ramp, len(env)):] = np.linspace(floor, 1, min(ramp, len(env)))
        m[a:b] *= env
    put(music, m, by["sonar_a"]["start"])
    tracks["music"] = music
    for name, a in tracks.items():
        wav(OUT / f"{name}.wav", a)
    base = sum((tracks[k] for k in tracks if k != "music"), np.zeros(n, np.float32))
    wav(OUT / "mix_nomusic.wav", base)
    wav(OUT / "mix_music.wav", base + music)


def finalize(raw, mix, output):
    # AAC can overshoot a PCM true peak, so measure the encoded audio and leave limiter headroom.
    def measure(path):
        s = run("ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-").stderr
        return float(re.findall(r"I:\s+(-?\d+\.\d+) LUFS", s)[-1]), float(re.findall(r"Peak:\s+(-?\d+\.\d+) dBFS", s)[-1])

    name = output.stem
    audio = OUT / f"{name}_audio.m4a"
    gain = -16 - measure(mix)[0] + 1.6
    for _ in range(6):
        run("ffmpeg", "-v", "error", "-y", "-i", mix, "-af",
            f"volume={gain:.3f}dB,alimiter=limit=0.78:attack=2:release=50:level=false",
            "-c:a", "aac", "-b:a", "192k", audio)
        loud, peak = measure(audio)
        if abs(loud + 16) <= 0.2 and peak <= -1.5:
            break
        gain += -16 - loud
    else:
        raise RuntimeError(f"Could not meet loudness target: {loud} LUFS, {peak} dBTP")
    run("ffmpeg", "-v", "error", "-y", "-i", raw, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "copy", "-t", T_DURATION, "-movflags", "+faststart", output)


def previews(video, T):
    moments = (0, 2.0, 7.2, 12.0, 26.0, 35.0, 60.0, 67.5, 84.0, T["duration"]-1)
    dst = REPO / "results/T0007/preview"
    dst.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(moments):
        run("ffmpeg", "-v", "error", "-y", "-ss", round(t, 3), "-i", video, "-frames:v", "1",
            "-vf", "scale=960:-2", "-q:v", "3", dst / f"{i+1:02d}.jpg")


def main():
    global T_DURATION
    OUT.mkdir(parents=True, exist_ok=True)
    root = Path(json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))["footage_root"])
    slots = json.loads((HERE / "slots.json").read_text(encoding="utf-8"))
    T = timeline(slots)
    T_DURATION = T["duration"]
    assert T["segments"][-1]["end"] == T["duration"] and T["narration_starts"]["N2"] == next(r["start"] for r in T["segments"] if r["name"] == "sonar_a")
    stage = stage_sonar()
    (OUT / "plates").mkdir(exist_ok=True)
    still(OUT / "sonar/sonar_b.mp4", OUT / "plates/sonar_end.jpg", 5.8)
    app = video_assets(root, T, slots)
    write_page(T, app)
    run("hyperframes.cmd", "check", cwd=HERE)
    raw = OUT / "scene2_raw.mp4"
    if not raw.exists() or raw.stat().st_mtime < (HERE / "index.html").stat().st_mtime:
        run("hyperframes.cmd", "render", "-q", "high", "-f", "30", "-o", raw, cwd=HERE)
    audio_tracks(root, T, slots, app, stage)
    finalize(raw, OUT / "mix_music.wav", OUT / "scene2_draft_music.mp4")
    finalize(raw, OUT / "mix_nomusic.wav", OUT / "scene2_draft_nomusic.mp4")
    previews(OUT / "scene2_draft_nomusic.mp4", T)
    print(json.dumps({"duration": T_DURATION, "drafts": ["scene2_draft_music.mp4", "scene2_draft_nomusic.mp4"]}))


if __name__ == "__main__":
    main()
