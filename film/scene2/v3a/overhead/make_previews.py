"""Downsample the requested snapshots to reviewable 960 px JPEGs."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
raw = HERE / 'assets/raw'
out = REPO / 'results/F0006/preview'
out.mkdir(parents=True, exist_ok=True)
times = ('0', '0.6', '1.5', '2.6', '3.4', '4.2', '4.97')
frames = sorted(raw.glob('frame-*-at-*s.png'))
if len(frames) != len(times):
    raise RuntimeError(f'Expected {len(times)} raw snapshots, got {len(frames)}')
sheet = Image.new('RGB', (960, 7 * 290), (18, 22, 25))
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype('arial.ttf', 20)
for i, (source, time) in enumerate(zip(frames, times)):
    with Image.open(source) as image:
        if image.size != (1920, 1080):
            raise RuntimeError(f'Unexpected size for {source.name}: {image.size}')
        half = image.convert('RGB').resize((960, 540), Image.Resampling.LANCZOS)
        half.save(out / f'{i:02d}-{time.replace(".", "p")}s.jpg', quality=89, optimize=True)
        phone = half.resize((480, 270), Image.Resampling.LANCZOS)
        sheet.paste(phone, (240, i * 290))
        draw.text((16, i * 290 + 8), f'{time} s', font=font, fill=(235, 239, 242))
sheet.save(out / 'phone-review.jpg', quality=90, optimize=True)
