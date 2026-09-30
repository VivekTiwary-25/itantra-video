"""Scene 2 sonar section build: sonar_a, relay_1..3, sonar_b (HyperFrames compositions) plus sound stems.

Run from the repo root:   python film/scene2/sonar/build.py            (everything)
                          python film/scene2/sonar/build.py pages      (only re-fill the HTML + copy scripts)
Steps: geo (geo.js from the traced outlines + OSM roads), pages (index.html per segment, scripts copied in),
       plates (graded relay clips with the freeze and colour drain baked in, ffmpeg), sound (sfx stems + music).
Needs: machine.local.json (footage_root), ffmpeg, numpy, scipy.
Writes film/scene2/sonar/<segment>/ (index.html, hyperframes.json, meta.json, copies of gsap/three/sonar scripts)
and film/scene2/sonar/<segment>/assets/ (plates and wav stems: media, never committed).
Render one segment:  cd film/scene2/sonar/<segment> && hyperframes.cmd render -q high -f 30 -o <out>.mp4
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
SHARED_FILES = ['sonar.js', 'overlay.js', 'sonar.css']

# heights in map px (~0.58 m each): judged from the imagery (shadow lengths, floors), illustrative only
HEIGHTS = {'tower_nw': 42, 'white_block': 20, 'block_a': 30, 'block_b': 34, 'block_c': 30, 'block_d': 28,
           'sw_court_1': 26, 'sw_court_2': 26, 'white_se': 22}
ROADS = {'secondary': (16, 0.75), 'tertiary': (10, 0.6), 'residential': (7, 0.55), 'service': (5, 0.7)}

# overview framing: every relay dive starts from it and sonar_b sits on it
OVERVIEW = {'tx': 458, 'tz': 690, 'D': 900, 'pitch': 55, 'yaw': 0}
# sonar_b pushes in slowly from the overview to a tighter frame on the route, and comes to rest for the still ending
B_END = {'tx': 448, 'tz': 712, 'D': 690, 'pitch': 57, 'yaw': 0}


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"failed: {' '.join(map(str, cmd))[:400]}\n{r.stderr[-2500:]}")
    return r


def seg_dir(seg):
    d = HERE / seg
    (d / 'assets').mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------- geo
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
    campus = []
    for b in g['campus']:
        h = HEIGHTS.get(b['id'], 9)
        campus.append({k: v for k, v in b.items() if k in ('id', 'pts', 'court')} | {'h': h})
    context = [{'pts': b['pts'], 'h': 14 + (i * 7) % 9} for i, b in enumerate(g['context'])]
    oval = next(f for f in g['features'] if f['kind'] == 'oval')
    rects = [{'pts': f['pts']} for f in g['features'] if f['kind'] == 'rect']
    pts = {k: v for k, v in g['points'].items() if not k.startswith('_')}
    geo = {'campus': campus, 'context': context, 'oval': oval, 'rects': rects, 'roads': roads, 'points': pts}
    return 'window.GEO = ' + json.dumps(geo, separators=(',', ':')) + ';\n', pts


# ---------------------------------------------------------------- pages
def resolve_pulses(lst, pts):
    return [[pts[o] if isinstance(o, str) else o, t0, sp] for o, t0, sp in lst]


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
        "media": {"autoProxy": True}}, indent=2) + '\n', encoding='utf-8')
    (d / 'meta.json').write_text(json.dumps({'id': seg, 'name': seg}, indent=2) + '\n', encoding='utf-8')


def fill(tpl, vals):
    for k, v in vals.items():
        tpl = tpl.replace('{{' + k + '}}', str(v))
    left = re.findall(r'\{\{\w+\}\}', tpl)
    if left:
        sys.exit(f'unfilled placeholders: {left}')
    return tpl


def build_pages():
    geo_js, pts = build_geo()
    tpl = (SHARED / 'sonar.html.tpl').read_text(encoding='utf-8')
    A, Bc = C.SONAR_A, C.SONAR_B
    cfg_a = {'mode': 'a', 'points': pts, 'overview': OVERVIEW,
             'cam_start': {'tx': 520, 'tz': 600, 'D': 1250, 'pitch': 66, 'yaw': -16},
             'cam_settle': A['cam_settle'], 'fade_in': A['fade_in'],
             'pulses': resolve_pulses(A['pulses'], pts), 'points_on': A['points_on'], 'labels_on': A['labels_on'],
             'floor': 0.6}
    write_project('sonar_a', fill(tpl, {'SEG': 'sonar_a', 'DUR': C.SEG_LEN['sonar_a'], 'CFG': json.dumps(cfg_a)}), geo_js)
    cfg_b = {'mode': 'b', 'points': pts, 'overview': B_END,
             'cam_start': OVERVIEW,
             'pulses': resolve_pulses(Bc['pulses'] + [('Y', Bc['arrive'], 260.0)], pts),
             'hops': [list(h) for h in Bc['hops']], 'arrive': Bc['arrive'], 'labels_on': -1,
             'still_from': Bc['still_from'], 'ring_out': [Bc['still_from'] - 1.1, Bc['still_from'] - 0.05], 'floor': 0.6}
    write_project('sonar_b', fill(tpl, {'SEG': 'sonar_b', 'DUR': C.SEG_LEN['sonar_b'], 'CFG': json.dumps(cfg_b)}), geo_js)

    rtpl = (SHARED / 'relay.html.tpl').read_text(encoding='utf-8')
    S = C.RELAY_SHAPE
    for seg, r in C.RELAYS.items():
        cfg = {'points': pts, 'overview': OVERVIEW, 'focus': r['point'], 'shape': S, 'relay': r,
               'pulses': resolve_pulses([('V', -3.0, 300.0), (r['point'], -0.35, 260.0)], pts), 'floor': 0.6}
        vals = {'SEG': seg, 'DUR': C.SEG_LEN[seg], 'CFG': json.dumps(cfg),
                'PLATE_START': S['plate_start'], 'PLATE_DUR': round(C.SEG_LEN[seg] - S['plate_start'], 3)}
        write_project(seg, fill(rtpl, vals), geo_js)
    print('pages written:', ', '.join(C.ORDER))


# ---------------------------------------------------------------- plates (relay clips)
def grades():
    out = {}
    for line in open(REPO / 'film/scene1/grades.sh', encoding='utf-8'):
        m = re.match(r'^(\w+)="(.*)"\s*$', line.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out


def frame_stats(path, t):
    """Mean R, G, B (0-1) of the middle 80% of a frame, sky rows excluded (top 25%)."""
    import numpy as np
    raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-ss', f'{t:.3f}', '-i', str(path), '-frames:v', '1', '-vf', 'scale=192:108',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(108, 192, 3)[27:100, 19:173] / 255.0
    return a.reshape(-1, 3).mean(0)


def build_plates():
    import numpy as np
    root = json.load(open(REPO / 'machine.local.json'))['footage_root']
    G = grades()['GRADE_V1']
    S = C.RELAY_SHAPE
    fps = C.FPS
    # match the three clips to each other first: gentle per-channel gains towards their common average
    stats = {seg: frame_stats(f"{root}/{r['clip']}", r['F']) for seg, r in C.RELAYS.items()}
    avg = np.mean(list(stats.values()), 0)
    report = {}
    for seg, r in C.RELAYS.items():
        src = f"{root}/{r['clip']}"
        st = stats[seg]
        lum, lum_avg = st.mean(), avg.mean()
        # half-way towards the shared exposure and a neutral balance, clamped to +-8 %
        gains = np.clip(((avg / st) * 0.5 + 0.5) * ((lum_avg / lum) ** 0.5) / ((avg / st) * 0.5 + 0.5).mean(), 0.92, 1.08)
        match = "colorchannelmixer=rr={:.4f}:gg={:.4f}:bb={:.4f}".format(*gains)
        report[seg] = {'mean_rgb_before': [round(float(x), 3) for x in st], 'gains': [round(float(x), 4) for x in gains]}
        Ff = round(r['F'] * fps)
        live_n = round((S['freeze'] - S['plate_start']) * fps)                    # 45 frames
        hold_n = round((S['resume'] - S['freeze']) * fps)                         # 99 frames
        tail_n = round((C.SEG_LEN[seg] - S['resume']) * fps) + 3                  # 21 (+3 spare)
        total = live_n + hold_n + tail_n
        # time-varying drain mask (plate time T): 0 = full colour, 1 = grey. Feathered ellipse around the phone stays in colour.
        T0 = S['plate_start']
        d0, d1 = S['drain'][0] - T0, S['drain'][1] - T0
        u0, u1 = S['undrain'][0] - T0, S['undrain'][1] - T0
        px, py, rx, ry = r['island']
        # smoothstep ramps in T; mask computed at 1/4 resolution then scaled up (soft anyway)
        def ss(a, b):
            x = f"clip((T-{a:.3f})/{b - a:.3f},0,1)"
            return f"({x}*{x}*(3-2*{x}))"
        k = f"{ss(d0, d1)}*(1-{ss(u0, u1)})"
        m = f"clip((hypot((X*4-{px})/{rx:.1f},(Y*4-{py})/{ry:.1f})-0.5)/0.6,0,1)"
        expr = f"255*{m}*{k}"
        fc = (
            f"[0:v]fps={fps},format=yuv420p,split=3[a][b][c];"
            f"[a]trim=start_frame={Ff - live_n}:end_frame={Ff},setpts=PTS-STARTPTS[live];"
            f"[b]trim=start_frame={Ff}:end_frame={Ff + 1},setpts=PTS-STARTPTS,loop=loop={hold_n - 1}:size=1:start=0,setpts=N/{fps}/TB[hold];"
            f"[c]trim=start_frame={Ff}:end_frame={Ff + tail_n},setpts=PTS-STARTPTS[tail];"
            f"[live][hold][tail]concat=n=3:v=1:a=0,{match},{G},format=gbrp,split[col][g0];"
            f"[g0]hue=s=0,eq=brightness=-0.05:contrast=0.88,format=gbrp[gray];"
            f"color=c=black:s=480x270:r={fps}:d={total / fps:.4f},format=gbrp,"
            f"geq=r='{expr}':g='{expr}':b='{expr}',scale=1920:1080:flags=bicubic,format=gbrp[mask];"
            f"[col][gray][mask]maskedmerge,format=yuv420p[out]"
        )
        out = seg_dir(seg) / 'assets' / f'{seg}_plate.mp4'
        sh(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', fc, '-map', '[out]', '-an', '-frames:v', str(total),
            '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-g', '15',
            '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', str(out)])
        report[seg].update({'frames': total, 'live': live_n, 'hold': hold_n, 'tail': tail_n, 'src_frames': [Ff - live_n, Ff + tail_n]})
        print(seg, report[seg])
    return report


# ---------------------------------------------------------------- main
def main():
    steps = sys.argv[1:] or ['pages', 'plates', 'sound']
    if 'pages' in steps or 'geo' in steps:
        build_pages()
    if 'plates' in steps:
        build_plates()
    if 'sound' in steps:
        import sound
        sound.build_all({seg: seg_dir(seg) / 'assets' for seg in C.ORDER}, HERE / 'music')


if __name__ == '__main__':
    main()
