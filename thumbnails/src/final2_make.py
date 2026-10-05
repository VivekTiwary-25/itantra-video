"""Final thumbnails round 2: lips pressed together, photo look (5-frame median merge + light sharpening), v2 right side."""
import subprocess, os, re
import numpy as np
from PIL import Image, ImageFilter

W = os.path.dirname(os.path.abspath(__file__))
F = os.environ.get('FOOTAGE_VIDEO', 'FOOTAGE:Video/') + '20261002_'
V2 = 'thumbnails/v2_vachana_relay_nonetwork.png'
OUTS = ['thumbnails/final']
GRADE = re.search(r'^GRADE_V1="(.*)"$', open('film/scene1/grades.sh', encoding='utf-8').read(), re.M).group(1)

# name, clip, time, scaled frame height, face y fraction, face centre in 4K
VARIANTS = [
    ('final2_1_hedge', '072440_short_intro_4', 0.20, 1650, 0.27, (1600, 1000)),
    ('final2_2_steps-phone', '073404_long_intro', 0.05, 1650, 0.27, (1912, 960)),
    ('final2_3_steps-phone-2', '073404_long_intro', 0.30, 1650, 0.27, (1912, 980)),
    ('final2_4_B-lips-closed', '073035_short_intro_2', 17.37, 1650, 0.34, (2128, 1000)),
    ('final2_5_B-start', '073035_short_intro_2', 0.73, 1650, 0.27, (2128, 1000)),
]
PW, FADE0 = 600, 340


def merged(clip, t, face):
    """median of up to 5 consecutive frames (only the ones where she is still), then the film grade"""
    out = os.path.join(W, f'm_{clip}_{t:.2f}.png')
    if os.path.exists(out):
        return Image.open(out).convert('RGB')
    fr = []
    for k in range(-2, 3):
        p = os.path.join(W, f'r_{clip}_{t:.2f}_{k}.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t + k / 30:.4f}', '-i', F + clip + '.mp4', '-frames:v', '1', p], check=True)
        fr.append(np.asarray(Image.open(p).convert('RGB')).astype(np.float32))
    import cv2
    c = fr[2]
    x, y = face
    box = (slice(y - 350, y + 350), slice(x - 350, x + 350))
    gc = cv2.cvtColor(c[box].astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    keep = [c]
    for i, f in enumerate(fr):
        if i == 2:
            continue
        gf = cv2.cvtColor(f[box].astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
        (dx, dy), _ = cv2.phaseCorrelate(gc, gf)
        M = np.float32([[1, 0, -dx], [0, 1, -dy]])
        a = cv2.warpAffine(f, M, (f.shape[1], f.shape[0]), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
        r = float(np.abs(a[box] - c[box]).mean())
        print('   frame', i - 2, 'shift', round(dx, 2), round(dy, 2), 'residual', round(r, 2))
        if r < 0:
            keep.append(a)
    m = np.median(np.stack(keep), axis=0) if len(keep) >= 3 else c
    raw = os.path.join(W, f'mr_{clip}_{t:.2f}.png')
    Image.fromarray(m.clip(0, 255).astype(np.uint8)).save(raw)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-vf', f'setsar=1,nlmeans=s=2.2:p=7:r=13,{GRADE}', out], check=True)
    print(clip, t, 'merged', len(keep), 'frames')
    return Image.open(out).convert('RGB')


v2 = np.asarray(Image.open(V2).convert('RGB')).astype(np.float32)
k = np.ones(PW, np.float32) * 0.96
k[FADE0:] = np.linspace(0.96, 0.0, PW - FADE0)
for d in OUTS:
    os.makedirs(d, exist_ok=True)
for name, clip, t, zh, fy, (fx0, fy0) in VARIANTS:
    im = merged(clip, t, (fx0, fy0))
    zw = round(zh * 16 / 9)
    big = im.resize((zw, zh), Image.LANCZOS)
    left = int(round(fx0 / im.width * zw - PW / 2)); top = int(round(fy0 / im.height * zh - fy * 720))
    left = max(0, min(zw - PW, left)); top = max(0, min(zh - 720, top))
    ph = big.crop((left, top, left + PW, top + 720)).filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))
    out = v2.copy()
    out[:, :PW] = np.asarray(ph).astype(np.float32) * k[None, :, None]
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    for d in OUTS:
        img.save(os.path.join(d, name + '.png'))

names = [v[0] for v in VARIANTS]
S = Image.new('RGB', (len(names) * 336 + 16, 180 + 32), (18, 18, 20))
for i, n in enumerate(names):
    S.paste(Image.open(os.path.join(OUTS[0], n + '.png')).resize((320, 180), Image.LANCZOS), (16 + i * 336, 16))
for d in OUTS:
    S.save(os.path.join(d, 'final2_contact_sheet.png'))
