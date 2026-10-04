"""Intro v4 audio prep, run by the lead OUTSIDE the Codex sandbox (it needs ffmpeg + the word timings).

Pieces (spec discussion/v3/005-claude-lead.md section I):
  1. short take, "I'm Vachana ... SIH26173."            (vacchna_short_intro.mp3, camera 20261002_081346_short_intro.mp4)
  2. long intro part 2 take 1, "But what does that mean?" ... "...by text-to-speech model."
     (one continuous stretch: the five kept sentences are consecutive in the take; only "So in short..." and
      "Do you think?" after it are cut)
Writes RENDERS:intro_v4/voice.wav (48 kHz mono, -16 LUFS per piece), film/intro_v3/cuts_v4.json,
film/intro_v3/words_v4.json and envelope_v4.json (film time), film/captions/v3/intro.json.
Film time zero = first frame of the short camera clip.
"""
import json, math, re, subprocess, sys, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import prep  # noqa: E402  (scene-1 chain, pcm, alignment helpers)

CFG = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
FOOT = Path(CFG["footage_root"])
OUT = Path(CFG["renders_dir"]) / "intro_v4"
SR = 48000
GAP = 0.30
LONG_AUDIO = FOOT / "Audio/vachna_south_campus_intro_part_2_take_1.mp3"
LONG_WORDS = REPO / "local/intro_words/vachna_south_campus_intro_part_2_take_1.words.json"
LONG_CAMS = ["Video/20261002_073404_long_intro.mp4", "Video/20261002_072612_long_intro_2.mp4"]
LONG_KEEP = (0.60, 24.58)            # clean-audio span of the five kept sentences (word starts/ends)
SHORT_KEEP_END = 7.02                 # end of "SIH26173." in the short take (clean seconds)


def align(video, audio):
    prep.VIDEO, prep.AUDIO = video, audio
    return prep.alignment()


def piece(audio, lo, hi, chain):
    sig = prep.pcm(audio, SR, chain)
    a, b = max(0.0, lo - 0.12), hi + 0.30
    v = sig[round(a * SR):round(b * SR)].copy()
    f = round(.03 * SR)
    v[:f] *= np.linspace(0, 1, f)
    v[-f:] *= np.linspace(1, 0, f)
    return v, a, b


def lufs(sig):
    tmp = OUT / "_measure.wav"
    write(tmp, sig)
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr)[-1])


def write(path, sig):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(sig, -1, 1) * 32767).astype("<i2").tobytes())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    chain = prep.scene1_chain()
    short_words = json.loads((HERE / "words.json").read_text(encoding="utf-8"))
    short_words = [w for w in short_words if w["e"] <= SHORT_KEEP_END + 0.01]
    long_words = [w for w in json.loads(LONG_WORDS.read_text(encoding="utf-8")) if LONG_KEEP[0] - 0.4 <= w["s"] <= LONG_KEEP[1]]

    short_al = align(FOOT / "Video/20261002_081346_short_intro.mp4", FOOT / "Audio/vacchna_short_intro.mp3")
    cands = []
    for cam in LONG_CAMS:
        r = align(FOOT / cam, LONG_AUDIO)
        dur = float(json.loads(prep.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", FOOT / cam]))["format"]["duration"])
        cands.append({"camera": cam, "duration": round(dur, 3), **r})
    best = max(cands, key=lambda c: c["correlation_peak"])

    s_sig, s_a, s_b = piece(FOOT / "Audio/vacchna_short_intro.mp3", short_words[0]["s"], SHORT_KEEP_END, chain)
    l_sig, l_a, l_b = piece(LONG_AUDIO, long_words[0]["s"], long_words[-1]["e"], chain)
    s_sig *= 10 ** ((-16 - lufs(s_sig)) / 20)
    l_sig *= 10 ** ((-16 - lufs(l_sig)) / 20)

    # film time: zero = first frame of the short camera clip (camera = clean + offset)
    s_off, l_off = short_al["offset_s"], best["offset_s"]
    p1_in = s_a + s_off
    p1_out = s_b + s_off
    p2_in = p1_out + GAP
    p2_out = p2_in + (l_b - l_a)
    if l_b + l_off > best["duration"]:
        raise SystemExit(f"long take camera too short: needs {l_b + l_off:.2f}s of {best['camera']}")
    voice = np.concatenate([s_sig, np.zeros(round(GAP * SR)), l_sig])
    voice = np.clip(voice, -0.84, 0.84)
    write(OUT / "voice.wav", voice)
    (OUT / "_measure.wav").unlink(missing_ok=True)

    cuts = {"film_zero": "first frame of FOOTAGE:Video/20261002_081346_short_intro.mp4",
            "voice_wav": "RENDERS:intro_v4/voice.wav", "voice_starts_at_film": round(p1_in, 4),
            "pieces": [
                {"name": "opening", "text": "I'm Vachana from team chmod 777 for ISRO's problem statement, SIH26173.",
                 "audio": "FOOTAGE:Audio/vacchna_short_intro.mp3", "clean_in": round(s_a, 3), "clean_out": round(s_b, 3),
                 "camera": "FOOTAGE:Video/20261002_081346_short_intro.mp4", "camera_in": round(s_a + s_off, 3), "camera_out": round(s_b + s_off, 3),
                 "film_in": round(p1_in, 3), "film_out": round(p1_out, 3), "alignment": short_al},
                {"name": "explain", "text": " ".join(w["w"] for w in long_words),
                 "audio": "FOOTAGE:" + str(LONG_AUDIO.relative_to(FOOT)).replace("\\", "/"), "clean_in": round(l_a, 3), "clean_out": round(l_b, 3),
                 "camera": "FOOTAGE:" + best["camera"], "camera_in": round(l_a + l_off, 3), "camera_out": round(l_b + l_off, 3),
                 "film_in": round(p2_in, 3), "film_out": round(p2_out, 3), "alignment": best, "camera_candidates": cands}],
            "cut_out_of_take": ["So in short, speech become text and text is sent and text again becomes speech.", "Do you think?"]}
    (HERE / "cuts_v4.json").write_text(json.dumps(cuts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fw = [{"w": w["w"], "s": round(w["s"] - s_a + p1_in, 3), "e": round(w["e"] - s_a + p1_in, 3)} for w in short_words] + \
         [{"w": w["w"], "s": round(w["s"] - l_a + p2_in, 3), "e": round(w["e"] - l_a + p2_in, 3)} for w in long_words]
    fixes = {"CH": "chmod", "mode": None, "Itantra,": "iTantra,", "Aitantra": "iTantra", "ithantra,": "iTantra,", "SIH26173.": "SIH26173."}
    out = []
    for w in fw:
        t = w["w"]
        if t in fixes:
            if fixes[t] is None:
                continue
            t = fixes[t]
        out.append({**w, "w": t})
    # merge whisper's split hyphen tokens ("on" "-device" -> "on-device")
    merged = []
    for w in out:
        if merged and w["w"].startswith("-"):
            merged[-1] = {**merged[-1], "w": merged[-1]["w"] + w["w"], "e": w["e"]}
        else:
            merged.append(dict(w))
    out = merged
    (HERE / "words_v4.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    # captions: break at sentence ends; long sentences split near the middle at a comma or word gap, max ~46 chars
    sents, cur = [], []
    for w in out:
        cur.append(w)
        if w["w"].endswith((".", "?")):
            sents.append(cur); cur = []
    if cur:
        sents.append(cur)
    def split(ws):
        t = " ".join(x["w"] for x in ws)
        if len(t) <= 46 or len(ws) < 4:
            return [ws]
        best, score = 1, 1e9
        for i in range(1, len(ws)):
            a = len(" ".join(x["w"] for x in ws[:i])); b = len(t) - a
            sc = abs(a - b) - (12 if ws[i - 1]["w"].endswith(",") else 0)
            if sc < score:
                best, score = i, sc
        return split(ws[:best]) + split(ws[best:])
    groups = [g for sw in sents for g in split(sw)]
    caps = [{"start": g[0]["s"], "end": round(g[-1]["e"] + 0.15, 3), "text": " ".join(x["w"] for x in g)} for g in groups]
    for a, b in zip(caps, caps[1:]):
        a["end"] = round(min(a["end"], b["start"] - 0.02), 3)
    (REPO / "film/captions/v3/intro.json").write_text(json.dumps(caps, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    env = []
    sig = prep.pcm(OUT / "voice.wav", SR)
    for i in range(math.ceil(len(sig) / (SR / 30))):
        b = sig[i * 1600:(i + 1) * 1600]
        env.append(round(float(np.sqrt(np.mean(b * b))), 5) if len(b) else 0)
    (HERE / "envelope_v4.json").write_text(json.dumps({"starts_at_film": round(p1_in, 4), "fps": 30, "rms": env}) + "\n", encoding="utf-8")
    print(json.dumps({"best_long_camera": best, "film_pieces": [[round(p1_in, 2), round(p1_out, 2)], [round(p2_in, 2), round(p2_out, 2)]],
                      "captions": len(caps)}, indent=1))


if __name__ == "__main__":
    main()
