"""Scene 1 build (v2): cuts, crop/punch-ins, grade, cleaned voice, and word-timed panel cues.

Run from the repo root:  python film/scene1/build.py
Needs: machine.local.json (footage_root), ffmpeg, local/models/rnnoise/cb.rnnn
       (RNNoise model "conjoined-burgers" from github.com/GregorR/rnnoise-models),
       and film/scene1/words_p1.json / words_p2.json (word timings of the denoised clean audio).
Writes film/scene1/assets/{part1.mp4, part2.mp4, voice.wav} (git-ignored) and
film/scene1/index.html from index.html.tpl with every cue time filled in.
"""
import json, subprocess, os, re, sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
os.chdir(REPO)
S = Path('film/scene1'); A = S / 'assets'; A.mkdir(exist_ok=True)
ROOT = json.load(open('machine.local.json'))['footage_root']
FPS = 30
SR = 48000
OFF = {1: 0.571, 2: 0.389}          # clean-audio time t plays at video time t + OFF (cross-correlation, no drift)
GRADE = 'A'                         # draft choice; options in grades.sh / grade_option_*.jpg

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"failed: {' '.join(cmd)[:300]}\n{r.stderr[-2000:]}")
    return r

grades = {}
for line in open(S / 'grades.sh', encoding='utf-8'):
    m = re.match(r'^(\w+)="(.*)"\s*$', line.strip())
    if m:
        grades[m.group(1)] = m.group(2)
LOOK, MATCH2 = grades[f'GRADE_{GRADE}'], grades['MATCH2']

# ---------------------------------------------------------------- edit decision list
# Frames at 30 fps in each source clip. Cuts sit inside measured silences in the denoised clean audio.
# framing: 'base' or 'tight' (8% punch-in about her face, hides the jump).
# Part 1 base = crop 1640x922 at (280,79): removes the finger (x<=275, y<=473, video 1.2-1.9 s) for the whole shot.
P1_BASE = (280, 79, 1640, 922)
P1_TIGHT = (323, 113, 1518, 854)     # 1.08x about her face (~860,540)
P2_BASE = (0, 0, 1920, 1080)
# 1.08x punch-in. Her face moves -63 px across cut 2 and +9 px across cut 3 (template-matched), so the crop starts
# where her face lines up across cut 2 and drifts slowly (57 px over 7.8 s, hidden in the handheld motion) to line up across cut 3.
P2_TIGHT = ('14+57*t/7.8333', 37, 1778, 1000)
EDL = {
    1: [(24, 408, 'base'),           # 0.80-13.60 s  (starts after the first 0.8 s)
        (419, 564, 'tight')],        # 13.97-18.80 s ; cut 1: 0.37 s reading pause between "TTS" and "and STT"
    2: [(0, 740, 'base'),            # 0.00-24.67 s
        (764, 999, 'tight'),         # 25.47-33.30 s ; cut 2: 0.80 s pause after "again" (Vivek's note, ~0:42)
        (1010, 1113, 'base')],       # 33.67-37.10 s ; cut 3: 0.37 s pause in "text is sent ... locally"
}
RECT = {1: {'base': P1_BASE, 'tight': P1_TIGHT}, 2: {'base': P2_BASE, 'tight': P2_TIGHT}}

def seg_table():
    rows, t = [], 0.0
    for p in (1, 2):
        for a, b, fr in EDL[p]:
            rows.append(dict(part=p, vin=a / FPS, vout=b / FPS, scene=t, framing=fr))
            t += (b - a) / FPS
    return rows, t

SEGS, CUT_END = seg_table()
P1_DUR = sum((b - a) for a, b, _ in EDL[1]) / FPS

def to_scene(part, clean_t):
    vt = clean_t + OFF[part]
    segs = [s for s in SEGS if s['part'] == part]
    for s in segs:
        if vt < s['vout']:
            return s['scene'] + max(0.0, vt - s['vin'])
    s = segs[-1]
    return s['scene'] + (vt - s['vin'])

# ---------------------------------------------------------------- cues from word timings (+ energy onsets)
def load_pcm(path, sr):
    return subprocess.run(['ffmpeg', '-v', 'quiet', '-i', str(path), '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                          capture_output=True).stdout

def energy(path):
    raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-i', str(path), '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.int16) / 32768
    f = x[:len(x) // 160 * 160].reshape(-1, 160)
    e = 20 * np.log10(np.sqrt((f ** 2).mean(1)) + 1e-9)
    e = np.convolve(e, np.ones(5) / 5, 'same')
    fl, pk = np.percentile(e, 10), np.percentile(e, 90)
    return e, fl + 0.25 * (pk - fl)

def onset(part, w, E):
    """Refine a word start: the last silence->speech edge within [start-0.3, start+0.15]."""
    e, thr = E[part]
    s = w['s']
    lo, hi = max(1, int((s - 0.3) * 100)), min(len(e) - 1, int((s + 0.15) * 100))
    edges = [i for i in range(lo, hi) if e[i - 1] <= thr < e[i]]
    return edges[-1] / 100 if edges else s

# ---------------------------------------------------------------- voice
CHAIN = ("pan=mono|c0=0.5*c0+0.5*c1,highpass=f=100:poles=2,highpass=f=100:poles=2,"
         "arnndn=m=local/models/rnnoise/cb.rnnn,afftdn=nr=12:nf=-45:tn=0,"
         "agate=threshold=0.02:ratio=2:range=0.3:attack=5:release=200:knee=4,"
         "equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3000:t=q:w=1.0:g=2,deesser=i=0.3:m=0.5:f=0.5,"
         "acompressor=threshold=-20dB:ratio=2:attack=10:release=150")
SRC_A = {1: f'{ROOT}/Audio/vachna part1.mp3', 2: f'{ROOT}/Audio/vachna part2.mp3'}
SRC_V = {1: f'{ROOT}/Video/vachna part1.mp4', 2: f'{ROOT}/Video/vachna part2.mp4'}

def build_voice_parts():
    for p in (1, 2):
        sh(['ffmpeg', '-v', 'error', '-y', '-i', SRC_A[p], '-af', CHAIN, '-ar', str(SR), '-ac', '1', str(A / f'p{p}_proc.wav')])

def build_voice(total):
    out = np.zeros(int(total * SR) + SR, np.float64)
    fade = int(0.006 * SR)
    for p in (1, 2):
        x = np.frombuffer(load_pcm(A / f'p{p}_proc.wav', SR), np.int16) / 32768
        for s in (s for s in SEGS if s['part'] == p):
            c0, c1 = s['vin'] - OFF[p], s['vout'] - OFF[p]
            a, b = int(round(c0 * SR)), int(round(c1 * SR))
            seg = np.zeros(b - a)
            src_a, src_b = max(a, 0), min(b, len(x))
            if src_b > src_a:
                seg[src_a - a:src_b - a] = x[src_a:src_b]
            ramp = np.linspace(0, 1, fade)
            seg[:fade] *= ramp; seg[-fade:] *= ramp[::-1]
            o = int(round(s['scene'] * SR))
            out[o:o + len(seg)] += seg
    out = out[:int(total * SR)]
    import wave
    with wave.open(str(A / 'voice_pre.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype('<i2').tobytes())
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(A / 'voice_pre.wav'), '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True)
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])
    gain = -16.0 - I
    sh(['ffmpeg', '-v', 'error', '-y', '-i', str(A / 'voice_pre.wav'), '-af',
        f'volume={gain:.2f}dB,alimiter=limit=0.84:attack=2:release=50:level=false', '-ar', str(SR), str(A / 'voice.wav')])
    return I, gain

# ---------------------------------------------------------------- video
def build_video(p, hold_end):
    segs = EDL[p]
    n = len(segs)
    fc = [f"[0:v]fps={FPS},split={n}" + ''.join(f'[s{i}]' for i in range(n))]
    for i, (a, b, fr) in enumerate(segs):
        x, y, w, h = RECT[p][fr]
        fc.append(f"[s{i}]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS,crop={w}:{h}:x='{x}':y='{y}',"
                  f"scale=1920:1080:flags=lanczos,setsar=1[v{i}]")
    tail = (MATCH2 + ',' if p == 2 else '') + LOOK
    if hold_end > 0:
        tail += f",tpad=stop_mode=clone:stop_duration={hold_end:.3f}"
    fc.append(''.join(f'[v{i}]' for i in range(n)) + f"concat=n={n}:v=1:a=0,{tail}[out]")
    sh(['ffmpeg', '-v', 'error', '-y', '-i', SRC_V[p], '-filter_complex', ';'.join(fc), '-map', '[out]', '-an',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p',
        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart',
        str(A / f'part{p}.mp4')])

# ---------------------------------------------------------------- main
def main():
    W = {p: json.load(open(S / f'words_p{p}.json')) for p in (1, 2)}
    html_only = '--html-only' in sys.argv      # re-fill index.html from existing assets (no audio/video re-render)
    if not html_only:
        build_voice_parts()
    E = {p: energy(A / f'p{p}_proc.wav') for p in (1, 2)}

    def find(p, text, nth=1):
        k = 0
        for w in W[p]:
            if re.sub(r'[^a-z0-9]', '', w['w'].lower()) == text:
                k += 1
                if k == nth:
                    return w
        sys.exit(f'word not found: part {p} "{text}" #{nth}')

    def cue(p, text, nth=1, lead=0.12):
        return round(to_scene(p, onset(p, find(p, text, nth), E)) - lead, 3)

    last = W[2][-1]
    speech_end = round(to_scene(2, last['e']), 3)
    C = {
        # part 1 (top panel)
        'team_in': cue(1, 'we', 1, 0.25), 'team': cue(1, 'team'), 'inst': cue(1, 'national'), 'name': cue(1, 'vachana'),
        'ps_in': cue(1, 'we', 2, 0.2), 'psid': cue(1, 'problem'),
        'tts': cue(1, 'tts'), 'stt': cue(1, 'sta'), 'lowbit': cue(1, 'low'),
        'p1_end': round(to_scene(1, find(1, 'communication')['e']), 3),
        'cut_p2': round(P1_DUR, 3),
        # part 2 (right panel)
        'mean': cue(2, 'what', 1, 0.2), 'phone': cue(2, 'lets'),
        'sim': cue(2, 'sim'), 'net': cue(2, 'internet'), 'router': cue(2, 'router'),
        'travels': cue(2, 'our', 2, 0.25), 'ondevice': cue(2, 'on'), 'speech_wave': cue(2, 'speech', 1),
        'compact': cue(2, 'compact'), 'bt': cue(2, 'bluetooth'), 'relay': cue(2, 'relay'),
        'device_end': round(to_scene(2, find(2, 'device', 2)['e']), 3),
        'tts2': cue(2, 'the', 4), 'inshort': cue(2, 'so', 1, 0.2),
        'n1': cue(2, 'speech', 6), 'n2': cue(2, 'text', 6), 'n3': cue(2, 'speech', 7),
        'speech_end': speech_end,
    }
    C['door'] = round(speech_end + 0.11, 3)
    TOTAL = round(C['door'] + 3.3, 3)
    p2_len = sum((b - a) for a, b, _ in EDL[2]) / FPS
    hold = TOTAL - P1_DUR - p2_len
    C['total'] = TOTAL

    I = gain = None
    if not html_only:
        I, gain = build_voice(TOTAL)
        build_video(1, 0)
        build_video(2, hold)

    tpl = (S / 'index.html.tpl').read_text(encoding='utf-8')
    vals = {'TOTAL': TOTAL, 'P1DUR': round(P1_DUR, 3), 'P2START': round(P1_DUR, 3), 'P2DUR': round(TOTAL - P1_DUR, 3),
            'SFX_START': round(C['door'] - 0.05, 3), 'CUES': json.dumps(C)}
    for k, v in vals.items():
        tpl = tpl.replace('{{' + k + '}}', str(v))
    (S / 'index.html').write_text(tpl, encoding='utf-8')
    json.dump({'cues': C, 'segments': SEGS}, open(S / 'cues.json', 'w'), indent=1)
    print(json.dumps(C, indent=1))
    print('segments:'); [print(' ', s) for s in SEGS]
    print(f'total {TOTAL}s, part1 {P1_DUR:.3f}s, hold {hold:.3f}s, voice in {I} LUFS gain {gain} dB')

if __name__ == '__main__':
    main()
