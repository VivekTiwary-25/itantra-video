import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const repo = path.resolve(import.meta.dirname, '../..');
const source = path.join(repo, 'film/scene3/v3/snaps_f0015');
const target = path.join(import.meta.dirname, 'preview');
const tiles = path.join(repo, 'local/renders/scene3/v3/phone_tiles');
fs.mkdirSync(target, { recursive: true });
fs.mkdirSync(tiles, { recursive: true });
const frames = [
  ['00','00-card-full.jpg'], ['01','01-card-reveal.jpg'],
  ['02','02-vachana-speaking.jpg'], ['03','03-after-vachana-camera.jpg'],
  ['04','04-tech-no-contact.jpg'], ['05','05-tech-search.jpg'],
  ['06','06-tech-accept.jpg'], ['07','07-vivek-banner.jpg'],
  ['08','07b-banner-punch.jpg'], ['tap','08-accept-tap.jpg'],
  ['11','08b-accept-result.jpg'], ['12','09-sos-tts.jpg'],
  ['13','10-vivek-reply.jpg'], ['14','10b-reply-punch.jpg'],
  ['15','11-last-frame.jpg'],
];
function run(args) {
  const p = spawnSync('ffmpeg', args, { cwd: repo, stdio: 'inherit' });
  if (p.status !== 0) throw Error('ffmpeg failed');
}
for (const [i, [prefix, name]] of frames.entries()) {
  const folder = prefix === 'tap' ? path.join(repo, 'film/scene3/v3/snaps_tap') : source;
  const png = fs.readdirSync(folder).find(x => x.startsWith(`frame-${prefix === 'tap' ? '00' : prefix}-`));
  if (!png) throw Error(`Missing snapshot ${prefix}`);
  const input = path.join(folder, png);
  run(['-v','error','-y','-i',input,'-vf','scale=960:540:flags=lanczos','-frames:v','1','-q:v','3',path.join(target,name)]);
  run(['-v','error','-y','-i',input,'-vf','scale=480:270:flags=lanczos','-frames:v','1','-q:v','3',path.join(tiles,`tile-${String(i).padStart(2,'0')}.jpg`)]);
}
run(['-v','error','-y','-framerate','1','-i',path.join(tiles,'tile-%02d.jpg'),'-vf','tile=4x4:nb_frames=15','-frames:v','1','-q:v','3',path.join(target,'phone-review.jpg')]);
