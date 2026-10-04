"""Convert five HyperFrames snapshots to 1920px JPEGs and a 960px sheet.

Run after snapshot --at=0.4,1.2,1.9,2.8,3.6 --no-end -o results/F0003/preview/raw.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import shutil

REPO = Path(__file__).resolve().parents[4]
out = REPO / 'results/F0003/preview'
raw = (out / 'raw').resolve()
if not raw.is_relative_to(out.resolve()):
    raise RuntimeError('Snapshot folder escaped results/F0003/preview')
frames = sorted(raw.glob('frame-*.png'))
if len(frames) != 5:
    raise RuntimeError(f'Expected five snapshots, found {len(frames)}')
names = ['card', 'panel', 'circle', 'phone-icons', 'full-card']
sheet = Image.new('RGB', (960, 930), (13, 17, 23))
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype('arial.ttf', 22)
for i, (path, name) in enumerate(zip(frames, names)):
    with Image.open(path) as frame:
        rgb = frame.convert('RGB')
        if rgb.size != (1920, 1080):
            raise RuntimeError(f'Unexpected frame size: {rgb.size}')
        rgb.save(out / f'{i+1:02d}-{name}.jpg', quality=90, optimize=True)
        thumb = rgb.resize((480, 270), Image.Resampling.LANCZOS)
        x, y = (i % 2) * 480, (i // 2) * 310
        sheet.paste(thumb, (x, y))
        draw.text((x+12, y+274), f'{i+1:02d} {name}', fill=(232, 236, 241), font=font)
sheet.save(out / 'contact-960.jpg', quality=90, optimize=True)
shutil.rmtree(raw)
