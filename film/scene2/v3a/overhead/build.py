"""Prepare ignored local media and data for the five-second overhead preview.

Run from any working directory: python film/scene2/v3a/overhead/build.py
"""
from pathlib import Path
import json
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
config = json.loads((REPO / 'machine.local.json').read_text(encoding='utf-8'))
footage = Path(config['footage_root']) / 'Video'
assets = HERE / 'assets'
assets.mkdir(exist_ok=True)
(assets / 'glass').mkdir(exist_ok=True)

for name in ('glass.css', 'glass.js', 'noise.png'):
    shutil.copy2(REPO / 'film/common/glass' / name, assets / 'glass' / name)
shutil.copy2(REPO / 'film/vendor/gsap/gsap.min.js', assets / 'gsap.min.js')

geo = {
    'osm': json.loads((REPO / 'film/scene2/geo/nie_north_osm.json').read_text(encoding='utf-8')),
    'outlines': json.loads((REPO / 'film/scene2/geo/campus_outlines.json').read_text(encoding='utf-8')),
}
(assets / 'geo.js').write_text('window.OVERHEAD_GEO = ' + json.dumps(geo, separators=(',', ':')) + ';\n', encoding='utf-8')

for source_name, output_name, seek in (
    ('normalpart2.mp4', 'walk-still.jpg', None),
    ('normalpart6.mp4', 'yash-still.jpg', 0.0),
):
    source = footage / source_name
    if not source.is_file():
        raise FileNotFoundError(f'Missing FOOTAGE:Video/{source_name}')
    if seek is None:
        probe = subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', str(source)
        ], text=True)
        seek = max(0.0, float(probe.strip()) - 0.55)
    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-ss', f'{seek:.3f}', '-i', str(source), '-frames:v', '1',
        '-vf', 'scale=1920:1080:flags=lanczos', '-q:v', '3',
        str(assets / output_name)
    ], check=True)
    print(f'Prepared ignored still from FOOTAGE:Video/{source_name}')

preview = (HERE / 'preview.html').read_text(encoding='utf-8')
(HERE / 'index.html').write_text(preview.replace('data-preview-id="overhead"', 'data-composition-id="overhead"'), encoding='utf-8')
print('Prepared ignored HyperFrames index.html')
