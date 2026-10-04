// Local fallback for previewing this task when Python is unavailable in the worker sandbox.
// The canonical cross-machine builder remains film/scene3/v3/build.py.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const repo = path.resolve(import.meta.dirname, '../..');
const scene = path.join(repo, 'film/scene3/v3');
const assets = path.join(scene, 'assets');
const plates = path.join(repo, 'local/renders/scene3/v3/plates');
const machine = JSON.parse(fs.readFileSync(path.join(repo, 'machine.local.json'), 'utf8'));
const render = path.join(machine.renders_dir, 'scene3');
const footage = path.join(machine.footage_root, 'Video');
fs.mkdirSync(assets, { recursive: true });
fs.mkdirSync(path.join(assets, 'glass'), { recursive: true });
fs.mkdirSync(plates, { recursive: true });
for (const file of ['glass.css', 'glass.js', 'noise.png'])
  fs.copyFileSync(path.join(repo, 'film/common/glass', file), path.join(assets, 'glass', file));
const grade = fs.readFileSync(path.join(repo, 'film/scene1/grades.sh'), 'utf8').match(/^GRADE_V1="(.*)"$/m)?.[1];
if (!grade) throw Error('Missing grade');
function run(bin, args) {
  const p = spawnSync(bin, args, { cwd: repo, stdio: 'inherit' });
  if (p.status !== 0) throw Error(`${bin} failed`);
}
for (const [name, file, start, duration] of [
  ['vachana', 'sospart1.mp4', '0', '10.64'],
  ['vivek', 'sospart2.mp4', '3.0', '7.70'],
]) {
  const out = path.join(plates, `${name}.mp4`);
  if (!fs.existsSync(out)) run('ffmpeg', ['-v','error','-y','-ss',start,'-t',duration,'-i',path.join(footage,file),'-vf',`fps=30,scale=1920:1080:flags=lanczos,${grade},format=yuv420p`,'-an','-c:v','libx264','-preset','medium','-crf','18',out]);
  const target = path.join(assets, `${name}.mp4`);
  if (!fs.existsSync(target)) fs.linkSync(out, target);
}
for (const [name, source] of [
  ['vachana_sos', path.join(render, 'app/vachana_sos.mp4')],
  ['vivek_app', path.join(render, 'app/vivek_app.mp4')],
  ...['sos_in','sos_sonar','sos_dive'].map(x => [x, path.join(render, `v2/sonar/${x}.mp4`)]),
]) {
  const target = path.join(assets, `${name}.mp4`);
  if (!fs.existsSync(source)) throw Error(`Missing local preview media: ${name}`);
  if (!fs.existsSync(target)) fs.linkSync(source, target);
  if (name.includes('sos') && !name.startsWith('sos_') || name === 'vivek_app') {
    const still = path.join(assets, `${name}_first.jpg`);
    if (!fs.existsSync(still)) run('ffmpeg', ['-v','error','-y','-ss','0','-i',source,'-frames:v','1','-q:v','3',still]);
  }
}
const existing = fs.readFileSync(path.join(scene, 'index.html'), 'utf8');
let layers = existing.slice(existing.indexOf('<div class="scene"'), existing.indexOf('<div id="techline-layer">'));
layers = layers.replace('class="glass-card full" id="sos-card"', 'class="glass-card full sos" id="sos-card"');
layers = layers.replace('id="vivek-field"><div class="screen"', 'id="vivek-field"><div class="screen" data-layout-allow-overflow');
if (!layers.includes('accept-tap-ring')) layers = layers.replace(/(<video id="video_vivek_app"[^>]*><\/video>)/, '$1<div class="accept-tap-ring" aria-hidden="true"></div>');
const timeline = JSON.parse(fs.readFileSync(path.join(scene, 'timeline.json'), 'utf8'));
const captions = JSON.parse(fs.readFileSync(path.join(repo, 'film/captions/v3/s3.json'), 'utf8'));
const page = fs.readFileSync(path.join(scene, 'index.html.tpl'), 'utf8')
  .replace('{{DURATION}}', timeline.duration.toFixed(6))
  .replace('{{TIMELINE}}', JSON.stringify(timeline))
  .replace('{{CAPTIONS}}', JSON.stringify(captions).replaceAll('<', '\\u003c'))
  .replace('{{LAYERS}}', layers);
fs.writeFileSync(path.join(scene, 'index.html'), page);
