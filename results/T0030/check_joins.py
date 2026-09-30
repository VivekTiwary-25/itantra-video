from pathlib import Path
from PIL import Image, ImageChops, ImageStat

p = Path(__file__).parent / "preview"
frames = [Image.open(p / f"join_{i:02}.jpg").convert("RGB") for i in range(1, 7)]
sheet = Image.new("RGB", (1920, 1620))
for i, frame in enumerate(frames):
    sheet.paste(frame, ((i % 2) * 960, (i // 2) * 540))
sheet.save(p / "joins.jpg", quality=88)
for i in range(3):
    left, right = frames[2 * i:2 * i + 2]
    difference = sum(ImageStat.Stat(ImageChops.difference(left, right)).mean) / 3
    brightness = [ImageStat.Stat(frame.convert("L")).mean[0] for frame in (left, right)]
    print(f"join {i + 1}: mean absolute difference {difference:.2f}; brightness {brightness[0]:.1f} -> {brightness[1]:.1f}")
