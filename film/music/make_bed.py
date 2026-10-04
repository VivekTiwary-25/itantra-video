"""Render the film-wide music bed, procedurally and offline, to RENDERS:music/bed_v3.wav (48 kHz stereo).

    python film/music/make_bed.py [--cues film/music/cues.json] [--output <wav>]

Everything comes from cues.json (section starts in film seconds), so re-run it when the timeline changes.
One key throughout: D Dorian (D minor with B natural), which fits the existing UI cues in film/sound/.
Deterministic: noise comes from fixed-seed generators, so every run gives the same file.
Each section is normalised to its `lufs` target (BS.1770 K-weighted, gated) before the 2-3 s
equal-power crossfades, so section levels stay right when sounds are edited.
"""
from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path

import numpy as np
from scipy import signal

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CUES = Path(__file__).with_name("cues.json")
SR = 48000
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def hz(note: str) -> float:
    """'D3' -> frequency. Naturals only: the bed never leaves D Dorian."""
    midi = 12 * (int(note[1:]) + 1) + NAMES[note[0]]
    return 440.0 * 2 ** ((midi - 69) / 12)


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def pan(mono, p):
    """Equal-power pan, p in -1..1."""
    a = (p + 1) * np.pi / 4
    return np.column_stack((mono * np.cos(a), mono * np.sin(a)))


# ---------------------------------------------------------------- instruments
def pad(t, chords, cutoff, detune=0.004, harmonics=10, xfade=1.8, wobble=0.25):
    """Warm pad: three slightly detuned band-limited saws per note, soft low-pass by harmonic weights.
    chords = [(start_s, end_s, [notes])] in film seconds; neighbouring chords overlap by xfade."""
    out = np.zeros((len(t), 2))
    for ci, (c0, c1, notes) in enumerate(chords):
        env = smooth((t - (c0 - xfade / 2)) / xfade) * (1 - smooth((t - (c1 - xfade / 2)) / xfade))
        if ci == 0:
            env = 1 - smooth((t - (c1 - xfade / 2)) / xfade)
        if ci == len(chords) - 1:
            env = smooth((t - (c0 - xfade / 2)) / xfade) if ci else np.ones_like(t)
        live = env > 1e-4
        if not live.any():
            continue
        tl = t[live]
        for ni, note in enumerate(notes):
            f0 = hz(note)
            # slow filter movement per note
            fc = cutoff * (1 + wobble * np.sin(2 * np.pi * (0.05 + 0.013 * ni) * tl + ni))
            voice = np.zeros_like(tl)
            for d in (-detune, 0.0, detune):
                f = f0 * (1 + d)
                for n in range(1, harmonics + 1):
                    if n * f > 9000:
                        break
                    w = (1.0 / n) / (1 + (n * f / fc) ** 4)
                    voice += w * np.sin(2 * np.pi * n * f * tl + 1.7 * n + 11 * d * ni)
            voice /= 3
            amp = 1.0 / (1 + 0.35 * ni)  # upper notes a little softer
            p = ((ni % 2) * 2 - 1) * min(0.15 + 0.12 * ni, 0.6)
            out[live] += pan(voice * env[live] * amp, p)
    return out


def plucks(t, times, notes, decay=0.35, attack=0.012, bright=0.25, level=1.0, pans=None):
    """Soft rounded pulses (no click): sine + a little 2nd harmonic, gentle attack, exponential tail."""
    out = np.zeros((len(t), 2))
    t0 = t[0]
    for i, (when, note) in enumerate(zip(times, notes)):
        a = int(round((when - t0) * SR))
        n = int(decay * 6 * SR)
        lo, hi = max(a, 0), min(a + n, len(t))
        if hi <= lo:
            continue
        tt = (np.arange(lo, hi) - a) / SR
        f = hz(note) if isinstance(note, str) else note
        env = smooth(tt / attack) * np.exp(-tt / decay)
        tone = np.sin(2 * np.pi * f * tt) + bright * np.sin(4 * np.pi * f * tt) * np.exp(-tt / (decay * 0.4))
        p = pans[i % len(pans)] if pans else 0.0
        out[lo:hi] += pan(tone * env * level, p)
    return out


def sonar_blooms(t, times, f_start, f_end, length=1.6, level=1.0):
    """Low sonar bloom: a slow downward glide with a long calm tail (same feel as film/sound sos_pulse)."""
    out = np.zeros((len(t), 2))
    t0 = t[0]
    for i, when in enumerate(times):
        a = int(round((when - t0) * SR))
        n = int(length * SR)
        lo, hi = max(a, 0), min(a + n, len(t))
        if hi <= lo:
            continue
        tt = (np.arange(lo, hi) - a) / SR
        f = f_start + (f_end - f_start) * (tt / length)
        phase = 2 * np.pi * np.cumsum(f) / SR
        env = smooth(tt / 0.06) * np.exp(-tt / (length * 0.33))
        tone = np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.12 * np.sin(3 * phase)
        out[lo:hi] += pan(tone * env * level, 0.25 * np.sin(i * 1.3))
    return out


def noise_band(t, lo_hz, hi_hz, seed, rate=0.07):
    """Filtered noise 'air' with slow amplitude movement; deterministic seed."""
    rng = np.random.default_rng(seed)
    sos = signal.butter(2, [lo_hz, hi_hz], btype="band", fs=SR, output="sos")
    l = signal.sosfilt(sos, rng.standard_normal(len(t)))
    r = signal.sosfilt(sos, rng.standard_normal(len(t)))
    mov = 0.6 + 0.4 * np.sin(2 * np.pi * rate * t + seed)
    return np.column_stack((l, r)) * mov[:, None]


def drone(t, notes, trem_hz=0.3, depth=0.25):
    out = np.zeros(len(t))
    for i, note in enumerate(notes):
        f = hz(note)
        ph = 2 * np.pi * f * t
        out += (np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)) / (1 + i)
    out *= 1 - depth + depth * np.sin(2 * np.pi * trem_hz * t) ** 2
    return pan(out, 0.0)


def grid(start, end, period, offset=0.0):
    return list(np.arange(start + offset, end, period))


def chords_every(start, end, step, seq):
    out, k, s = [], 0, start
    while s < end:
        out.append((s, min(s + step, end), seq[k % len(seq)]))
        s += step
        k += 1
    return out


# ---------------------------------------------------------------- sections
def section_audio(name, t, s0, s1, cues):
    bpm = float(cues.get("pulse_bpm", 72))
    beat = 60.0 / bpm
    if name == "intro":
        # very quiet warm pad, no beat
        ch = [(s0, (s0 + s1) / 2, ["D3", "A3", "C4", "E4", "F4"]),
              ((s0 + s1) / 2, s1 + 2, ["D3", "G3", "B3", "E4"])]
        return pad(t, ch, cutoff=650) + 0.05 * noise_band(t, 250, 1200, seed=1)
    if name == "s2a":
        # light pulse under the walk: quarter notes at pulse_bpm, chords change every 8 beats
        seq = [["D3", "A3", "C4", "E4", "F4"], ["F2", "C3", "E3", "A3"],
               ["C3", "G3", "C4", "E4"], ["G2", "D3", "B3", "E4"]]
        ch = chords_every(s0 - 2, s1 + 2, 8 * beat, seq)
        times = grid(s0 - 2, s1 + 2, beat)
        roots = {0: ["D4", "A4"], 1: ["F4", "C5"], 2: ["C4", "G4"], 3: ["G4", "D5"]}
        notes = []
        for x in times:
            k = int((x - (s0 - 2)) // (8 * beat)) % 4
            notes.append(roots[k][int(round((x - s0) / beat)) % 2])
        return (pad(t, ch, cutoff=900)
                + plucks(t, times, notes, decay=0.28, level=0.22, pans=[-0.3, 0.3])
                + 0.04 * noise_band(t, 300, 1500, seed=2))
    if name == "s2b":
        # sonar: low hum + slow pulse (one bloom every 4 beats), thin pad
        ch = [(s0 - 2, s1 + 2, ["D3", "A3", "E4"])]
        blooms = grid(s0 - 2, s1 + 2, 4 * beat, offset=0.4)
        return (0.55 * pad(t, ch, cutoff=480, wobble=0.35)
                + 0.30 * drone(t, ["D2", "A2"], trem_hz=0.25)
                + sonar_blooms(t, blooms, hz("D3"), hz("D3") * 0.94, level=0.38)
                + 0.06 * noise_band(t, 200, 800, seed=3, rate=0.05))
    if name == "s3":
        # more tension: lower register, pulse ~17% faster, quiet E/F rub on top. No siren, no booms.
        fast = 60.0 / (bpm * 7 / 6)  # 84 BPM when pulse_bpm is 72
        seq = [["D2", "A2", "E3", "F3"], ["A1", "E2", "D3", "E3"],
               ["D2", "A2", "F3", "G3"], ["C2", "G2", "E3", "F3"]]
        ch = chords_every(s0 - 2, s1 + 2, 8 * fast, seq)
        times = grid(s0 - 2, s1 + 2, fast)
        notes = ["D3" if i % 2 == 0 else "A2" for i in range(len(times))]
        rub = pad(t, [(s0 - 2, s1 + 2, ["E5", "F5"])], cutoff=1400, harmonics=3, wobble=0.5)
        return (pad(t, ch, cutoff=700)
                + plucks(t, times, notes, decay=0.22, bright=0.4, level=0.30, pans=[-0.15, 0.15])
                + 0.10 * rub
                + 0.18 * drone(t, ["D2"], trem_hz=0.5, depth=0.35)
                + 0.05 * noise_band(t, 400, 2000, seed=4, rate=0.11))
    if name in ("exploded", "s4"):  # s4 (v4 recap) uses the glassy, airy exploded-view sound
        # glassy and airy: bright high pad, slow soft glass pings, high air
        ch = [(s0 - 2, s1 + 2, ["A3", "D4", "E4", "A4", "D5"])]
        times = grid(s0 - 1, s1 + 2, 1.5 * beat, offset=0.3)
        ring = ["D6", "A5", "E6", "F5", "A5", "C6"]
        return (0.8 * pad(t, ch, cutoff=2600, harmonics=6, wobble=0.15)
                + plucks(t, times, [ring[i % 6] for i in range(len(times))], decay=0.9,
                         attack=0.006, bright=0.15, level=0.10, pans=[-0.5, 0.4, -0.2, 0.55, -0.45, 0.2])
                + 0.035 * noise_band(t, 3500, 9000, seed=5, rate=0.09))
    if name == "cards":
        # rises gently, then resolves on a clean Dm(add9) chord on the closing card
        c = float(next(s for s in cues["sections"] if s["name"] == "cards").get("closing_chord_at", s0 + 8))
        mid = (s0 + c) / 2
        ch = [(s0 - 2, mid, ["F2", "C3", "E3", "A3", "C4"]),
              (mid, c, ["G2", "D3", "B3", "E4"]),
              (c, s1 + 3, ["D2", "A2", "D3", "F3", "A3", "E4"])]
        rise = 10 ** ((3.0 * smooth((t - s0) / (c - s0))) / 20)  # +3 dB into the closing chord
        open_ = pad(t, ch, cutoff=900) * (1 - smooth((t - s0) / (c - s0)))[:, None] \
            + pad(t, ch, cutoff=1500) * smooth((t - s0) / (c - s0))[:, None]
        chime = plucks(t, [c, c + 0.02], ["D5", "A5"], decay=1.4, attack=0.01, bright=0.1, level=0.09, pans=[-0.2, 0.25])
        return open_ * rise[:, None] + chime
    raise ValueError(f"unknown section {name}")


# ---------------------------------------------------------------- loudness (ITU-R BS.1770)
def k_weight(x):
    # 48 kHz K-weighting: high-shelf + high-pass (coefficients from BS.1770-4)
    b1, a1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
    b2, a2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
    return signal.lfilter(b2, a2, signal.lfilter(b1, a1, x, axis=0), axis=0)


def lufs(x):
    """Integrated loudness, 400 ms blocks / 75% overlap, absolute -70 and relative -10 LU gates."""
    y = k_weight(x)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    if len(y) < blk:
        return -120.0
    ms = np.array([np.mean(y[i:i + blk] ** 2, axis=0).sum() for i in range(0, len(y) - blk + 1, hop)])
    ld = -0.691 + 10 * np.log10(ms + 1e-20)
    g = ms[ld > -70]
    if not len(g):
        return -120.0
    rel = -0.691 + 10 * np.log10(g.mean()) - 10
    g2 = ms[(ld > -70) & (ld > rel)]
    return float(-0.691 + 10 * np.log10(g2.mean()))


def reverb_ir(seconds=2.6, seed=7):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    tt = np.arange(n) / SR
    env = np.exp(-tt / (seconds / 6.9)) * smooth(tt / 0.02)
    sos = signal.butter(1, 5500, fs=SR, output="sos")
    ir = np.column_stack([signal.sosfilt(sos, rng.standard_normal(n)) * env for _ in range(2)])
    return ir / np.sqrt((ir ** 2).sum(axis=0))


# ---------------------------------------------------------------- render
def validate(cues):
    secs = cues["sections"]
    if int(cues.get("sample_rate", SR)) != SR:
        raise ValueError("the bed renders at 48 kHz")
    if secs[0]["start"] != 0:
        raise ValueError("sections must start at film second 0")
    for a, b in zip(secs, secs[1:]):
        if abs(a["end"] - b["start"]) > 1e-6:
            raise ValueError(f"sections must be contiguous ({a['name']} -> {b['name']})")
    if not 2.0 <= float(cues.get("crossfade_seconds", 2.5)) <= 3.0:
        raise ValueError("crossfade must be 2-3 s")


def render(cues) -> tuple[np.ndarray, list[tuple[str, float]]]:
    validate(cues)
    secs = cues["sections"]
    xf = float(cues.get("crossfade_seconds", 2.5))
    total = int(round(secs[-1]["end"] * SR))
    mix = np.zeros((total, 2))
    levels = []
    for i, s in enumerate(secs):
        s0, s1 = float(s["start"]), float(s["end"])
        a = max(0, int(round((s0 - xf / 2) * SR))) if i else 0
        b = min(total, int(round((s1 + xf / 2) * SR))) if i < len(secs) - 1 else total
        t = np.arange(a, b) / SR
        audio = section_audio(s["name"], t, s0, s1, cues)
        core = (t >= s0 + (xf / 2 if i else 0)) & (t < s1 - (xf / 2 if i < len(secs) - 1 else 0))
        measured = lufs(audio[core])
        audio *= 10 ** ((float(s["lufs"]) - measured) / 20)
        # equal-power crossfade weights
        w = np.ones(len(t))
        if i:
            w *= np.sin(np.pi / 2 * np.clip((t - (s0 - xf / 2)) / xf, 0, 1))
        if i < len(secs) - 1:
            w *= np.cos(np.pi / 2 * np.clip((t - (s1 - xf / 2)) / xf, 0, 1))
        mix[a:b] += audio * w[:, None]
        levels.append((s["name"], float(s["lufs"])))

    # one shared room so the sections feel like one piece
    wet = float(cues.get("reverb_mix", 0.3))
    ir = reverb_ir()
    rev = np.column_stack([signal.fftconvolve(mix[:, c], ir[:, c])[:total] for c in range(2)])
    mix = (1 - wet) * mix + wet * rev * 1.4

    # re-trim each section to its target after the reverb (reverb shifts loudness slightly)
    # The gain curve is flat inside each section and glides linearly across each crossfade.
    gains = []
    for s in secs:
        a, b = int(s["start"] * SR), int(s["end"] * SR)
        core = slice(a + int(xf / 2 * SR), max(a + int(xf / 2 * SR) + SR, b - int(xf / 2 * SR)))
        gains.append(10 ** ((float(s["lufs"]) - lufs(mix[core])) / 20))
    tt = np.arange(total) / SR
    curve = np.full(total, gains[0])
    for i in range(1, len(secs)):
        edge = float(secs[i]["start"])
        k = np.clip((tt - (edge - xf / 2)) / xf, 0, 1)
        curve = np.where(tt >= edge - xf / 2, curve * (1 - k) + gains[i] * k, curve)
    mix *= curve[:, None]

    fin = smooth(np.arange(total) / SR / 1.5)
    fout = smooth((secs[-1]["end"] - np.arange(total) / SR) / float(cues.get("end_fade_seconds", 2.5)))
    mix *= (fin * fout)[:, None]
    return mix, levels


def write_wav(path: Path, audio: np.ndarray):
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = float(np.max(np.abs(audio)))
    if peak > 0.89:  # about -1 dBFS; the bed should be nowhere near this
        raise ValueError(f"peak {peak:.3f} too high; lower the section targets")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(audio, -1, 1) * 32767).round().astype("<i2").tobytes())


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cues", type=Path, default=DEFAULT_CUES)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    cues = json.loads(args.cues.read_text(encoding="utf-8"))
    cfg = json.loads((ROOT / "machine.local.json").read_text(encoding="utf-8"))
    out = args.output or Path(cfg["renders_dir"]) / "music" / "bed_v3.wav"
    mix, _ = render(cues)
    write_wav(out, mix)
    print(f"RENDERS:music/{out.name}" if args.output is None else f"wrote {out.name}")
    print(f"length {len(mix) / SR:.2f} s, peak {20 * np.log10(np.max(np.abs(mix))):.1f} dBFS, "
          f"integrated {lufs(mix):.1f} LUFS")
    for s in cues["sections"]:
        a, b = int(s["start"] * SR), int(s["end"] * SR)
        print(f"  {s['name']:<9} {s['start']:>6.1f}-{s['end']:<6.1f} {lufs(mix[a:b]):6.1f} LUFS (target {s['lufs']})")


if __name__ == "__main__":
    main()
