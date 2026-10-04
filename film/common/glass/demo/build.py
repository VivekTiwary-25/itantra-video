"""Prepare local moving footage for the 4 s glass demo.

Run from any working directory: python film/common/glass/demo/build.py
Only writes ignored MP4 derivatives under this demo's assets/. Never stages footage.
"""
from pathlib import Path
import json
import subprocess
import shutil

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
config = json.loads((REPO / 'machine.local.json').read_text(encoding='utf-8'))
footage = Path(config['footage_root']) / 'Video'
assets = HERE / 'assets'
assets.mkdir(exist_ok=True)
kit = HERE.parent
kit_copy = assets / 'glass'
kit_copy.mkdir(exist_ok=True)
for name in ('glass.css', 'glass.js', 'noise.png'):
    shutil.copy2(kit / name, kit_copy / name)
shutil.copy2(REPO / 'film/vendor/gsap/gsap.min.js', assets / 'gsap.min.js')

for name, source in (
    ('normalpart1.mp4', 'normalpart1.mp4'),
    ('vachna-part1.mp4', 'vachna part1.mp4'),
):
    src = footage / source
    if not src.is_file():
        raise FileNotFoundError(f'Missing FOOTAGE:Video/{source}')
    dst = assets / name
    subprocess.run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-ss', '2.0', '-i', str(src), '-t', '2.0', '-an',
        '-vf', 'scale=1920:1080:flags=lanczos',
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
        '-pix_fmt', 'yuv420p', str(dst)
    ], check=True)
    print(f'Prepared ignored demo media: {name}')
