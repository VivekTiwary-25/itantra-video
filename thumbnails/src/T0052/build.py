"""Run from the repository root: python thumbnails/src/T0052/build.py."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent
WORK = ROOT / 'local/thumbs/T0052'
subprocess.run([sys.executable, str(SOURCE / 'prepare.py')], cwd=ROOT, check=True)
html = (SOURCE / 'index.html').read_text(encoding='utf-8')
names = ['v1_vachana_relay_speak', 'v2_vachana_relay_nonetwork', 'v3_vachana_sos']
for mode, name in enumerate(names, 1):
    directory = WORK / f'v{mode}'
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'index.html').write_text(html.replace('data-mode="1"', f'data-mode="{mode}"'), encoding='utf-8')
    for asset in ['three.min.js', 'gsap.min.js', 'geo.js', 'sonar.js', 'relay-person.png', 'sos-person.png']:
        shutil.copy2(WORK / asset, directory / asset)
    (directory / 'hyperframes.json').write_text('{"media":{"autoProxy":false}}')
    subprocess.run([shutil.which('hyperframes.cmd'), 'snapshot', str(directory), '--at', '0', '--no-end', '--describe', 'false'], cwd=ROOT, check=True)
    shutil.copy2(directory / 'snapshots/frame-00-at-0s.png', ROOT / 'thumbnails' / f'{name}.png')
subprocess.run([sys.executable, str(SOURCE / 'verify.py')], cwd=ROOT, check=True)
