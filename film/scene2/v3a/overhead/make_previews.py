"""Downsample the requested snapshots to reviewable 960 px JPEGs and a 480 px phone sheet."""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
raw = HERE / 'assets/raw'
out = REPO / 'results/F0013/preview'
out.mkdir(parents=True, exist_ok=True)
times = ('0', '0.6', '1.5', '2.6', '3.4', '4.2', '4.97')
frames = sorted(raw.glob('frame-*-at-*s.png'))
if len(frames) != len(times):
    raise RuntimeError(f'Expected {len(times)} raw snapshots, got {len(frames)}')
sheet = Image.new('RGB', (480, 7 * 270), (18, 22, 25))
for i, (source, time) in enumerate(zip(frames, times)):
    with Image.open(source) as image:
        if image.size != (1920, 1080):
            raise RuntimeError(f'Unexpected size for {source.name}: {image.size}')
        half = image.convert('RGB').resize((960, 540), Image.Resampling.LANCZOS)
        half.save(out / f'{i:02d}-{time.replace(".", "p")}s.jpg', quality=89, optimize=True)
        phone = image.convert('RGB').resize((480, 270), Image.Resampling.LANCZOS)
        sheet.paste(phone, (0, i * 270))
sheet.save(out / 'phone-review.jpg', quality=90, optimize=True)
