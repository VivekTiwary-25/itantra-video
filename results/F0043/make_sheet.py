from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from shutil import copyfile, rmtree

here = Path(__file__).resolve().parent / "preview"
latest = here / "map-final"
if latest.is_dir():
    for fresh in latest.glob("frame-*-at-*.png"):
        old = next(here.glob("frame-*-at-" + fresh.stem.split("-at-")[1] + ".png"), None)
        if old is None:
            raise RuntimeError(f"missing original for {fresh.name}")
        copyfile(fresh, old)
    if latest.resolve().parent != here.resolve():
        raise RuntimeError("unexpected temporary preview directory")
    rmtree(latest)
review = here / "dive-review"
if review.is_dir():
    fresh = review / "frame-00-at-34.5s.png"
    if not fresh.is_file() or review.resolve().parent != here.resolve():
        raise RuntimeError("unexpected dive review directory")
    copyfile(fresh, here / "frame-10-at-34.5s.png")
    (here / "frame-10-at-33.9s.png").unlink()
    (here / "frame-10-at-33.9s-480.jpg").unlink()
    rmtree(review)
frames = sorted(here.glob("frame-*-at-*.png"))
width, height, band = 480, 270, 32
sheet = Image.new("RGB", (width * 4, (height + band) * 4), "#10141d")
draw = ImageDraw.Draw(sheet)
for i, path in enumerate(frames):
    image = Image.open(path).convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
    x, y = (i % 4) * width, (i // 4) * (height + band)
    sheet.paste(image, (x, y + band))
    draw.text((x + 10, y + 8), path.stem, fill="#f3f5f8")
    image.save(here / (path.stem + "-480.jpg"), quality=90, subsampling=0)
sheet.save(here / "sheet-480.jpg", quality=90, subsampling=0)
