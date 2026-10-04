"""Resize local HyperFrames snapshots and assemble a phone-size review sheet."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

repo = Path(__file__).resolve().parents[2]
source = repo / "film/scene3/v3/snaps"
target = Path(__file__).resolve().parent / "preview"
target.mkdir(parents=True, exist_ok=True)
frames = [
    ("frame-00-at-0s.png", "00-card-full.jpg"),
    ("frame-01-at-0.8s.png", "01-card-reveal.jpg"),
    ("frame-02-at-7.1s.png", "02-vachana-speaking.jpg"),
    ("frame-03-at-12.267s.png", "03-after-vachana-camera.jpg"),
    ("frame-04-at-20.5s.png", "04-tech-no-contact.jpg"),
    ("frame-05-at-23.5s.png", "05-tech-search.jpg"),
    ("frame-06-at-27.7s.png", "06-tech-accept.jpg"),
    ("frame-07-at-31.833s.png", "07-vivek-banner.jpg"),
    ("frame-08-at-33.833s.png", "08-accept-tap.jpg"),
    ("../snaps_accept2/frame-01-at-35.2s.png", "08b-accept-result.jpg"),
    ("frame-09-at-40.5s.png", "09-sos-tts.jpg"),
    ("frame-10-at-44.5s.png", "10-vivek-reply.jpg"),
    ("frame-11-at-51.367s.png", "11-last-frame.jpg"),
]
tiles = []
for original, name in frames:
    with Image.open(source / original) as img:
        preview = img.convert("RGB").resize((960, 540), Image.Resampling.LANCZOS)
        preview.save(target / name, quality=89, optimize=True)
        phone = preview.resize((320, 180), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (340, 211), "#111820")
    canvas.paste(phone, (10, 10))
    ImageDraw.Draw(canvas).text((10, 194), name, fill="#f3f5f8")
    tiles.append(canvas)
sheet = Image.new("RGB", (340 * 3, 211 * 4), "#111820")
for i, tile in enumerate(tiles):
    sheet.paste(tile, ((i % 3) * 340, (i // 3) * 211))
sheet.save(target / "phone-review.jpg", quality=90, optimize=True)
