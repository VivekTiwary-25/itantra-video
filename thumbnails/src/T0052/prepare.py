"""Extract the chosen real frames, apply GRADE_V1, and feather their silhouettes."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'local/thumbs/T0052'
WORK.mkdir(parents=True, exist_ok=True)
config = json.loads((ROOT / 'machine.local.json').read_text())
grade = re.search(r'^GRADE_V1="(.*)"$', (ROOT / 'film/scene1/grades.sh').read_text(), re.M)[1]
selections = [
    ('relay', 'normalpart1.mp4', 8.0, [(485,123),(508,122),(531,130),(546,150),(552,178),(565,213),(568,237),(585,244),(598,276),(610,332),(603,375),(583,429),(573,453),(570,500),(560,540),(370,540),(376,495),(388,457),(397,412),(406,379),(412,329),(418,273),(438,245),(430,216),(442,191),(454,167),(458,147),(475,130)], (365,110,620,540)),
    ('sos', 'sospart1.mp4', 9.5, [(480,181),(502,193),(519,222),(526,266),(543,280),(558,311),(561,365),(549,409),(549,496),(548,529),(546,540),(388,540),(392,490),(397,438),(398,388),(389,363),(387,335),(394,302),(406,283),(410,272),(394,278),(408,252),(421,217),(445,190),(459,185)], (375,175,570,540)),
]
for mode, name, time, points, crop in selections:
    raw = WORK / f'{mode}-graded.png'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(time),
                    '-i', str(Path(config['footage_root']) / 'Video' / name), '-vf', grade,
                    '-frames:v', '1', '-update', '1', str(raw)], check=True)
    frame = cv2.imread(str(raw))
    small = cv2.resize(frame, (960, 540))
    polygon = np.zeros((540, 960), dtype=np.uint8)
    cv2.fillPoly(polygon, [np.array(points, dtype=np.int32)], 255)
    inner = cv2.erode(polygon, np.ones((41, 41), np.uint8))
    outer = cv2.dilate(polygon, np.ones((13, 13), np.uint8))
    mask = np.full((540, 960), cv2.GC_BGD, dtype=np.uint8)
    mask[outer > 0] = cv2.GC_PR_BGD
    mask[polygon > 0] = cv2.GC_PR_FGD
    mask[inner > 0] = cv2.GC_FGD
    cv2.setRNGSeed(52)
    cv2.grabCut(small, mask, None, np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64), 3, cv2.GC_INIT_WITH_MASK)
    alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    alpha[polygon == 0] = 0
    alpha = cv2.erode(alpha, np.ones((3, 3), np.uint8))
    image = Image.open(raw).convert('RGBA')
    matte = Image.fromarray(alpha).resize(image.size, Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(2.5))
    image.putalpha(matte)
    factor = image.width / 960
    image.crop(tuple(round(x * factor) for x in crop)).save(WORK / f'{mode}-person.png')
    assert Image.open(WORK / f'{mode}-person.png').getextrema()[3] == (0, 255)

for source in ['film/vendor/three/three.min.js', 'film/vendor/gsap/gsap.min.js',
               'film/scene2/sonar/sonar_a/geo.js', 'film/scene2/sonar/shared/sonar.js']:
    shutil.copy2(ROOT / source, WORK / Path(source).name)
print('Prepared graded, feathered real-person frames and local sonar dependencies.')
