"""Scene 3 SOS sonar section build: sos_in, sos_sonar, sos_dive (HyperFrames compositions) plus sound stems.

Run from the repo root:   python film/scene3/sonar/build.py            (everything)
                          python film/scene3/sonar/build.py pages      (only re-fill the HTML + copy scripts)
Steps: pages (index.html per segment, scripts copied in), plates (ffmpeg: the app still, the blurred sides, the
       graded sospart2 plate for the dive), sound (sfx stems + sos_music.wav).
Input: RENDERS:scene3/app/vachana_sos_last.png (the vachana_sos slot's last frame). If it is missing, sos_in shows
       a marked placeholder card; re-run `build.py plates pages` once the still exists.
Needs: machine.local.json (footage_root, renders_dir), ffmpeg, numpy, scipy.
Render one segment:  cd film/scene3/sonar/<segment> && hyperframes.cmd render -q high -f 30 -o <out>.mp4
"""
import json, math, os, re, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
os.chdir(REPO)
sys.path.insert(0, str(HERE))
import cues as C  # noqa: E402

GEO_DIR = REPO / 'film/scene2/geo'
SHARED = HERE / 'shared'
VENDOR = {'gsap.min.js': REPO / 'film/vendor/gsap/gsap.min.js', 'three.min.js': REPO / 'film/vendor/three/three.min.js'}
SHARED_FILES = ['sonar.js', 'sos.js', 'sonar.css']
MACHINE = json.load(open(REPO / 'machine.local.json'))

# same heights and road styles as scene 2 (film/scene2/sonar/build.py), so the campus looks identical
HEIGHTS = {'tower_nw': 42, 'white_block': 20, 'block_a': 30, 'block_b': 34, 'block_c': 30, 'block_d': 28,
           'sw_court_1': 26, 'sw_court_2': 26, 'white_se': 22}
ROADS = {'secondary': (16, 0.75), 'tertiary': (10, 0.6), 'residential': (7, 0.55), 'service': (5, 0.7)}


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"failed: {' '.join(map(str, cmd))[:400]}\n{r.stderr[-2500:]}")
    return r


def seg_dir(seg):
    d = HERE / seg
    (d / 'assets').mkdir(parents=True, exist_ok=True)
    return d


def renders_path(ref):
    assert ref.startswith('RENDERS:')
    return Path(MACHINE['renders_dir']) / ref[len('RENDERS:'):]


# ---------------------------------------------------------------- geo (same as scene 2)
def z18px(lat, lon, origin):
    n = 256 * 2 ** 18
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return [round(x - origin[0], 1), round(y - origin[1], 1)]


def build_geo():
    g = json.load(open(GEO_DIR / 'campus_outlines.json', encoding='utf-8'))
    origin = g['frame']['origin_world_px']
    osm = json.load(open(GEO_DIR / 'nie_north_osm.json', encoding='utf-8'))
    roads = []
    for e in osm['elements']:
        hw = e.get('tags', {}).get('highway')
        if hw not in ROADS:
            continue
        pts = [z18px(p['lat'], p['lon'], origin) for p in e['geometry']]
        pts = [p for p in pts if -200 < p[0] < 1750 and -200 < p[1] < 1450]
        if len(pts) >= 2:
            w, b = ROADS[hw]
            roads.append({'pts': pts, 'w': w, 'b': b})
    campus = [{k: v for k, v in b.items() if k in ('id', 'pts', 'court')} | {'h': HEIGHTS.get(b['id'], 9)} for b in g['campus']]
    context = [{'pts': b['pts'], 'h': 14 + (i * 7) % 9} for i, b in enumerate(g['context'])]
    oval = next(f for f in g['features'] if f['kind'] == 'oval')
    rects = [{'pts': f['pts']} for f in g['features'] if f['kind'] == 'rect']
    geo = {'campus': campus, 'context': context, 'oval': oval, 'rects': rects, 'roads': roads}
    return 'window.GEO = ' + json.dumps(geo, separators=(',', ':')) + ';\n'


# ---------------------------------------------------------------- plates
def app_still_info():
    p = renders_path(C.APP_STILL['input'])
    if not p.exists():
        return None, None
    r = sh(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(p)])
    w, h = map(int, r.stdout.strip().split(','))
    return p, (w, h - C.APP_STILL['crop_top'])


def build_plates():
    root = MACHINE['footage_root']
    grade = None
    for line in open(REPO / 'film/scene1/grades.sh', encoding='utf-8'):
        m = re.match(r'^GRADE_V1="(.*)"\s*$', line.strip())
        if m:
            grade = m.group(1)
    enc = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-g', '15',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', '-an']
    fps = C.FPS
    # sos_in sides: sospart1's last frames, graded, heavily blurred and darkened (scene 2 slot layout), held
    src, t = C.SIDES_SRC
    n_in = round(C.SEG_LEN['sos_in'] * fps) + 2
    sh(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', f'{root}/{src}', '-frames:v', '1', '-vf',
        f"{grade},gblur=sigma=40,eq=brightness=-0.02,colorchannelmixer=rr=0.55:gg=0.55:bb=0.55,loop=loop={n_in}:size=1:start=0,fps={fps},setpts=N/{fps}/TB",
        '-frames:v', str(n_in), *enc, str(seg_dir('sos_in') / 'assets' / 'sides.mp4')])
    # sos_in phone: the slot's last frame, never graded, status bar cropped like the slots
    p, _ = app_still_info()
    if p:
        sh(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', str(p), '-vf',
            f"crop=iw:ih-{C.APP_STILL['crop_top']}:0:{C.APP_STILL['crop_top']},scale=trunc(iw/2)*2:trunc(ih/2)*2,fps={fps}",
            '-frames:v', str(n_in), *enc, str(seg_dir('sos_in') / 'assets' / 'app_still.mp4')])
    # sos_dive plate: graded sospart2, src (src_end - plate length) .. src_end, so the last frame is src_end - 1/fps
    D = C.SOS_DIVE
    n_d = round((C.SEG_LEN['sos_dive'] - D['plate_start']) * fps)
    s0 = round(D['src_end'] * fps) - n_d
    sh(['ffmpeg', '-v', 'error', '-y', '-i', f'{root}/Video/sospart2.mp4', '-filter_complex',
        f"[0:v]fps={fps},trim=start_frame={s0}:end_frame={s0 + n_d + 2},setpts=PTS-STARTPTS,{grade}[o]", '-map', '[o]',
        '-frames:v', str(n_d + 2), *enc, str(seg_dir('sos_dive') / 'assets' / 'sos_dive_plate.mp4')])
    print(f'plates: sides {n_in} fr, app still {"yes" if p else "MISSING (placeholder)"}, dive plate src frames {s0}-{s0 + n_d - 1}')


# ---------------------------------------------------------------- pages
def write_project(seg, html, geo_js):
    d = seg_dir(seg)
    (d / 'index.html').write_text(html, encoding='utf-8', newline='\n')
    (d / 'geo.js').write_text(geo_js, encoding='utf-8', newline='\n')
    for name, src in VENDOR.items():
        shutil.copyfile(src, d / name)
    for name in SHARED_FILES:
        shutil.copyfile(SHARED / name, d / name)
    (d / 'hyperframes.json').write_text(json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
        "media": {"autoProxy": True}}, indent=2) + '\n', encoding='utf-8', newline='\n')
    (d / 'meta.json').write_text(json.dumps({'id': seg, 'name': seg}, indent=2) + '\n', encoding='utf-8', newline='\n')


def build_pages():
    geo_js = build_geo()
    tpl = (SHARED / 'sos.html.tpl').read_text(encoding='utf-8')
    base = {'V': C.V, 'VIVEK': C.VIVEK, 'speed': C.WAVE_SPEED, 'waves': C.WAVES, 'arrive': C.ARRIVE,
            'arrive_r': math.dist(C.V, C.VIVEK), 'cam_close': C.CAM_CLOSE, 'sonar_start': C.SONAR_START,
            'sonar_end': C.SONAR_END, 'dive_to': C.DIVE_TO}
    for seg in C.ORDER:
        cfg = dict(base, mode=seg, t_offset=C.T_OFFSET[seg])
        layers = ''
        if seg == 'sos_in':
            S = C.SOS_IN
            p, size = app_still_info()
            phone_w = round(1080 * size[0] / size[1]) if size else 486
            cfg |= {'app_pulses': S['app_pulses'], 'phone_out': S['phone_out'], 'sonar_in': S['sonar_in'],
                    'pull_back_T': [S['pull_back'][0] + C.T_OFFSET[seg], 0.0], 'phone_w': phone_w,
                    'search_xy': C.APP_STILL['search_xy']}
            screen = ('<video id="app" class="clip" src="assets/app_still.mp4" data-start="0" data-duration="2.0" '
                      'data-media-start="0" muted playsinline></video>') if p else \
                     '<div class="placeholder">APP: vachana_sos<br/>(last frame: searching)</div>'
            rings = ''.join('<g style="opacity:0"><circle class="glow" r="10"/><circle class="ring" r="10"/></g>' for _ in S['app_pulses'])
            layers = f'''  <div id="phoneL">
    <video id="sides" class="clip" src="assets/sides.mp4" data-start="0" data-duration="2.0" data-media-start="0" muted playsinline></video>
    <div id="phone">{screen}</div>
    <div id="searchGlow"></div>
    <svg id="appWaves" width="1920" height="1080" viewBox="0 0 1920 1080">{rings}</svg>
  </div>'''
        elif seg == 'sos_dive':
            D = C.SOS_DIVE
            cfg |= {'dive': D['dive'], 'clip_in': D['clip_in'], 'glow': D['glow'], 'phone': D['phone']}
            dur = round(C.SEG_LEN[seg] - D['plate_start'], 3)
            layers = f'''  <div id="clipL" style="opacity:0">
    <div id="clipZoom" style="position:absolute;inset:0">
      <video id="plate" class="clip" src="assets/sos_dive_plate.mp4" data-start="{D['plate_start']}" data-duration="{dur}" data-media-start="0" muted playsinline></video>
    </div>
    <div id="phoneGlow"></div>
  </div>'''
        html = tpl.replace('{{SEG}}', seg).replace('{{DUR}}', str(C.SEG_LEN[seg])).replace('{{CFG}}', json.dumps(cfg)).replace('{{LAYERS}}', layers)
        left = re.findall(r'\{\{\w+\}\}', html)
        if left:
            sys.exit(f'unfilled placeholders: {left}')
        write_project(seg, html, geo_js)
    print('pages written:', ', '.join(C.ORDER))


def main():
    steps = sys.argv[1:] or ['plates', 'pages', 'sound']
    if 'plates' in steps:
        build_plates()
    if 'pages' in steps:
        build_pages()
    if 'sound' in steps:
        import sound
        sound.build_all({seg: seg_dir(seg) / 'assets' for seg in C.ORDER}, HERE / 'music')


if __name__ == '__main__':
    main()
