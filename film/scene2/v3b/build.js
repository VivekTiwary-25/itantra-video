/* Scene 2 v3b: local-only build. node build.js [--preview|--final]. */
const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const HERE = __dirname;
const REPO = path.resolve(HERE, '../../..');
const machine = JSON.parse(fs.readFileSync(path.join(REPO, 'machine.local.json'), 'utf8'));
const RENDERS = machine.renders_dir;
const ASSETS = path.join(HERE, 'assets');
const T = JSON.parse(fs.readFileSync(path.join(HERE, 'timeline.json'), 'utf8'));
const C = JSON.parse(fs.readFileSync(path.join(REPO, 'film/captions/v3/s2b.json'), 'utf8'));
const order = ['sonar_a', 'relay_1', 'relay_2', 'relay_3', 'sonar_b'];
const durations = [7, 6, 6, 6, 6];
const renderFinal = process.argv.includes('--render');
const final = process.argv.includes('--final') || renderFinal;
const preview = process.argv.includes('--preview');
const missing = [];
function run(exe, argv, cwd=REPO) {
  const p = cp.spawnSync(exe, argv.map(String), {cwd, encoding:'utf8', shell:exe.endsWith('.cmd'), maxBuffer:8*1024*1024});
  if (p.error || p.status !== 0) throw Error(`${exe}: ${p.error || p.stderr || p.stdout}`);
  return p.stdout;
}
function probe(file) {
  if (!fs.existsSync(file)) return null;
  const d = JSON.parse(run('ffprobe', ['-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',file]));
  const v = (d.streams || []).find(s=>s.codec_type==='video');
  return {duration:Number(d.format.duration), width:v?.width, height:v?.height};
}
function stage(src, dst) {
  if (fs.existsSync(dst)) fs.unlinkSync(dst);
  try { fs.linkSync(src,dst); } catch { fs.copyFileSync(src,dst); }
}
function placeholder(dst, seconds, size) {
  run('ffmpeg',['-v','error','-y','-f','lavfi','-i',`color=c=0x0a0d12:s=${size}:r=30:d=${seconds}`,
    '-an','-c:v','libx264','-preset','ultrafast','-crf','30','-pix_fmt','yuv420p',dst]);
}
function verified(file, seconds, portrait=false) {
  const p=probe(file);
  if (!p || p.duration+0.07<seconds || !p.width || !p.height || (portrait && p.height<=p.width))
    throw Error(`Missing or invalid asset ${file}: ${JSON.stringify(p)}; need ${seconds}s`);
}
function stageVideo(name, src, seconds, size, portrait=false) {
  const dst=path.join(ASSETS,`${name}.mp4`);
  if (fs.existsSync(src)) { verified(src,seconds,portrait);stage(src,dst); }
  else { missing.push(name);placeholder(dst,seconds,size); }
  verified(dst,seconds,portrait);
}
function stageSound(name, src) {
  const dst=path.join(ASSETS,`${name}.wav`);
  if (!fs.existsSync(src)) {
    missing.push(name);
    const seconds=name==='N2'?3.35:name==='N3'?1.55:name==='sonar_a_sfx'?7:6;
    run('ffmpeg',['-v','error','-y','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',seconds,dst]);
    return;
  }
  stage(src,dst);
}
function main() {
  fs.mkdirSync(ASSETS,{recursive:true});
  for (const f of ['glass.css','glass.js','noise.png']) {
    const dir=path.join(ASSETS,'glass');fs.mkdirSync(dir,{recursive:true});
    fs.copyFileSync(path.join(REPO,'film/common/glass',f),path.join(dir,f));
  }
  fs.copyFileSync(path.join(REPO,'film/vendor/gsap/gsap.min.js'),path.join(HERE,'gsap.min.js'));
  const slot=JSON.parse(fs.readFileSync(path.join(REPO,'film/scene2/v2/slots.json'),'utf8')).yash_app;
  const slotSrc=path.join(RENDERS,slot.path.slice(8).split('/').join(path.sep));
  stageVideo('yash_app',slotSrc,slot.duration,'1080x2400',true);
  const slotTime=T.start_state.slot_time;
  run('ffmpeg',['-v','error','-y','-ss',slotTime,'-i',path.join(ASSETS,'yash_app.mp4'),'-frames:v','1',path.join(ASSETS,'yash_slot.jpg')]);
  const sonarDir=path.join(RENDERS,'scene2','sonar');
  const sfxDir=path.join(RENDERS,'scene2','sonar_work','film','scene2','sonar');
  for (let i=0;i<order.length;i++) {
    const n=order[i];stageVideo(n,path.join(sonarDir,`${n}.mp4`),durations[i],'1920x1080');
    stageSound(`${n}_sfx`,path.join(sfxDir,n,'assets',`${n}_sfx.wav`));
  }
  run('ffmpeg',['-v','error','-y','-ss','2.5','-i',path.join(ASSETS,'sonar_a.mp4'),'-frames:v','1','-q:v','3',path.join(ASSETS,'sonar_open.jpg')]);
  for (const n of ['N2','N3']) {
    const cfg=JSON.parse(fs.readFileSync(path.join(REPO,'film/common/narration.json'),'utf8'));
    const src=cfg.voice==='vivek' ? path.join(RENDERS,'narration','vivek',`${n}.wav`)
      : path.join(RENDERS,'scene2','narration','david',`${n}.wav`);
    stageSound(n,src);
  }
  const template=fs.readFileSync(path.join(HERE,'index.html.tpl'),'utf8');
  fs.writeFileSync(path.join(HERE,'index.html'),template.replaceAll('{{TIMELINE}}',JSON.stringify(T)).replaceAll('{{CAPTIONS}}',JSON.stringify(C)));
  if (final && missing.length) throw Error(`Missing assets for final render: ${missing.join(', ')}`);
  run('hyperframes.cmd',['check'],HERE);
  if (renderFinal) {
    const out=path.join(RENDERS,'scene2','v3b','scene2_v3b.mp4');fs.mkdirSync(path.dirname(out),{recursive:true});
    run('hyperframes.cmd',['render','-q','high','-f','30','-o',out],HERE);
    verified(out,T.duration);
  }
  if (preview) {
    const out=path.join(REPO,'results','F0017','preview');fs.mkdirSync(out,{recursive:true});
    const times=[0,.7,1.4,5.2,10.5,17,27.8,29.2,31.4,32.367];
    const tmp=path.join(REPO,'results','F0017','snapshots');fs.mkdirSync(tmp,{recursive:true});
    run('hyperframes.cmd',['snapshot','--at',times.join(','),'--no-end','-o',tmp],HERE);
    const pngs=fs.readdirSync(tmp).filter(x=>x.endsWith('.png')).sort();
    if (pngs.length!==times.length) throw Error(`Expected ${times.length} snapshots, got ${pngs.length}: ${pngs}`);
    for (let i=0;i<pngs.length;i++) run('ffmpeg',['-v','error','-y','-i',path.join(tmp,pngs[i]),'-vf','scale=960:-2','-q:v','3',path.join(out,`${String(i).padStart(2,'0')}-${String(times[i]).replace('.','p')}s.jpg`)]);
    run('python',['-c',`from PIL import Image\nfrom pathlib import Path\np=Path(__import__('sys').argv[1]); frames=[Image.open(f).convert('RGB').resize((480,270),Image.Resampling.LANCZOS) for f in sorted(p.glob('[0-9][0-9]-*s.jpg'))]; sheet=Image.new('RGB',(480,270*len(frames))); [sheet.paste(frame,(0,i*270)) for i,frame in enumerate(frames)]; sheet.save(p/'phone-review.jpg',quality=90,optimize=True)`,out]);
    fs.rmSync(tmp,{recursive:true,force:true});
  }
  console.log(JSON.stringify({duration:T.duration,slot_time:slotTime,placeholder_assets:missing,checked:true,preview}));
}
try {main();} catch(e) {console.error(e.stack||e);process.exit(1);}
