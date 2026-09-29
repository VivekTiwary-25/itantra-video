"""Measure clean-audio placement relative to camera sound for the six film pairs.

Runs with Python 3.2+ and the standard library. Requires ffmpeg and ffprobe on PATH.
Temporary decoded audio is kept under local/tmp and may be deleted after the run.
"""
import array
import json
import math
import os
import subprocess
import sys

RATE = 16000
STEP_MS = 10
PAIRS = [
    ('normalpart1', 'Video/normalpart1.mp4', 'Audio/normalpart1.mp3'),
    ('normalpart6', 'Video/normalpart6.mp4', 'Audio/Normalpart6.mp3'),
    ('sospart1', 'Video/sospart1.mp4', 'Audio/sospart1.mp3'),
    ('sospart2', 'Video/sospart2.mp4', 'Audio/sospart2.mp3'),
    ('vachna part1', 'Video/vachna part1.mp4', 'Audio/vachna part1.mp3'),
    ('vachna part2', 'Video/vachna part2.mp4', 'Audio/vachna part2.mp3'),
]


def run(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise RuntimeError('%s failed: %s' % (args[0], err.decode('utf-8', 'replace')[-1000:]))
    return out


def fft(a, inverse=False):
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        angle = (2 if inverse else -2) * math.pi / length
        root = complex(math.cos(angle), math.sin(angle))
        half = length >> 1
        for start in range(0, n, length):
            w = 1
            for k in range(start, start + half):
                u = a[k]
                t = w * a[k + half]
                a[k] = u + t
                a[k + half] = u - t
                w *= root
        length <<= 1
    if inverse:
        for i in range(n):
            a[i] /= n


def convolution(x, y):
    n = 1
    while n < len(x) + len(y) - 1:
        n <<= 1
    a = list(map(complex, x)) + [0j] * (n - len(x))
    b = list(map(complex, y)) + [0j] * (n - len(y))
    fft(a)
    fft(b)
    for i in range(n):
        a[i] *= b[i]
    fft(a, True)
    return [z.real for z in a[:len(x) + len(y) - 1]]


def envelope(samples, span):
    # Mean absolute band-passed amplitude; floor + log tame close-mic dynamics.
    out = []
    for start in range(0, len(samples) - span + 1, span):
        energy = sum(abs(v) for v in samples[start:start + span]) / float(span)
        out.append(math.log(1 + energy))
    return out


def center(x):
    mean = sum(x) / float(len(x))
    return [v - mean for v in x]


def score_at(v, a, lag):
    start = max(0, lag)
    end = min(len(v), lag + len(a))
    if end <= start:
        return 0.0
    ai = start - lag
    sv = sa = svv = saa = sva = 0.0
    n = end - start
    for i in range(n):
        x, y = v[start + i], a[ai + i]
        sv += x
        sa += y
        svv += x*x
        saa += y*y
        sva += x*y
    cov = sva - sv*sa/n
    den = (svv - sv*sv/n) * (saa - sa*sa/n)
    return cov / math.sqrt(den) if den > 1e-12 else 0.0


def global_search(v, a):
    # FFT gives every lag's dot product. Check plausible lags with Pearson
    # correlation so a short silent overlap cannot win.
    vc, ac = center(v), center(a)
    dots = convolution(vc, list(reversed(ac)))
    min_overlap = min(len(a), len(v), max(200, int(0.4 * min(len(a), len(v)))))
    candidates = []
    for lag in range(-len(a) + min_overlap, len(v) - min_overlap + 1):
        overlap = min(len(v), lag + len(a)) - max(0, lag)
        if overlap < min_overlap:
            continue
        # Approximate normalization first; exact Pearson for the best candidates.
        candidates.append((dots[lag + len(a) - 1] / overlap, lag))
    candidates.sort(reverse=True)
    shortlist = [lag for _, lag in candidates[:40]]
    best = max(shortlist, key=lambda lag: score_at(v, a, lag))
    return best


def waveform_search(v, a, min_overlap, around=None, radius=None):
    """Find sample lag with band-passed waveform correlation (4 kHz samples)."""
    vc, ac = center(v), center(a)
    dots = convolution(vc, list(reversed(ac)))
    scored = []
    for lag in range(-len(a)+min_overlap, len(v)-min_overlap+1):
        if around is not None and abs(lag-around) > radius:
            continue
        overlap = min(len(v), lag+len(a)) - max(0, lag)
        scored.append((abs(dots[lag+len(a)-1])/math.sqrt(overlap), lag))
    scored.sort(reverse=True)
    candidates = [lag for _, lag in scored[:20]]
    best = max(candidates, key=lambda lag: abs(score_at(v, a, lag)))
    best_score = abs(score_at(v, a, best))
    alternative_lags = [lag for _, lag in scored if abs(lag-best) > 800][:30]
    alternatives = [abs(score_at(v, a, lag)) for lag in alternative_lags]
    second = max(alternatives) if alternatives else 0.0
    return best, best_score, second


def refine(v1, a1, coarse_ms, start_ms=None, end_ms=None, radius_ms=20):
    if start_ms is None:
        start_ms = max(0, -coarse_ms)
    if end_ms is None:
        end_ms = min(len(a1), len(v1) - coarse_ms)
    start_ms = max(start_ms, 0)
    end_ms = min(end_ms, len(a1))
    # Slice to a fixed clean-audio window, preserving its original time origin.
    piece = a1[start_ms:end_ms]
    scores = []
    for lag in range(coarse_ms - radius_ms, coarse_ms + radius_ms + 1):
        scores.append((score_at(v1, piece, lag + start_ms), lag))
    return max(scores)[1], max(scores)[0]


def local_search(v, a, start, end, center_lag, radius=50):
    piece = a[start:end]
    scores = [(score_at(v, piece, lag + start), lag)
              for lag in range(center_lag - radius, center_lag + radius + 1)]
    return max(scores)[1]


def decode(src, dest):
    run(['ffmpeg', '-nostdin', '-y', '-v', 'error', '-i', src, '-vn', '-ac', '1',
         '-ar', str(RATE), '-af', 'highpass=f=300,lowpass=f=3400',
         '-f', 's16le', '-acodec', 'pcm_s16le', dest])
    with open(dest, 'rb') as f:
        data = array.array('h')
        data.frombytes(f.read())
    if sys.byteorder != 'little':
        data.byteswap()
    return data


def source_duration(src):
    return float(run(['ffprobe', '-v', 'error', '-show_entries',
                      'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                      src]).decode('ascii').strip())


def one(root, tmp, pair, video, audio):
    vsrc = os.path.join(root, *video.split('/'))
    asrc = os.path.join(root, *audio.split('/'))
    if not os.path.isfile(vsrc) or not os.path.isfile(asrc):
        raise RuntimeError('Missing source for ' + pair)
    safe = pair.replace(' ', '_')
    vs = decode(vsrc, os.path.join(tmp, safe + '-camera.pcm'))
    als = decode(asrc, os.path.join(tmp, safe + '-clean.pcm'))
    v4, a4 = vs[::4], als[::4]
    wlag, wpeak, wsecond = waveform_search(
        v4, a4, min(len(v4), len(a4), max(8000, int(0.4*min(len(v4), len(a4))))))
    v1, a1 = envelope(vs, 16), envelope(als, 16)
    v10 = [sum(v1[i:i+10])/10 for i in range(0, len(v1)-9, 10)]
    a10 = [sum(a1[i:i+10])/10 for i in range(0, len(a1)-9, 10)]
    coarse = global_search(v10, a10)
    # Search the millisecond envelope across the common recording span.
    offset_ms, best_score = refine(v1, a1, coarse*10)
    wave_at_envelope = abs(score_at(v4, a4, int(round(offset_ms*4))))
    # Confidence compares the best full-span match with every other distinct
    # alignment, excluding a 200 ms neighborhood of the winner.
    min_overlap = min(len(a10), len(v10), max(200, int(0.4 * min(len(a10), len(v10)))))
    alternatives = []
    for lag in range(-len(a10)+min_overlap, len(v10)-min_overlap+1):
        if abs(lag*10 - offset_ms) > 200:
            alternatives.append(score_at(v10, a10, lag))
    second = max(alternatives) if alternatives else 0.0
    peak = score_at(v10, a10, int(round(offset_ms/10.0)))
    envelope_ratio = peak / second if second > 0 else float('inf')
    # For normalpart1, the camera and clean waveforms have virtually no
    # sample-level coherence at the strong envelope match. Use the envelope
    # and flag this in the written verdict; elsewhere the waveform is sharper.
    envelope_only = (peak >= 0.6 and wave_at_envelope < 0.05 and
                     wpeak/max(wsecond, 1e-9) < 1.4)
    if not envelope_only:
        offset_ms = int(round(wlag/4.0))
    ratio = envelope_ratio if envelope_only else wpeak/max(wsecond, 1e-9)
    confidence = 'high' if ratio >= 2 else 'medium' if ratio >= 1.4 else 'low'
    # Divide the portion of clean audio that actually overlaps the video.
    common_start = max(0, -offset_ms)
    common_end = min(len(a1), len(v1)-offset_ms)
    third = (common_end-common_start)//3
    first_start, first_end = common_start, common_start+third
    last_start, last_end = common_end-third, common_end
    if envelope_only:
        first_coarse = local_search(v10, a10, first_start//10, first_end//10,
                                    int(round(offset_ms/10.0)))
        last_coarse = local_search(v10, a10, last_start//10, last_end//10,
                                   int(round(offset_ms/10.0)))
        first_ms, _ = refine(v1, a1, first_coarse*10, first_start, first_end)
        last_ms, _ = refine(v1, a1, last_coarse*10, last_start, last_end)
    else:
        regional = []
        for start, end in ((first_start, first_end), (last_start, last_end)):
            # Leave 0.5 s on both sides so every candidate is fully in video.
            start4 = (start+500)//4
            end4 = (end-500)//4
            if end4-start4 < 1000:
                start4, end4 = start//4, end//4
            segment = a4[start4:end4]
            region_lag, _, _ = waveform_search(v4, segment, len(segment),
                                                 wlag+start4, 2000)
            regional.append(int(round((region_lag-start4)/4.0)))
        first_ms, last_ms = regional
    vdur = source_duration(vsrc)
    adur = source_duration(asrc)
    before = max(0.0, -offset_ms/1000.0)
    after = max(0.0, offset_ms/1000.0 + adur - vdur)
    outside = []
    if before > 0.0005:
        outside.append('first %.3f s before video start' % before)
    if after > 0.0005:
        outside.append('last %.3f s after video end' % after)
    if not outside:
        outside = ['none']
    return dict(pair=pair, video='FOOTAGE:'+video, audio='FOOTAGE:'+audio,
                offset_s=offset_ms/1000.0, confidence=confidence,
                peak_ratio=round(ratio, 3), drift_first_s=first_ms/1000.0,
                drift_last_s=last_ms/1000.0, drift_ms=last_ms-first_ms,
                clean_outside_video='; '.join(outside))


def main():
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config = json.load(open(os.path.join(repo, 'machine.local.json')))
    root = os.environ.get('FOOTAGE_ROOT') or config['footage_root']
    tmp = os.path.join(repo, 'local', 'tmp', 'T0002')
    if not os.path.isdir(tmp):
        os.makedirs(tmp)
    results = []
    for pair, video, audio in PAIRS:
        print('Measuring ' + pair)
        sys.stdout.flush()
        results.append(one(root, tmp, pair, video, audio))
        print(json.dumps(results[-1], sort_keys=True))
        sys.stdout.flush()
    out = os.path.join(repo, 'results', 'T0002', 'sync.json')
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main()
