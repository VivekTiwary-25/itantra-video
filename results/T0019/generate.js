// Rebuild the six review stills with local footage and the scene's approved grade.
const fs = require('fs');
const path = require('path');
const cp = require('child_process');

const repo = path.resolve(__dirname, '../..');
const config = JSON.parse(fs.readFileSync(path.join(repo, 'machine.local.json'), 'utf8'));
const source = path.join(config.footage_root, 'Video', 'normalpart1.mp4');
const grades = fs.readFileSync(path.join(repo, 'film/scene1/grades.sh'), 'utf8');
const grade = grades.match(/^GRADE_V1="(.*)"$/m)[1];
const out = path.join(__dirname, 'preview');
fs.mkdirSync(out, {recursive: true});

function ease(p) {
  p = Math.max(0, Math.min(1, p));
  return p < 0.5 ? 4*p*p*p : 1-Math.pow(-2*p+2, 3)/2;
}

const end = 7 + 20/30; // last bench frame before the 7.7 s slot cut
for (const [name, endingScale] of [['current', 8.5], ['wide_1p8', 1.8], ['medium_2p2_early_dissolve', 2.2]]) {
  for (const [label, sceneTime] of [['minus_0p3', end-0.3], ['end', end]]) {
    const f = ease((sceneTime-5.4)/2.3);
    const scale = 1+(endingScale-1)*f;
    const cx = 820+80*f, cy = 930-350*f;
    const tx = f*(960-scale*cx), ty = f*(540-scale*cy);
    // Crop on the graded 1920x1080 plate, then enlarge with Lanczos.
    const w = 1920/scale, h = 1080/scale;
    const x = -tx/scale, y = -ty/scale;
    const base = `fps=30,scale=1920:1080:flags=lanczos,${grade},crop=w=${w.toFixed(6)}:h=${h.toFixed(6)}:x=${x.toFixed(6)}:y=${y.toFixed(6)},scale=1920:1080:flags=lanczos,unsharp=5:5:0.28:5:5:0,format=yuv420p`;
    const alpha = name.startsWith('medium') ? Math.max(0, Math.min(1, (sceneTime-7.4)/0.5)) : 0;
    const vf = alpha ? `${base},split[front][side];[side]boxblur=luma_radius=40:luma_power=1,eq=brightness=-0.2,drawbox=x=717:y=0:w=486:h=1080:color=0x0b1018:t=fill[app];[front][app]blend=all_expr='A*${(1-alpha).toFixed(6)}+B*${alpha.toFixed(6)}',format=yuv420p[out]` : base;
    const args = ['-hide_banner', '-loglevel', 'error', '-y', '-ss', (sceneTime-3).toFixed(6), '-i', source,
      ...(alpha ? ['-filter_complex', vf, '-map', '[out]'] : ['-vf', vf]),
      '-frames:v', '1', '-q:v', '4', path.join(out, `${name}_${label}.jpg`)];
    cp.execFileSync('ffmpeg', args, {stdio: 'inherit'});
    console.log(`${name}_${label}: source=${(sceneTime-3).toFixed(3)} scale=${scale.toFixed(3)} crop=${w.toFixed(0)}x${h.toFixed(0)} dissolve=${alpha.toFixed(3)}`);
  }
}
