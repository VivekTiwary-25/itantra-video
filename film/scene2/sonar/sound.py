"""Procedural sound for the scene 2 sonar section: one sfx stem per segment plus one music bed for all five.

Everything is synthesised with numpy/scipy from fixed seeds (no downloaded or licensed audio), so it rebuilds
bit-identically. Cue times come from cues.py, the same numbers the pictures use.
Writes <segment>_sfx.wav (48 kHz stereo) into each segment's assets/ and sonar_music.wav (31 s) into music/.
Run through build.py (step "sound"), or directly: python film/scene2/sonar/sound.py
"""
import json, subprocess, re, wave
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

import cues as C

SR = 48000
SFX_GAIN_DB = 6.0      # all sfx stems: quiet, peaks around -16 dBFS
MUSIC_LUFS = -22.0     # music bed integrated loudness (the lead ducks it further under the narrator)


# ---------------------------------------------------------------- helpers
def t_axis(d):
    return np.arange(int(round(d * SR))) / SR


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)


def db(v):
    return 10 ** (v / 20)


_IR = {}


def reverb_ir(length=2.2, seed=11, damp=3.2):
    """Stereo decaying-noise impulse response (a soft, dark room)."""
    key = (length, seed, damp)
    if key not in _IR:
        rng = np.random.default_rng(seed)
        t = t_axis(length)
        env = np.exp(-t * damp)
        ir = []
        for ch in range(2):
            n = rng.standard_normal(len(t)) * env
            n = lp(n, 3200)
            n[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
            ir.append(n / np.sqrt((n ** 2).sum()))
        _IR[key] = np.stack(ir, 1)
    return _IR[key]


def verb(mono, wet=0.35, **kw):
    ir = reverb_ir(**kw)
    out = np.stack([mono, mono], 1) * (1 - wet)
    for ch in range(2):
        out[:, ch] += fftconvolve(mono, ir[:, ch])[:len(mono)] * wet * 1.4
    return out


def place(buf, clip, at):
    """Add a stereo clip into buf starting at time `at` (clipped to the buffer)."""
    i = int(round(at * SR))
    if clip.ndim == 1:
        clip = np.stack([clip, clip], 1)
    j0 = max(0, -i)
    n = min(len(clip) - j0, len(buf) - max(i, 0))
    if n > 0:
        buf[max(i, 0):max(i, 0) + n] += clip[j0:j0 + n]


def write_wav(path, x):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    I = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
    P = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)
    return (float(I[-1]) if I else None), (float(P[-1]) if P else None)


# ---------------------------------------------------------------- sound effects
def sonar_ping(level=-22, f=392.0, seed=1):
    """Soft, low sonar ping: a pure tone with a tiny pitch settle, a low air swell under it, long dark tail."""
    d = 3.2
    t = t_axis(d)
    ph = 2 * np.pi * np.cumsum(f * (1 + 0.012 * np.exp(-t * 9))) / SR
    tone = np.sin(ph) + 0.18 * np.sin(2.003 * ph) + 0.06 * np.sin(3.01 * ph)
    env = np.clip(t / 0.012, 0, 1) * np.exp(-t * 2.6)
    tone = lp(tone * env, 1800)
    rng = np.random.default_rng(seed)
    swell = bp(rng.standard_normal(len(t)), 70, 260) * np.clip(t / 0.25, 0, 1) ** 2 * np.exp(-np.clip(t - 0.25, 0, None) * 2.2)
    x = tone * 0.8 + swell * 0.35
    out = verb(x, wet=0.5, length=2.8, damp=2.2)
    return out * db(level) / (np.abs(out).max() + 1e-9)


def glass_blip(f, level=-34):
    d = 1.4
    t = t_axis(d)
    x = np.sin(2 * np.pi * f * t) * np.clip(t / 0.004, 0, 1) * np.exp(-t * 7) + 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 12)
    out = verb(x, wet=0.45, length=1.6, damp=3.5)
    return out * db(level) / (np.abs(out).max() + 1e-9)


def whoosh(d=1.1, peak=0.55, level=-24, seed=3, lo_start=2600, lo_end=380):
    """Soft air whoosh: band-passed noise whose centre falls, swelling to `peak` then fading fast."""
    rng = np.random.default_rng(seed)
    t = t_axis(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(n)
    blk = 960
    for i in range(0, len(n), blk):
        fr = min(1, i / (peak * SR))
        fc = lo_start * (lo_end / lo_start) ** fr
        seg = bp(n[max(0, i - blk * 3):i + blk], fc * 0.55, min(fc * 1.8, SR / 2 - 100))[-len(n[i:i + blk]):]
        out[i:i + blk] = seg
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) * 7.5))
    x = out * env + lp(rng.standard_normal(len(t)), 180) * env * 0.5
    L = x
    R = np.concatenate([np.zeros(int(0.004 * SR)), x[:-int(0.004 * SR)]])
    pan = np.clip(t / d, 0, 1)
    st = np.stack([L * (1.05 - 0.1 * pan), R * (0.95 + 0.1 * pan)], 1)
    st = st + verb(x, wet=1.0, length=1.2, damp=4.5) * 0.25
    return st * db(level) / (np.abs(st).max() + 1e-9)


def tick(level=-26):
    """The soft tick when the callout line lands: a tiny woody click with a hint of pitch."""
    d = 0.6
    t = t_axis(d)
    rng = np.random.default_rng(5)
    click = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 900)
    tone = np.sin(2 * np.pi * 2350 * t) * np.exp(-t * 90) * 0.5 + np.sin(2 * np.pi * 1175 * t) * np.exp(-t * 60) * 0.35
    x = click * 0.6 + tone
    out = verb(x, wet=0.25, length=0.8, damp=7)
    return out * db(level) / (np.abs(out).max() + 1e-9)


def hush(d=0.7, level=-36, rising=False, seed=9):
    """Very soft filtered-air swell for the freeze (falling) and the return to colour (rising)."""
    rng = np.random.default_rng(seed)
    t = t_axis(d)
    x = bp(rng.standard_normal(len(t)), 200, 1400)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    if not rising:
        env *= np.exp(-t * 2)
    else:
        env *= np.clip(t / d, 0, 1)
    out = verb(x * env, wet=0.4, length=1.0, damp=5)
    return out * db(level) / (np.abs(out).max() + 1e-9)


def bell(f, level=-24, d=3.2):
    """Soft chime: a gentle FM bell."""
    t = t_axis(d)
    idx = 1.2 * np.exp(-t * 3)
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * 1.4 * t))
    x *= np.clip(t / 0.006, 0, 1) * np.exp(-t * 1.6)
    out = verb(x, wet=0.45, length=2.6, damp=2.4)
    return out * db(level) / (np.abs(out).max() + 1e-9)


def sfx_sonar_a():
    A = C.SONAR_A
    buf = np.zeros((int(C.SEG_LEN['sonar_a'] * SR), 2))
    cues = []
    for i, (_, t0, _) in enumerate(A['pulses']):
        lvl = [-26, -24, -25][i % 3]
        place(buf, sonar_ping(lvl, f=[349.2, 392.0, 349.2][i % 3], seed=i + 1), t0)
        cues.append(('sonar pulse', t0))
    notes = [659.3, 784.0, 880.0, 987.8, 1174.7]
    for (k, t0), f in zip(A['points_on'].items(), notes):
        place(buf, glass_blip(f, -36), t0)
        cues.append((f'point {k} lights', t0))
    return buf, cues


def sfx_relay(seg):
    S = C.RELAY_SHAPE
    buf = np.zeros((int(C.SEG_LEN[seg] * SR), 2))
    cues = []
    place(buf, sonar_ping(-30, f=392.0, seed=21), 0.0); cues.append(('faint sonar ping (sonar view)', 0.0))
    w = whoosh(peak=S['whoosh_peak'], seed={'relay_1': 3, 'relay_2': 4, 'relay_3': 6}[seg])
    place(buf, w, 0.0); cues.append(('dive whoosh (peak)', S['whoosh_peak']))
    place(buf, hush(0.6, -38, False, seed=7), S['freeze'] - 0.05); cues.append(('freeze: soft air settle', S['freeze']))
    place(buf, tick(-26), S['tick']); cues.append(('callout tick', S['tick']))
    place(buf, hush(0.55, -38, True, seed=8), S['undrain'][0] - 0.1); cues.append(('colour returns: soft air lift', S['undrain'][0]))
    return buf, cues


def sfx_sonar_b():
    B = C.SONAR_B
    buf = np.zeros((int(C.SEG_LEN['sonar_b'] * SR), 2))
    cues = []
    for _, t0, _ in B['pulses']:
        if t0 >= 0:
            place(buf, sonar_ping(-27, f=349.2, seed=31), t0); cues.append(('sonar pulse', t0))
    hop_notes = {'R1': 740.0, 'R2': 830.6, 'R3': 987.8}
    for a, b, t0, t1 in B['hops']:
        place(buf, whoosh(d=0.8, peak=max(0.2, t1 - t0 - 0.05), level=-38, seed=int(t0 * 100), lo_start=1800, lo_end=900), t0)
        if b in hop_notes:
            place(buf, glass_blip(hop_notes[b], -34), t1); cues.append((f'packet reaches {b}', t1))
    place(buf, bell(659.3, -24), B['arrive']); place(buf, bell(987.8, -29), B['arrive'] + 0.11)
    place(buf, sonar_ping(-30, f=293.7, seed=33), B['arrive']); cues.append(('chime: packet arrives at Y (Yash)', B['arrive']))
    # the still ending: fade the tails out before the cut point
    n0 = int((C.SEG_LEN['sonar_b'] - 0.5) * SR)
    buf[n0:] *= np.linspace(1, 0.6, len(buf) - n0)[:, None]
    return buf, cues


# ---------------------------------------------------------------- music
def saw(f, t, rng, voices=3, detune=0.006):
    out = np.zeros_like(t)
    for v in range(voices):
        fv = f * (1 + detune * (v - (voices - 1) / 2))
        ph = (fv * t + rng.random()) % 1.0
        out += 2 * ph - 1
    return out / voices


def music():
    """Low, tactical, restrained bed for sonar_a..sonar_b (31 s). D minor. Leaves room in the narration zones."""
    total = sum(C.SEG_LEN.values())
    t = t_axis(total)
    rng = np.random.default_rng(2026)
    off = {s: C.seg_offset(s) for s in C.ORDER}
    zones = [(a, b) for a, b, _ in C.music_narration_zones()]

    def zone_gain(depth_db=-7, ramp=0.6):
        g = np.ones_like(t)
        for a, b in zones:
            x = np.clip(np.minimum((t - (a - ramp)) / ramp, ((b + ramp) - t) / ramp), 0, 1)
            g = np.minimum(g, 1 - (1 - db(depth_db)) * x)
        return g

    # chord plan (root Hz, chord tones)
    D2, F2, A2, Bb1, G1, C2 = 73.42, 87.31, 110.0, 58.27, 49.0, 65.41
    plan = [  # (start, chord freqs)
        (0.0, [D2, F2 * 2, A2 * 2, D2 * 4]),            # Dm
        (off['relay_1'], [Bb1 * 2, D2 * 2, F2 * 2, Bb1 * 4]),   # Bb
        (off['relay_2'], [G1 * 2, D2 * 2, 2 * 116.54, G1 * 4]), # Gm
        (off['relay_3'], [Bb1 * 2, F2 * 2, 2 * 130.81, D2 * 4]),# Bb(add C) - lift
        (off['sonar_b'], [A2, 2 * 146.83, 2 * 164.81, A2 * 2]), # A sus4 -> resolves
        (off['sonar_b'] + 3.1, [D2, F2 * 2, A2 * 2, D2 * 4]),   # Dm on the arrival
    ]
    pad = np.zeros_like(t)
    xf = 1.2
    for i, (s0, freqs) in enumerate(plan):
        s1 = plan[i + 1][0] if i + 1 < len(plan) else total + 1
        w = np.clip((t - s0 + xf / 2) / xf, 0, 1) * np.clip((s1 + xf / 2 - t) / xf, 0, 1)
        if not w.any():
            continue
        v = sum(saw(f, t, rng) * (0.6 if k == 0 else 0.35) for k, f in enumerate(freqs))
        pad += v * w
    # slow filter movement on the pad
    pad_lo = lp(pad, 520, 2)
    pad_hi = lp(pad, 1400, 2)
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * t / 9.0)
    pad = pad_lo * (1 - 0.35 * lfo) + pad_hi * 0.35 * lfo
    pad *= np.clip(t / 5.0, 0, 1) ** 1.5                       # swell in slowly from silence under the first narration

    # sub drone following the root
    root = np.zeros_like(t)
    for i, (s0, freqs) in enumerate(plan):
        s1 = plan[i + 1][0] if i + 1 < len(plan) else total + 1
        root = np.where((t >= s0) & (t < s1), freqs[0] if freqs[0] < 100 else freqs[0] / 2, root)
    ph = 2 * np.pi * np.cumsum(root) / SR
    sub = (np.sin(ph) * 0.7 + np.sin(2 * ph) * 0.2) * (0.8 + 0.2 * np.sin(2 * np.pi * t / 6.5))
    sub = lp(sub, 160) * np.clip(t / 2.0, 0, 1)

    # tactical ostinato: muted low plucks on 16ths at 96 BPM, starting after the first narration zone
    bpm = 96.0
    step = 60 / bpm / 4
    ost = np.zeros_like(t)
    pat = [1, 0, 0.6, 0, 1, 0, 0.6, 0.35, 1, 0, 0.6, 0, 1, 0.35, 0.6, 0]
    k = 0
    pl = t_axis(0.35)
    rp = np.random.default_rng(77)
    while k * step < total:
        tk = k * step
        a = pat[k % 16]
        if a and tk >= 3.2:
            ri = [i for i, (s0, _) in enumerate(plan) if s0 <= tk][-1]
            f = plan[ri][1][0]
            f = f if f > 60 else f * 2
            f *= [1, 1, 1.5, 1, 1, 1, 1.5, 2][k % 8] if k % 16 in (2, 6, 10, 14, 7, 13) else 1
            note = (saw(f, pl, rp, 2, 0.004)) * np.exp(-pl * 16) * np.clip(pl / 0.003, 0, 1)
            note = lp(note, 900)
            place_m(ost, note * a, tk)
        k += 1
    ost *= np.clip((t - 3.2) / 2.5, 0, 1)
    # time "holds its breath" during each relay freeze: ostinato dips, returns with the colour
    hold = np.ones_like(t)
    S = C.RELAY_SHAPE
    for seg in ('relay_1', 'relay_2', 'relay_3'):
        a, b = off[seg] + S['freeze'], off[seg] + S['resume']
        x = np.clip(np.minimum((t - a) / 0.5, (b - t) / 0.5), 0, 1)
        hold = np.minimum(hold, 1 - 0.7 * x)
    ost *= hold
    # soft high tick on 8ths (clock-like), relays only, very quiet
    ticks = np.zeros_like(t)
    tt = t_axis(0.08)
    click = hp(np.random.default_rng(3).standard_normal(len(tt)), 5000) * np.exp(-tt * 180)
    k = 0
    while k * step * 2 < total:
        tk = k * step * 2
        if off['relay_1'] - 0.5 <= tk < off['sonar_b'] + 0.5:
            place_m(ticks, click * (1.0 if k % 2 == 0 else 0.55), tk)
        k += 1
    ticks *= hold

    # the packet journey in sonar_b: ostinato thins out and stops before the narration line
    b0 = off['sonar_b']
    end_ost = np.clip(1 - (t - (b0 + 2.6)) / 1.0, 0, 1)
    ost *= end_ost
    ticks *= np.clip(1 - (t - (b0 + 0.5)) / 1.0, 0, 1)

    zg = zone_gain(-10, 0.8)                                     # leave room for the narrator
    zs = zone_gain(-8, 0.8)
    sonar_b_trim = 1 - (1 - db(-3)) * np.clip((t - (b0 - 0.5)) / 1.0, 0, 1)
    mono_l = (pad * 0.30 * zg + sub * 0.32 * zs + ost * 0.33 * zg + ticks * 0.05) * sonar_b_trim
    mono_r = mono_l.copy()
    # gentle width: delay the pad on one side
    dly = int(0.011 * SR)
    pad_r = np.concatenate([np.zeros(dly), pad[:-dly]]) * 0.30 * zg * sonar_b_trim
    mono_r = mono_r - pad * 0.30 * zg * sonar_b_trim + pad_r
    st = np.stack([mono_l, mono_r], 1)
    st = st * 0.85 + verb(st.mean(1), wet=1.0, length=3.0, damp=1.6) * 0.18
    # end: resolve and settle by 31 s
    tail = np.clip((total - t) / 1.2, 0, 1) ** 1.3
    st *= tail[:, None]
    st = hp(st.T, 28).T
    return st * db(-3) / (np.abs(st).max() + 1e-9)


def place_m(buf, clip, at):
    i = int(round(at * SR))
    n = min(len(clip), len(buf) - i)
    if n > 0:
        buf[i:i + n] += clip[:n]


# ---------------------------------------------------------------- main
def build_all(seg_assets, music_dir):
    summary = {}
    makers = {'sonar_a': sfx_sonar_a, 'sonar_b': sfx_sonar_b}
    for seg in C.ORDER:
        buf, cues = (makers[seg]() if seg in makers else sfx_relay(seg))
        buf = buf * db(SFX_GAIN_DB)
        path = Path(seg_assets[seg]) / f'{seg}_sfx.wav'
        write_wav(path, buf)
        I, P = loudness(path)
        summary[seg] = {'file': f'{seg}_sfx.wav', 'len_s': round(len(buf) / SR, 3), 'lufs': I, 'peak_dbfs': P,
                        'cues': [(n, round(tc, 3)) for n, tc in cues]}
        print(seg, summary[seg])
    m = music()
    mp = Path(music_dir) / 'sonar_music.wav'
    write_wav(mp, m)
    I, P = loudness(mp)
    m = m * db(MUSIC_LUFS - I)                       # level the bed to a fixed integrated loudness
    write_wav(mp, m)
    I, P = loudness(mp)
    summary['music'] = {'file': 'sonar_music.wav', 'len_s': round(len(m) / SR, 3), 'lufs': I, 'peak_dbfs': P,
                        'narration_zones': C.music_narration_zones()}
    print('music', summary['music'])
    (Path(music_dir) / 'sound_summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
    return summary


if __name__ == '__main__':
    here = Path(__file__).resolve().parent
    build_all({s: here / s / 'assets' for s in C.ORDER}, here / 'music')
