"""Verify the delivery and produce the required 320x180 preview triptych."""
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[3]
names = ['v1_vachana_relay_speak', 'v2_vachana_relay_nonetwork', 'v3_vachana_sos']
sheet = Image.new('RGB', (960, 180))
for i, name in enumerate(names):
    path = ROOT / 'thumbnails' / f'{name}.png'
    image = Image.open(path)
    assert image.size == (1280, 720), (name, image.size)
    assert path.stat().st_size < 20_000_000
    sheet.paste(image.convert('RGB').resize((320, 180), Image.Resampling.LANCZOS), (i * 320, 0))
preview = ROOT / 'results/T0052/preview'
preview.mkdir(parents=True, exist_ok=True)
sheet.save(preview / 'sheet.png')
first = Image.open(ROOT / 'thumbnails' / f'{names[0]}.png').convert('RGB')
second = Image.open(ROOT / 'thumbnails' / f'{names[1]}.png').convert('RGB')
diff = ImageChops.difference(first, second)
box = diff.getbbox()
assert box is not None and box[0] >= 450 and box[1] >= 218 and box[3] <= 300, box
print('Verified three 1280x720 PNGs and generated the 320x180 side-by-side preview.')
