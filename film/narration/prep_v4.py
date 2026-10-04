"""One-command narration v4 pipeline (spec 005 G3). Runs on vivek-pc, outside any sandbox.

    python film/narration/prep_v4.py [--only N2a,N2b] [--no-copy]
                                     [--input local/narration_vivek] [--out <dir>] [--manifest <json>]

For every line id in film/common/narration_v4.json that has a take in local/narration_vivek/
(<id>.wav / .mp3 / .m4a / .aac / .ogg, names case-insensitive, e.g. n2a.wav):
1. Clean it with film/narration/prep.py's own tools (scene-1 voice CHAIN, clipping check), trim only the leading and
   trailing silence (80 ms margins), loudness -18 LUFS, 48 kHz mono PCM16 -> RENDERS:narration/v4/<id>.wav.
   Never time-stretched, never cut inside the speech. A take that prep.py's check calls clipped gets the 30 Sep
   fallback instead (chain + limiter, then one static gain to -18 LUFS) and the table says so.
2. Transcribe it with faster-whisper (local/models/faster-whisper-medium.en, CPU int8, word timestamps; audio decoded
   by ffmpeg into numpy, no PyAV), then write duration / text / words / status "real" into narration_v4.json.
   If faster-whisper or the model is missing, the duration is still written and the text is left for the lead.
3. Unless --no-copy: scp the new wavs to RENDERS:narration/v4/ on utkarsh-pc and yash-pc (hosts and clones from
   local/swarm/itantra-video.json, renders_dir read from each clone's machine.local.json) and to the render clone
   used by tools/render_runner.py. Unreachable machines are skipped with a warning; every ssh/scp has a timeout.
4. Prints a table: id, new duration vs the old placeholder, text.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from array import array
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SR = 48000
EXTS = (".wav", ".mp3", ".m4a", ".aac", ".ogg")
MARGIN_S = 0.080
TARGET_LUFS = -18.0
COPY_MACHINES = ("utkarsh-pc", "yash-pc")
SSH_OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10"]
CASING = [  # transcript casing fixes (spec names); conservative: only exact spoken forms
    (r"\b(?:i|eye)[\s-]?tantra\b", "iTantra"),
    (r"\bch\s?mod\s*(?:seven seven seven|7\s?7\s?7)\b", "chmod 777"),
    (r"\bs\.?\s?i\.?\s?h\.?\s?-?\s?26173\b", "SIH26173"),
    (r"\bbluetooth\s+l\.?\s?e\b\.?", "Bluetooth LE"),
    (r"\bgoogle\s+tink\b", "Google Tink"),
]


def load_prep():
    spec = importlib.util.spec_from_file_location("narration_prep", REPO / "film/narration/prep.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def renders_dir() -> Path:
    return Path(json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))["renders_dir"])


def find_take(folder: Path, line_id: str) -> Path | None:
    if not folder.is_dir():
        return None
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix.lower() in EXTS and p.stem.lower() == line_id.lower():
            return p
    return None


def ff(*args):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *map(str, args)], cwd=REPO,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)  # chain paths are repo-relative
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    return r


def lufs(path: Path) -> float:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    if not m:
        raise RuntimeError(f"could not measure loudness of {path.name}")
    return float(m[-1])


def trim_silence(src: Path, dst: Path) -> tuple[float, float]:
    """Trim only leading/trailing silence, keeping MARGIN_S around the first/last active 10 ms block."""
    with wave.open(str(src), "rb") as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 2, SR):
            raise RuntimeError("cleaning did not produce 48 kHz mono PCM16")
        s = array("h")
        s.frombytes(w.readframes(w.getnframes()))
    if sys.byteorder != "little":
        s.byteswap()
    step, thr = SR // 100, 10 ** (-44 / 20) * 32768
    active = [i for i in range(0, len(s), step)
              if (sum(v * v for v in s[i:i + step]) / max(1, len(s[i:i + step]))) ** .5 >= thr]
    if not active:
        raise RuntimeError("no speech-like activity after cleaning")
    m = int(MARGIN_S * SR)
    a, b = max(0, active[0] - m), min(len(s), active[-1] + step + m)
    out = s[a:b]
    if sys.byteorder != "little":
        out.byteswap()
    with wave.open(str(dst), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes(out.tobytes())
    return a / SR, (len(s) - b) / SR


SKIP_DENOISE = False


def voice_chain(prep) -> str:
    chain = prep.chain()
    missing = [m for m in re.findall(r"arnndn=m=([^:,]+)", chain) if not (REPO / m.strip("'\"")).is_file()]
    if missing:
        if not SKIP_DENOISE:
            raise RuntimeError(f"RNNoise model(s) missing: {missing} (they live in local/models/ on vivek-pc)")
        print(f"WARNING (test only): RNNoise model(s) missing, arnndn dropped from the chain: {missing}")
        chain = ",".join(f for f in chain.split(",") if not f.startswith("arnndn"))
    return chain


def clean_take(prep, take: Path, out: Path, tmp: Path) -> dict:
    raw_len, clipped, near, rail = prep.source_info(take)
    chain = voice_chain(prep)
    stage1, stage2 = tmp / "clean.wav", tmp / "trim.wav"
    method = "prep.py chain + loudnorm -18 LUFS"
    filt = "aformat=channel_layouts=stereo," + chain
    if clipped:  # 30 Sep fallback: limiter + one static gain instead of rejecting the take
        filt += ",alimiter=limit=0.89:attack=5:release=50:level=false"
        method = "CLIPPED take: 30 Sep fallback (chain + limiter + static gain)"
    ff("-i", take, "-af", filt, "-ar", SR, "-ac", 1, "-c:a", "pcm_s16le", stage1)
    lead, tail = trim_silence(stage1, stage2)
    if clipped:
        gain = TARGET_LUFS - lufs(stage2)
        ff("-i", stage2, "-af", f"volume={gain:.3f}dB,alimiter=limit=0.84:level=false", "-ar", SR, "-ac", 1,
           "-c:a", "pcm_s16le", out)
    else:
        ff("-i", stage2, "-af", f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11", "-ar", SR, "-ac", 1, "-c:a", "pcm_s16le", out)
    with wave.open(str(out), "rb") as w:
        dur = w.getnframes() / w.getframerate()
    return {"take": take.name, "raw_s": round(raw_len, 3), "duration": round(dur, 3), "trim_lead_s": round(lead, 3),
            "trim_tail_s": round(tail, 3), "clipped": bool(clipped), "near_full_scale": near, "method": method}


def fix_casing(text: str) -> str:
    for pat, rep in CASING:
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)
    return text.strip()


class Transcriber:
    def __init__(self, model_dir: Path):
        self.model = None
        try:
            import numpy  # noqa: F401
            from faster_whisper import WhisperModel
        except ImportError:
            print("WARNING: faster-whisper/numpy not installed: no transcription (text left empty for the lead)")
            return
        if not model_dir.is_dir():
            print(f"WARNING: model folder missing ({model_dir.relative_to(REPO) if model_dir.is_relative_to(REPO) else model_dir}): no transcription")
            return
        self.model = WhisperModel(str(model_dir), device="cpu", compute_type="int8")

    def __call__(self, wav: Path):
        if not self.model:
            return None
        import numpy as np
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        audio = np.frombuffer(raw, dtype=np.float32)
        segs, _ = self.model.transcribe(audio, language="en", word_timestamps=True, beam_size=5,
                                        condition_on_previous_text=False)
        words = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
                 for s in segs for w in (s.words or [])]
        text = fix_casing(" ".join(w["word"] for w in words))
        return text, words


# ---------------------------------------------------------------- copy to render machines
def ssh(host: str, command: str, timeout=40):
    return subprocess.run(["ssh", *SSH_OPTS, host, command], capture_output=True, text=True, timeout=timeout)


def remote_renders(host: str, repo: str) -> str | None:
    try:
        r = ssh(host, f'type "{repo}\\machine.local.json"')
    except subprocess.TimeoutExpired:
        return None
    if r.returncode:
        return None
    try:
        return json.loads(r.stdout)["renders_dir"]
    except (ValueError, KeyError):
        return None


def copy_targets(swarm_cfg: Path) -> list[tuple[str, str]]:
    """(host, clone repo) pairs: listener clones of COPY_MACHINES + the render runner's render clone."""
    out = []
    if swarm_cfg.is_file():
        for l in json.loads(swarm_cfg.read_text(encoding="utf-8")).get("listeners", []):
            if l.get("name") in COPY_MACHINES and l.get("host") and l.get("repo"):
                out.append((l["host"], l["repo"]))
    else:
        print(f"WARNING: {swarm_cfg.name} not found: only the render clone is a copy target")
    rr = (REPO / "tools/render_runner.py")
    if rr.is_file():
        src = rr.read_text(encoding="utf-8")
        m = re.search(r'HOST,\s*RDIR\s*=\s*"([^"]+)",\s*r"([^"]+)"', src)
        if m and (m.group(1), m.group(2)) not in out:
            out.append((m.group(1), m.group(2)))
    return out


def copy_out(files: list[Path], swarm_cfg: Path) -> list[str]:
    notes, done = [], set()
    for host, repo in copy_targets(swarm_cfg):
        rd = remote_renders(host, repo)
        if not rd:
            notes.append(f"SKIPPED {host} ({repo}): unreachable or no machine.local.json")
            continue
        dest = rd.rstrip("\\/") + "\\narration\\v4"
        if (host, dest.lower()) in done:
            continue
        try:
            ssh(host, f'powershell -NoProfile -Command "New-Item -ItemType Directory -Force -Path \'{dest}\' | Out-Null"')
            r = subprocess.run(["scp", "-q", *SSH_OPTS, *map(str, files), f"{host}:{dest.replace(chr(92), '/')}/"],
                               capture_output=True, text=True, timeout=300)
            ok = r.returncode == 0
        except subprocess.TimeoutExpired:
            ok = False
        notes.append(f"{'copied' if ok else 'FAILED'} {len(files)} file(s) -> {host}:RENDERS:narration/v4/")
        done.add((host, dest.lower()))
    return notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", help="comma-separated line ids, e.g. N2a,N2b")
    ap.add_argument("--no-copy", action="store_true", help="do not scp to the render machines")
    ap.add_argument("--input", type=Path, default=REPO / "local/narration_vivek")
    ap.add_argument("--out", type=Path, help="default RENDERS:narration/v4")
    ap.add_argument("--manifest", type=Path, default=REPO / "film/common/narration_v4.json")
    ap.add_argument("--model", type=Path, default=REPO / "local/models/faster-whisper-medium.en")
    ap.add_argument("--swarm", type=Path, default=REPO / "local/swarm/itantra-video.json")
    ap.add_argument("--skip-missing-denoise", action="store_true", help="TESTS ONLY: drop arnndn if its model is absent")
    args = ap.parse_args()
    global SKIP_DENOISE
    SKIP_DENOISE = args.skip_missing_denoise
    out_dir = args.out or renders_dir() / "narration" / "v4"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    lines = manifest["lines"]
    only = {x.strip().lower() for x in args.only.split(",")} if args.only else None
    prep = load_prep()
    asr = Transcriber(args.model)
    rows, written = [], []
    for line_id, entry in lines.items():
        if only and line_id.lower() not in only:
            continue
        take = find_take(args.input, line_id)
        if not take:
            rows.append((line_id, None, entry.get("duration"), "(no take yet)", ""))
            continue
        old = entry.get("duration")
        dst = out_dir / f"{line_id}.wav"
        try:
            with tempfile.TemporaryDirectory(dir=REPO / "local") as tmp:
                info = clean_take(prep, take, dst, Path(tmp))
        except RuntimeError as exc:  # one bad take never stops the others
            rows.append((line_id, None, old, f"ERROR: {str(exc).splitlines()[0][:120]}", ""))
            continue
        tr = asr(dst)
        entry["duration"] = info["duration"]
        entry["status"] = "real"
        entry["take"] = info["take"]
        entry["cleaning"] = info["method"]
        if tr:
            entry["text"], entry["words"] = tr
        written.append(dst)
        rows.append((line_id, info["duration"], old, entry.get("text") or "(not transcribed)",
                     "CLIPPED->fallback" if info["clipped"] else ""))
    args.manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{'id':<5} {'new s':>7} {'old s':>7}  text")
    for line_id, new, old, text, note in rows:
        n = f"{new:7.3f}" if new is not None else "      -"
        o = f"{old:7.3f}" if isinstance(old, (int, float)) else "      -"
        print(f"{line_id:<5} {n} {o}  {text} {note}".rstrip())
    print(f"\n{len(written)} line(s) written to {out_dir}; manifest {args.manifest.name} updated")
    if written and not args.no_copy:
        for note in copy_out(written, args.swarm):
            print(note)
    elif args.no_copy:
        print("--no-copy: render machines not updated")
    changed = sorted({lines[r[0]].get("segment", "?") for r in rows if r[1] is not None})
    if changed:
        print("Rebuild these segments (their narration changed): " + ", ".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
