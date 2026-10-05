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
    assert image.format == 'PNG'
    assert path.stat().st_size < 20_000_000
    # The map is below 330 px and the full-background photo ends at 600 px.
    # This empty strip proves the tagline is clear of map/photo elements.
    assert image.convert('RGB').crop((604, 290, 1280, 330)).getbbox() is None, name
    sheet.paste(image.convert('RGB').resize((320, 180), Image.Resampling.LANCZOS), (i * 320, 0))
preview = ROOT / 'results/T0053/preview'
preview.mkdir(parents=True, exist_ok=True)
sheet.save(preview / 'sheet.png')
first = Image.open(ROOT / 'thumbnails' / f'{names[0]}.png').convert('RGB')
second = Image.open(ROOT / 'thumbnails' / f'{names[1]}.png').convert('RGB')
diff = ImageChops.difference(first, second)
box = diff.getbbox()
assert box is not None and box[0] >= 610 and box[1] >= 218 and box[3] <= 300, box
for name in ['relay-frame.png', 'sos-frame.png']:
    frame = Image.open(ROOT / 'local/thumbs/T0053' / name)
    assert frame.size == (600, 720) and frame.mode == 'RGB', name
print('Verified three 1280x720 PNGs and generated the 320x180 side-by-side preview.')
