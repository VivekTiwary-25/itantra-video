"""Score local footage candidates; keep all extracted frames outside git."""
import json
import subprocess
from pathlib import Path

import cv2
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'local/thumbs/T0053'
WORK.mkdir(parents=True, exist_ok=True)
config = json.loads((ROOT / 'machine.local.json').read_text())
names = ['normalpart1.mp4', '20261002_081346_short_intro.mp4', 'sospart1.mp4', 'sospart2.mp4']
all_scores = {}
for name in names:
    capture = cv2.VideoCapture(str(Path(config['footage_root']) / 'Video' / name))
    fps = capture.get(cv2.CAP_PROP_FPS)
    duration = capture.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    candidates = []
    for quarter in range(int(duration * 4)):
        time = quarter / 4
        filename = f'{Path(name).stem}-{time:.2f}.jpg'
        # Use the same FFmpeg timestamp seek as final extraction. OpenCV frame
        # seeking on these phone clips does not reproduce FFmpeg's selected frame.
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(time),
                        '-i', str(Path(config['footage_root']) / 'Video' / name),
                        '-vf', 'scale=960:540', '-frames:v', '1', '-update', '1',
                        str(WORK / filename)], check=True)
        frame = cv2.imread(str(WORK / filename))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Score the central actor region, avoiding background foliage at the edges.
        score = float(cv2.Laplacian(gray[60:480, 250:720], cv2.CV_64F).var())
        candidates.append({'time': time, 'sharpness': round(score, 2), 'image': filename})
    capture.release()
    best = sorted(candidates, key=lambda x: x['sharpness'], reverse=True)[:8]
    assert len(best) == 8
    sheet = Image.new('RGB', (1280, 400), '#080c12')
    draw = ImageDraw.Draw(sheet)
    for i, row in enumerate(best):
        x, y = i % 4 * 320, i // 4 * 200
        image = Image.open(WORK / row['image']).resize((320, 180), Image.Resampling.LANCZOS)
        sheet.paste(image, (x, y))
        draw.text((x + 6, y + 182), f"{row['time']:.2f}s / sharpness {row['sharpness']}", fill='white')
    sheet.save(WORK / f'{Path(name).stem}-best8.png')
    # Review the full clip chronologically: the required speaking pose takes
    # priority over sharpness, so the highest scores alone cannot select it.
    for start in range(0, len(candidates), 16):
        sheet = Image.new('RGB', (1280, 800), '#080c12')
        draw = ImageDraw.Draw(sheet)
        for i, row in enumerate(candidates[start:start + 16]):
            x, y = i % 4 * 320, i // 4 * 200
            image = Image.open(WORK / row['image']).resize((320, 180), Image.Resampling.LANCZOS)
            sheet.paste(image, (x, y))
            draw.text((x + 6, y + 182), f"{row['time']:.2f}s / sharpness {row['sharpness']}", fill='white')
        sheet.save(WORK / f'{Path(name).stem}-all-{start // 16 + 1}.png')
    all_scores[name] = {'best8': best, 'candidates': candidates}
    print(f'Scored {name}: {len(candidates)} frames.', flush=True)
(WORK / 'frame-scores.json').write_text(json.dumps(all_scores, indent=2))
print('Scored complete clips and made best-eight and chronological sheets in local/thumbs/T0053.')
