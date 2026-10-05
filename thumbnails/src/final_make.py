"""Final thumbnail: Vachana (YASH/20261002_073035.mp4, film grade GRADE_V1) on the left, v2's right side unchanged."""
import subprocess, os, re
import numpy as np, cv2
from PIL import Image

W = os.path.dirname(os.path.abspath(__file__))
V = os.environ.get('THUMB_SRC', 'FOOTAGE:Video/20261002_073035_short_intro_2.mp4')
V2 = 'thumbnails/v2_vachana_relay_nonetwork.png'
OUTS = ['thumbnails/final']
GRADE = re.search(r'^GRADE_V1="(.*)"$', open('film/scene1/grades.sh', encoding='utf-8').read(), re.M).group(1)

# name, time, zoom (frame height in px after scaling), face height position (fraction of 720)
VARIANTS = [
    ('final_A_smile', 2.567, 1600, 0.27, (2150, 940)),
    ('final_B_phone-up', 17.000, 1600, 0.27, (2120, 860)),
    ('final_C_smile-close', 2.567, 2050, 0.30, (2150, 940)),
    ('final_D_your-frame-8s', 8.000, 1600, 0.27, (2020, 920)),
]
PW, FADE0 = 600, 340   # photo width; shade 12% until 340 px, then ramps to black at 600 px (as in v2)

def frame(t):
    p = os.path.join(W, f'g_{t:.3f}.png')
    if not os.path.exists(p):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', V, '-frames:v', '1',
                        '-vf', f'scale=3840:2160,setsar=1,{GRADE}', p], check=True)
    return Image.open(p).convert('RGB')

v2 = np.asarray(Image.open(V2).convert('RGB')).astype(np.float32)
k = np.ones(PW, np.float32) * 0.88
k[FADE0:] = np.linspace(0.88, 0.0, PW - FADE0)
for d in OUTS:
    os.makedirs(d, exist_ok=True)
for name, t, zh, fy, (fx0, fy0) in VARIANTS:
    im = frame(t)
    cx, cy = fx0 / im.width, fy0 / im.height
    zw = round(zh * 16 / 9)
    big = im.resize((zw, zh), Image.LANCZOS)
    left = int(round(cx * zw - PW / 2)); top = int(round(cy * zh - fy * 720))
    left = max(0, min(zw - PW, left)); top = max(0, min(zh - 720, top))
    ph = np.asarray(big.crop((left, top, left + PW, top + 720))).astype(np.float32)
    out = v2.copy()
    out[:, :PW] = ph * k[None, :, None]
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    for d in OUTS:
        img.save(os.path.join(d, name + '.png'))
    print(name, 'crop', left, top)

# contact sheet at preview size
names = [v[0] for v in VARIANTS]
S = Image.new('RGB', (4 * 320 + 5 * 16, 180 + 32), (18, 18, 20))
for i, n in enumerate(names):
    S.paste(Image.open(os.path.join(OUTS[0], n + '.png')).resize((320, 180), Image.LANCZOS), (16 + i * 336, 16))
for d in OUTS:
    S.save(os.path.join(d, 'final_contact_sheet.png'))
