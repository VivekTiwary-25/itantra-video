"""Procedural sound for the scene 3 SOS sonar section: one sfx stem per segment plus ONE separate music stem.

Synthesised with numpy/scipy from fixed seeds (nothing downloaded), so it rebuilds identically. Cue times come
from cues.py, the same numbers the pictures use. The music is never mixed into the sfx stems or the videos.
Writes <segment>_sfx.wav (48 kHz stereo) into each segment's assets/, and music/sos_music.wav (12.5 s).
"""
import json, re, subprocess, wave
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

import cues as C

SR = 48000
SFX_PEAK_DB = -16.0     # sfx stems: quiet (scene 2's stems peak around -16 dBFS)
MUSIC_LUFS = -22.0      # music bed, same as scene 2's


def t_axis(d):
    return np.arange(int(round(d * SR))) / SR


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)


def lp(x, f):
    return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)


def hp(x, f):
    return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)


def db(v):
    return 10 ** (v / 20)


_IR = {}


def verb(mono, wet=0.35, length=2.2, damp=3.0, seed=11):
    key = (length, damp, seed)
    if key not in _IR:
        rng = np.random.default_rng(seed)
        t = t_axis(length)
        ir = []
        for _ in range(2):
            n = lp(rng.standard_normal(len(t)) * np.exp(-t * damp), 2800)
            n[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
            ir.append(n / np.sqrt((n ** 2).sum()))
        _IR[key] = np.stack(ir, 1)
    ir = _IR[key]
    out = np.stack([mono, mono], 1) * (1 - wet)
    for ch in range(2):
        out[:, ch] += fftconvolve(mono, ir[:, ch])[:len(mono)] * wet * 1.4
    return out


def norm(x, level):
    return x * db(level) / (np.abs(x).max() + 1e-9)


def place(buf, clip, at):
    i = int(round(at * SR))
    if clip.ndim == 1:
        clip = np.stack([clip, clip], 1)
    j0 = max(0, -i)
    n = min(len(clip) - j0, len(buf) - max(i, 0))
    if n > 0:
        buf[max(i, 0):max(i, 0) + n] += clip[j0:j0 + n]


def write_wav(path, x):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())


def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    I = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
    P = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)
    return (float(I[-1]) if I else None), (float(P[-1]) if P else None)


# ---------------------------------------------------------------- sounds
def sos_pulse(level=-20, f=196.0, seed=1):
    """A red SOS wave: a soft low tone with a slow swell and a dark tail. Controlled, no boom, no click."""
    d = 2.6
    t = t_axis(d)
    ph = 2 * np.pi * np.cumsum(f * (1 - 0.03 * np.exp(-t * 6))) / SR
    tone = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.08 * np.sin(3.01 * ph)
    env = np.clip(t / 0.06, 0, 1) ** 1.5 * np.exp(-t * 2.3)
    tone = lp(tone * env, 1100)
    rng = np.random.default_rng(seed)
    swell = bp(rng.standard_normal(len(t)), 60, 220) * np.clip(t / 0.2, 0, 1) ** 2 * np.exp(-np.clip(t - 0.2, 0, None) * 2.6)
    x = hp(tone * 0.85 + swell * 0.3, 45)
    return norm(verb(x, wet=0.45, length=2.4, damp=2.4, seed=seed + 20), level)


def app_pulse(level=-26, seed=2):
    """The phone's searching pulse: a short, soft, slightly higher breath of tone."""
    d = 1.2
    t = t_axis(d)
    x = np.sin(2 * np.pi * 392 * t) * np.clip(t / 0.03, 0, 1) * np.exp(-t * 5) + 0.3 * np.sin(2 * np.pi * 587.3 * t) * np.exp(-t * 7)
    return norm(verb(lp(x, 1600), wet=0.4, length=1.4, damp=4, seed=seed), level)


def swell(d=0.9, level=-30, seed=3):
    """Soft air swell for the phone -> campus transition (rising, then gone)."""
    rng = np.random.default_rng(seed)
    t = t_axis(d)
    x = bp(rng.standard_normal(len(t)), 150, 1200) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 * np.clip(t / d, 0, 1)
    return norm(verb(x, wet=0.4, length=1.0, damp=5, seed=seed), level)


def whoosh(d=1.2, peak=0.8, level=-26, seed=4, f0=2400, f1=360):
    rng = np.random.default_rng(seed)
    t = t_axis(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(n)
    blk = 960
    for i in range(0, len(n), blk):
        fc = f0 * (f1 / f0) ** min(1, i / (peak * SR))
        out[i:i + blk] = bp(n[max(0, i - blk * 3):i + blk], fc * 0.55, min(fc * 1.8, SR / 2 - 100))[-len(n[i:i + blk]):]
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) * 7.5))
    x = out * env + lp(rng.standard_normal(len(t)), 170) * env * 0.5
    return norm(np.stack([x, np.concatenate([np.zeros(192), x[:-192]])], 1) + verb(x, 1.0, 1.2, 4.5, seed) * 0.25, level)


def found(level=-24):
    """The wave reaches Vivek: a low, warm two-note tone (a fifth), restrained, not a chime of triumph."""
    d = 2.4
    t = t_axis(d)
    x = np.zeros_like(t)
    for f, at, g in ((293.7, 0.0, 1.0), (440.0, 0.09, 0.7)):
        tt = np.clip(t - at, 0, None)
        x += g * (t >= at) * np.sin(2 * np.pi * f * tt + 0.8 * np.exp(-tt * 4) * np.sin(2 * np.pi * f * 2 * tt)) * np.clip(tt / 0.01, 0, 1) * np.exp(-tt * 2.0)
    return norm(verb(lp(x, 2400), wet=0.45, length=2.2, damp=2.6, seed=9), level)


def sfx_segment(seg):
    buf = np.zeros((int(round(C.SEG_LEN[seg] * SR)), 2))
    cues = []
    off = C.T_OFFSET[seg]
    if seg == 'sos_in':
        for i, p in enumerate(C.SOS_IN['app_pulses']):
            place(buf, app_pulse(-27, seed=2 + i), p); cues.append(('phone searching pulse', p))
        place(buf, swell(0.9, -30), C.SOS_IN['phone_out'][0] - 0.1); cues.append(('soft swell, phone into campus', C.SOS_IN['phone_out'][0]))
    # red waves (in sonar time) that start inside this segment
    for i, (t0, _) in enumerate(C.WAVES):
        at = t0 - off
        if 0 <= at < C.SEG_LEN[seg]:
            quiet = any(a <= at <= b for a, b in C.SOS_SONAR['narration']) and seg == 'sos_sonar'
            place(buf, sos_pulse(-24 if quiet else -21, f=[196.0, 185.0, 196.0, 174.6, 196.0][i % 5], seed=10 + i), at)
            cues.append(('red SOS wave', round(at, 3)))
    if seg == 'sos_sonar':
        place(buf, found(-23), C.ARRIVE); cues.append(("wave reaches Vivek: his point lights red", C.ARRIVE))
    if seg == 'sos_dive':
        place(buf, whoosh(peak=C.SOS_DIVE['whoosh_peak'], level=-26), 0.0); cues.append(('dive whoosh (peak)', C.SOS_DIVE['whoosh_peak']))
        n0 = int((C.SEG_LEN[seg] - 0.25) * SR)
        buf[n0:] *= np.linspace(1, 0.5, len(buf) - n0)[:, None]      # leave room for lab_a's notification sound
    return norm(buf, SFX_PEAK_DB), cues


def saw(f, t, rng, voices=3, detune=0.006):
    out = np.zeros_like(t)
    for v in range(voices):
        out += 2 * ((f * (1 + detune * (v - (voices - 1) / 2)) * t + rng.random()) % 1.0) - 1
    return out / voices


def music():
    """Low, tactical, restrained bed for sos_in + sos_sonar + sos_dive (12.5 s). C minor, darker than scene 2.
    A slow low heartbeat locked to the red waves; steps back under N6 (sos_sonar 1.0-7.5); lifts at the arrival."""
    total = sum(C.SEG_LEN.values())
    t = t_axis(total)
    rng = np.random.default_rng(3303)
    s_off = C.SEG_LEN['sos_in']                      # music time of sos_sonar t=0
    arrive = s_off + C.ARRIVE
    C2, Eb2, G2, Ab1, Bb1 = 65.41, 77.78, 98.0, 51.91, 58.27
    plan = [(0.0, [C2, Eb2 * 2, G2 * 2]), (s_off + 3.0, [Ab1 * 2, C2 * 2, Eb2 * 2]), (s_off + 5.6, [Bb1 * 2, Eb2 * 2, G2 * 2]),
            (arrive, [C2, G2 * 2, Eb2 * 4])]
    pad = np.zeros_like(t)
    for i, (s0, fr) in enumerate(plan):
        s1 = plan[i + 1][0] if i + 1 < len(plan) else total + 1
        w = np.clip((t - s0 + 0.6) / 1.2, 0, 1) * np.clip((s1 + 0.6 - t) / 1.2, 0, 1)
        pad += sum(saw(f, t, rng) * (0.6 if k == 0 else 0.35) for k, f in enumerate(fr)) * w
    pad = lp(pad, 600) * np.clip(t / 1.5, 0, 1) ** 1.5
    root = np.zeros_like(t)
    for i, (s0, fr) in enumerate(plan):
        s1 = plan[i + 1][0] if i + 1 < len(plan) else total + 1
        root = np.where((t >= s0) & (t < s1), fr[0] if fr[0] < 70 else fr[0] / 2, root)
    sub = lp(np.sin(2 * np.pi * np.cumsum(root) / SR), 140) * np.clip(t / 1.0, 0, 1)
    # heartbeat: a soft double low thump on every red wave (music time)
    beat = np.zeros_like(t)
    bt = t_axis(0.5)
    thump = lp(np.sin(2 * np.pi * 55 * bt) * np.exp(-bt * 14) * np.clip(bt / 0.004, 0, 1), 200)
    for t0, _ in C.WAVES:
        at = t0 + s_off
        for dt, g in ((0.0, 1.0), (0.22, 0.6)):
            i = int(round((at + dt) * SR))
            if 0 <= i < len(beat):
                n = min(len(thump), len(beat) - i); beat[i:i + n] += thump[:n] * g
    # a high, very quiet tension tone that rises into the arrival and releases on the dive
    ten = np.sin(2 * np.pi * 784 * t + 0.3 * np.sin(2 * np.pi * 0.25 * t)) * np.clip((t - (arrive - 3.0)) / 3.0, 0, 1) ** 2 * np.clip((total - t) / 1.2, 0, 1)
    # step back under N6
    g = np.ones_like(t)
    for a, b, _ in C.music_quiet_zones():
        x = np.clip(np.minimum((t - (a - 0.6)) / 0.6, ((b + 0.6) - t) / 0.6), 0, 1)
        g = np.minimum(g, 1 - (1 - db(-9)) * x)
    m = pad * 0.32 * g + sub * 0.3 * np.maximum(g, db(-5)) + beat * 0.45 * np.maximum(g, db(-4)) + ten * 0.03
    dly = int(0.011 * SR)
    st = np.stack([m, m - pad * 0.32 * g + np.concatenate([np.zeros(dly), pad[:-dly]]) * 0.32 * g], 1)
    st = st * 0.85 + verb(st.mean(1), wet=1.0, length=2.8, damp=1.8) * 0.18
    st *= (np.clip((total - t) / 0.6, 0, 1) ** 1.2)[:, None]       # settles by 12.5 s; the lab scene has no music
    st = hp(st.T, 28).T
    return norm(st, -3)


def build_all(seg_assets, music_dir):
    summary = {}
    for seg in C.ORDER:
        buf, cues = sfx_segment(seg)
        p = Path(seg_assets[seg]) / f'{seg}_sfx.wav'
        write_wav(p, buf)
        I, P = loudness(p)
        summary[seg] = {'file': p.name, 'len_s': round(len(buf) / SR, 3), 'lufs': I, 'peak_dbfs': P, 'cues': cues}
        print(seg, summary[seg])
    m = music()
    mp = Path(music_dir) / 'sos_music.wav'
    write_wav(mp, m)
    I, _ = loudness(mp)
    write_wav(mp, m * db(MUSIC_LUFS - I))
    I, P = loudness(mp)
    summary['music'] = {'file': 'sos_music.wav', 'len_s': round(len(m) / SR, 3), 'lufs': I, 'peak_dbfs': P,
                        'quiet_zones': C.music_quiet_zones()}
    print('music', summary['music'])
    (Path(music_dir) / 'sound_summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8', newline='\n')
    return summary
