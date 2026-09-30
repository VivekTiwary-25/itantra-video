"""Prepare Vivek's five narration lines. Run from anywhere: python film/narration/prep.py.

Defaults: read local/narration_vivek, write RENDERS:narration/vivek, and switch
film/common/narration.json only when all five output WAVs exist. --input and
--out support isolated tests; --no-switch prevents a test from changing the film.
"""

import argparse
import ast
from array import array
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import wave


REPO = Path(__file__).resolve().parents[2]
LINES = {"N1": (3.0, 3.4), "N2": (3.8, 4.2), "N3": (1.5, 1.8),
         "N5": (3.0, 3.4), "N6": (6.8, 7.2)}
FORMATS = {".m4a", ".mp3", ".wav", ".aac", ".ogg"}
NAME = re.compile(r"^(N[12356])(?:[_-].+)?$", re.IGNORECASE)
SR = 48000


def run(args):
    done = subprocess.run(args, cwd=REPO, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True)
    if done.returncode:
        raise RuntimeError(f"{Path(args[0]).name} failed: {done.stderr[-1800:]}")
    return done


def chain():
    """Read the actual scene 1 constant, without importing its build side effects."""
    tree = ast.parse((REPO / "film/scene1/build.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CHAIN" for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError("film/scene1/build.py has no literal CHAIN")


def duration(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / wav.getframerate()


def source_info(path):
    """Check decoded input for actual full-scale samples before any cleaning."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1",
                          "-ar", str(SR), "-f", "f32le", "-"], cwd=REPO,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if raw.returncode:
        raise RuntimeError(raw.stderr.decode(errors="replace")[-1000:])
    values = array("f")
    values.frombytes(raw.stdout)
    if sys.byteorder != "little":
        values.byteswap()
    if not values:
        raise RuntimeError("no decoded audio")
    # A rail run catches hard digital clipping; the count also catches
    # repeated isolated clipped peaks. A single lossy overshoot is tolerated.
    near = sum(abs(v) >= .999 for v in values)
    run_length = longest = 0
    for value in values:
        run_length = run_length + 1 if abs(value) >= .999 else 0
        longest = max(longest, run_length)
    clipped = longest >= 3 or near >= max(8, int(len(values) * .0001))
    return len(values) / SR, clipped, near, longest


def trim_ends(source, dest):
    """Keep a 30 ms margin around the first and last active 10 ms frames."""
    with wave.open(str(source), "rb") as wav:
        if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) != (1, 2, SR):
            raise RuntimeError("cleaning did not produce 48 kHz mono PCM16")
        samples = array("h")
        samples.frombytes(wav.readframes(wav.getnframes()))
    if sys.byteorder != "little":
        samples.byteswap()
    step = SR // 100
    # The scene 1 gate suppresses room tone. Require energy above -44 dBFS.
    threshold = 10 ** (-44 / 20)
    active = []
    for start in range(0, len(samples), step):
        block = samples[start:start + step]
        rms = math.sqrt(sum(v * v for v in block) / len(block)) / 32768
        if rms >= threshold:
            active.append(start)
    if not active:
        raise RuntimeError("no speech-like activity after cleaning")
    first = max(0, active[0] - 3 * step)
    last = min(len(samples), active[-1] + 4 * step)
    with wave.open(str(dest), "wb") as wav:
        wav.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        block = samples[first:last]
        if sys.byteorder != "little":
            block.byteswap()
        wav.writeframes(block.tobytes())
    return (len(samples) - (last - first)) / SR


def process_take(path, temp, audio_chain, target, maximum):
    raw_length, clipped, near, rail_run = source_info(path)
    clean = temp / "clean.wav"
    trimmed = temp / "trimmed.wav"
    # Phone recordings can be mono. Upmix before scene 1's stereo pan so the
    # same chain works for both mono and stereo source files.
    run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-af", "aformat=channel_layouts=stereo," + audio_chain,
         "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(clean)])
    removed = trim_ends(clean, trimmed)
    trimmed_length = duration(trimmed)
    tempo = min(1.06, trimmed_length / maximum) if trimmed_length > maximum else 1.0
    filters = []
    if tempo > 1.00001:
        filters.append(f"atempo={tempo:.8f}")
    filters.append("loudnorm=I=-18:TP=-1.5:LRA=11")
    final = temp / "final.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(trimmed), "-af", ",".join(filters),
         "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", str(final)])
    final_length = duration(final)
    return final, {"take": path.name, "raw_length_s": round(raw_length, 3),
                   "trimmed_length_s": round(trimmed_length, 3),
                   "silence_removed_s": round(removed, 3),
                   "final_length_s": round(final_length, 3),
                   "target_s": target, "max_s": maximum,
                   "atempo": round(tempo, 6),
                   "compression_percent": round((1 - 1 / tempo) * 100, 2),
                   "over_max": final_length > maximum + .01,
                   "clipped": clipped, "near_full_scale_samples": near,
                   "longest_full_scale_run": rail_run}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=REPO / "local/narration_vivek")
    parser.add_argument("--out", type=Path, help="output directory; default is RENDERS:narration/vivek")
    parser.add_argument("--no-switch", action="store_true", help="leave film/common/narration.json alone")
    args = parser.parse_args()
    if not shutil.which("ffmpeg"):
        parser.error("ffmpeg is not on PATH")
    if args.out is None:
        config = json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))
        output = Path(config["renders_dir"]) / "narration/vivek"
    else:
        output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=True)
    input_dir = args.input.resolve()
    candidates = {key: [] for key in LINES}
    if input_dir.is_dir():
        for path in sorted(input_dir.iterdir(), key=lambda p: p.name.casefold()):
            match = NAME.fullmatch(path.stem)
            if path.is_file() and path.suffix.casefold() in FORMATS and match:
                candidates[match.group(1).upper()].append(path)
    else:
        print("WARNING: narration input directory is missing", file=sys.stderr)

    model_paths = (REPO / "local/models/rnnoise/cb.rnnn", REPO / "local/models/rnnoise/sh.rnnn")
    have_models = all(path.is_file() for path in model_paths)
    audio_chain = chain()
    if not have_models:
        audio_chain = ",".join(item for item in audio_chain.split(",") if not item.startswith("arnndn="))
        print("WARNING: RNNoise models missing; BOTH arnndn steps are DISABLED.", file=sys.stderr)

    report = {"voice": "vivek", "rnnoise_used": have_models, "loudness_target_lufs": -18,
              "lines": {}, "missing": [], "switched": False}
    with tempfile.TemporaryDirectory(prefix="prep_", dir=output) as scratch:
        scratch = Path(scratch)
        for key, (target, maximum) in LINES.items():
            entries = []
            for index, path in enumerate(candidates[key]):
                try:
                    take_dir = scratch / f"{key}_{index}"
                    take_dir.mkdir()
                    final, info = process_take(path, take_dir, audio_chain, target, maximum)
                    info["_final"] = final
                    entries.append(info)
                except Exception as error:
                    entries.append({"take": path.name, "error": str(error)})
                    print(f"WARNING: {key} {path.name}: {error}", file=sys.stderr)
            valid = [entry for entry in entries if not entry.get("clipped") and "error" not in entry]
            chosen = min(valid, key=lambda entry: (abs(entry["trimmed_length_s"] - target),
                                                   entry["take"].casefold())) if valid else None
            if chosen:
                shutil.copyfile(chosen["_final"], output / f"{key}.wav")
                print(f"{key}: chose {chosen['take']} ({chosen['final_length_s']:.3f}s; "
                      f"target {target:.1f}s; atempo {chosen['atempo']:.4f})")
                if chosen["over_max"]:
                    print(f"WARNING: {key} STILL OVER MAX {maximum:.1f}s after 6% cap; lead must decide.",
                          file=sys.stderr)
            else:
                report["missing"].append(key)
                print(f"WARNING: {key} has no usable unclipped take", file=sys.stderr)
            for entry in entries:
                entry.pop("_final", None)
            report["lines"][key] = {"chosen": chosen["take"] if chosen else None,
                                    "target_s": target, "max_s": maximum,
                                    "takes": entries}

    # A test output never changes the live voice selection.
    production = args.out is None
    if production and not args.no_switch and not report["missing"] and all(
            (output / f"{key}.wav").is_file() for key in LINES):
        switch = REPO / "film/common/narration.json"
        switch.parent.mkdir(parents=True, exist_ok=True)
        switch.write_text('{"voice": "vivek"}\n', encoding="utf-8")
        report["switched"] = True
        print("Switched film/common/narration.json to Vivek")
    elif report["missing"]:
        print("Voice switch unchanged; missing: " + ", ".join(report["missing"]), file=sys.stderr)
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if not report["missing"] else 1


if __name__ == "__main__":
    sys.exit(main())
