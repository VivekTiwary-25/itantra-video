"""Extract full graded footage frames and crop with their real background."""
import json
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / 'local/thumbs/T0053'
WORK.mkdir(parents=True, exist_ok=True)
config = json.loads((ROOT / 'machine.local.json').read_text())
grade = re.search(r'^GRADE_V1="(.*)"$', (ROOT / 'film/scene1/grades.sh').read_text(), re.M)[1]
selections = [
    ('relay', '20261002_081346_short_intro.mp4', 7.5, (1480, 600, 2680, 2040)),
    ('sos', 'sospart1.mp4', 4.25, (650, 216, 1370, 1080)),
]
for mode, name, time, crop in selections:
    raw = WORK / f'{mode}-graded.png'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(time),
                    '-i', str(Path(config['footage_root']) / 'Video' / name), '-vf', grade,
                    '-frames:v', '1', '-update', '1', str(raw)], check=True)
    image = Image.open(raw).convert('RGB')
    image.crop(crop).resize((600, 720), Image.Resampling.LANCZOS).save(WORK / f'{mode}-frame.png')
    assert Image.open(WORK / f'{mode}-frame.png').mode == 'RGB'

for source in ['film/vendor/three/three.min.js', 'film/vendor/gsap/gsap.min.js',
               'film/scene2/sonar/sonar_a/geo.js', 'film/scene2/sonar/shared/sonar.js']:
    shutil.copy2(ROOT / source, WORK / Path(source).name)
print('Prepared full-background footage crops with GRADE_V1 and local sonar dependencies.')
