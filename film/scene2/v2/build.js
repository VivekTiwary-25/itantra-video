/* Scene 2 v2. Run with node build.js [--prepare|--render|--preview]. No network inputs. */
const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const HERE = __dirname;
const REPO = path.resolve(HERE, '../../..');
const MACHINE = JSON.parse(fs.readFileSync(path.join(REPO, 'machine.local.json'), 'utf8'));
const ROOT = MACHINE.footage_root;
const RENDERS = MACHINE.renders_dir;
const OUT = path.join(RENDERS, 'scene2', 'v2');
const ASSETS = path.join(HERE, 'assets');
const FPS = 30, SR = 48000;
const SONAR = ['sonar_a', 'relay_1', 'relay_2', 'relay_3', 'sonar_b'];
const slots = JSON.parse(fs.readFileSync(path.join(HERE, 'slots.json'), 'utf8'));
const args = new Set(process.argv.slice(2));
const preview = args.has('--preview');
const prepareOnly = args.has('--prepare');

function mkdir(p) { fs.mkdirSync(p, {recursive:true}); }
function run(exe, argv, cwd=REPO) {
  const p = cp.spawnSync(exe, argv.map(String), {cwd, encoding:'utf8', shell: exe.endsWith('.cmd'), maxBuffer:64*1024*1024});
  if (p.error || p.status !== 0) throw Error(`${exe} ${argv.join(' ')}\n${p.error||p.stderr||p.stdout}`);
  return p.stdout;
}
function probe(p) {
  if (!fs.existsSync(p)) throw Error(`Missing picture asset: ${p}`);
  const x = JSON.parse(run('ffprobe', ['-v','error','-show_entries','format=duration:stream=codec_type,width,height,nb_frames','-of','json',p]));
  const v = (x.streams||[]).find(s=>s.codec_type==='video');
  if (!v || !Number.isFinite(Number(x.format.duration))) throw Error(`Unplayable video: ${p}`);
  return {duration:Number(x.format.duration), width:v.width, height:v.height};
}
function verifyVideo(p, need, portrait=false) {
  const v=probe(p);
  if (v.duration+0.08 < need || v.width<100 || v.height<100 || (portrait && v.height<=v.width))
    throw Error(`Bad video asset ${p}: ${JSON.stringify(v)}; need ${need}s${portrait?' portrait':''}`);
  return v;
}
function fresh(dst, sources) {return !fs.existsSync(dst)||sources.some(s=>fs.statSync(s).mtimeMs>fs.statSync(dst).mtimeMs);}
function linked(src,dst) {
  mkdir(path.dirname(dst));
  if(fs.existsSync(dst)) fs.unlinkSync(dst);
  try {fs.linkSync(src,dst);} catch {fs.copyFileSync(src,dst);}
}
function copyChanged(src,dst) {
  if(!fs.existsSync(dst) || !fs.readFileSync(src).equals(fs.readFileSync(dst))) fs.copyFileSync(src,dst);
}
function grade() {return fs.readFileSync(path.join(REPO,'film/scene1/grades.sh'),'utf8').match(/^GRADE_V1="(.*)"$/m)[1];}
function ffvideo(src,dst,ss,dur) {
  if(!fresh(dst,[src,path.join(REPO,'film/scene1/grades.sh')])) return;
  run('ffmpeg',['-v','error','-y','-ss',ss,'-t',dur,'-i',src,'-vf',`fps=30,scale=1920:1080:flags=lanczos,${grade()},format=yuv420p`,'-an','-c:v','libx264','-preset','fast','-crf','20','-movflags','+faststart',dst]);
}
function still(src,dst,at) {if(fresh(dst,[src])) run('ffmpeg',['-v','error','-y','-ss',at,'-i',src,'-frames:v','1','-q:v','3',dst]);}
function placeholder(dst, seconds, dims) {
  if(fs.existsSync(dst) && probe(dst).duration+0.08>=seconds) return;
  run('ffmpeg',['-v','error','-y','-f','lavfi','-i',`color=c=0x101820:s=${dims}:r=30:d=${seconds}`,'-an','-c:v','libx264','-preset','ultrafast','-crf','28','-pix_fmt','yuv420p','-movflags','+faststart',dst]);
}
function timeline() {
  let frames=0; const segments=[];
  function add(name,sec,extra={}) {let n=Math.round(sec*FPS);segments.push({name,start:+(frames/FPS).toFixed(3),end:+((frames+n)/FPS).toFixed(3),...extra});frames+=n;}
  add('doorway',3); add('bench',4.3,{source:'FOOTAGE:Video/normalpart1.mp4',source_in:0});
  add('vachana_split_in',.5,{source:'FOOTAGE:Video/normalpart1.mp4',source_in:4.3});
  add('vachana_send',slots.vachana_send.duration,{source:'FOOTAGE:Video/normalpart1.mp4',camera_in:4.8});
  add('vachana_send_freeze',3.6); add('walk',6,{source:'FOOTAGE:Video/normalpart2.mp4'});
  add('maps',slots.maps.duration); add('yash_before_notification',2.65,{source:'FOOTAGE:Video/normalpart6.mp4',source_in:0});
  add('yash_app',slots.yash_app.duration,{source:'FOOTAGE:Video/normalpart6.mp4',camera_in:2.65});
  for(const n of SONAR) add(n,n==='sonar_a'?7:6);
  add('sonar_b_hold',.5);
  const by=Object.fromEntries(segments.map(s=>[s.name,s]));
  return {fps:FPS,duration:+(frames/FPS).toFixed(3),segments,narration_starts:{N1:+(by.vachana_send_freeze.start+.2).toFixed(3),N2:by.sonar_a.start,N3:+(by.sonar_b.start+4).toFixed(3)}};
}
function walkPlate() {
  const src=path.join(ROOT,'Video/normalpart2.mp4'), dst=path.join(ASSETS,'walk.mp4');
  const ramp=path.join(REPO,'results/T0006/ramp.json');
  if(!fresh(dst,[src,ramp,path.join(REPO,'film/scene1/grades.sh')])) return dst;
  const pieces=JSON.parse(fs.readFileSync(ramp,'utf8')).pieces;
  const filters=pieces.map((p,i)=>`[0:v]trim=start=${p.src_start}:end=${p.src_end},setpts=(PTS-STARTPTS)/${p.speed},fps=30,scale=1920:1080,setsar=1[v${i}]`);
  filters.push(pieces.map((_,i)=>`[v${i}]`).join('')+`concat=n=${pieces.length}:v=1:a=0,${grade()},format=yuv420p[out]`);
  run('ffmpeg',['-v','error','-y','-i',src,'-filter_complex',filters.join(';'),'-map','[out]','-frames:v','180','-an','-c:v','libx264','-preset','fast','-crf','20',dst]);
  return dst;
}
function slotSource(spec) {
  if(!spec.path.startsWith('RENDERS:')) throw Error('slot path must be RENDERS:');
  const rel=spec.path.slice(8).replaceAll('/',path.sep);
  if(path.isAbsolute(rel)||rel.split(path.sep).includes('..')) throw Error('unsafe slot path');
  return path.join(RENDERS,rel);
}
function prepareSlots() {
  const result={};
  for(const [name,spec] of Object.entries(slots)) {
    const src=slotSource(spec), dst=path.join(ASSETS,`${name}.mp4`);
    const missing=!fs.existsSync(src);
    if(missing) placeholder(dst,spec.duration,name==='maps'?'1080x2400':'1080x2290');
    else {verifyVideo(src,spec.duration,true); linked(src,dst);}
    const v=verifyVideo(dst,spec.duration,true);
    still(dst,path.join(ASSETS,`${name}_last.jpg`),Math.max(0,spec.duration-.08));
    result[name]={video:`assets/${name}.mp4`,last:`assets/${name}_last.jpg`,width:Math.round(1000*v.width/v.height),placeholder:missing};
  }
  return result;
}
function sonarStage() {
  const stage=path.join(HERE,'sonar_stage'); mkdir(stage);
  const orig=path.join(REPO,'film/scene2/sonar');
  const shared=['sonar.js','overlay.js','sonar.css'];
  for(const n of SONAR) {
    const d=path.join(stage,n); mkdir(path.join(d,'assets'));
    for(const f of ['index.html','geo.js','hyperframes.json','meta.json']) copyChanged(path.join(orig,n,f),path.join(d,f));
    for(const f of shared) copyChanged(path.join(orig,'shared',f),path.join(d,f));
    copyChanged(path.join(REPO,'film/vendor/gsap/gsap.min.js'),path.join(d,'gsap.min.js'));
    copyChanged(path.join(REPO,'film/vendor/three/three.min.js'),path.join(d,'three.min.js'));
    const silent=path.join(d,'assets',`${n}_sfx.wav`);
    const originalSfx=path.join(orig,n,'assets',`${n}_sfx.wav`);
    if(fs.existsSync(originalSfx))linked(originalSfx,silent);
    else if(!fs.existsSync(silent)) run('ffmpeg',['-v','error','-y','-f','lavfi','-i',`anullsrc=r=48000:cl=stereo`,'-t',n==='sonar_a'?7:6,silent]);
    if(n.startsWith('relay_')) {
      const table={relay_1:['normalpart5.mp4',3],relay_2:['normalpart4.mp4',2.2],relay_3:['normalpart3.mp4',6.5]};
      const [file,F]=table[n], src=path.join(ROOT,'Video',file), plate=path.join(d,'assets',`${n}_plate.mp4`);
      const originalPlate=path.join(orig,n,'assets',`${n}_plate.mp4`);
      if(fs.existsSync(originalPlate))linked(originalPlate,plate);
      else if(fresh(plate,[src,path.join(REPO,'film/scene1/grades.sh')])) {
        const fc=`[0:v]trim=start=${F-1.5}:duration=1.5,setpts=PTS-STARTPTS,fps=30,scale=1920:1080[l];[0:v]trim=start=${F}:duration=0.04,setpts=PTS-STARTPTS,fps=30,scale=1920:1080,loop=loop=98:size=1:start=0,setpts=N/30/TB[h];[0:v]trim=start=${F}:duration=0.8,setpts=PTS-STARTPTS,fps=30,scale=1920:1080[t];[l][h][t]concat=n=3:v=1:a=0,${grade()},format=yuv420p[out]`;
        run('ffmpeg',['-v','error','-y','-i',src,'-filter_complex',fc,'-map','[out]','-an','-c:v','libx264','-preset','fast','-crf','20',plate]);
      }
      verifyVideo(plate,5.5);
    }
  }
  return stage;
}
function prepareSonar() {
  const stage=sonarStage();
  function visualFallback(out,seconds,idx) {
    const w=1920,h=1080,b=Buffer.alloc(w*h*3),centers=[[780,510],[690,460],[790,540],[920,560],[960,550]];
    const [cx,cy]=centers[idx];
    for(let y=0;y<h;y++)for(let x=0;x<w;x++) {
      const i=(y*w+x)*3,r=Math.hypot(x-cx,y-cy),grid=(x%96<2||y%96<2)?8:0,ring=(Math.abs(r-240)<3||Math.abs(r-430)<2)?58:0;
      b[i]=6+grid;b[i+1]=15+grid+Math.round(ring*.65);b[i+2]=26+grid+ring;
      for(const [px,py] of [[660,430],[850,520],[1000,570],[1120,640],[1240,700]])if(Math.hypot(x-px,y-py)<8){b[i]=36;b[i+1]=158;b[i+2]=247;break;}
    }
    const ppm=path.join(ASSETS,`${SONAR[idx]}_preview.ppm`);
    fs.writeFileSync(ppm,Buffer.concat([Buffer.from(`P6\n${w} ${h}\n255\n`),b]));
    run('ffmpeg',['-v','error','-y','-loop','1','-framerate','30','-i',ppm,'-t',seconds,'-vf','format=yuv420p','-an','-c:v','libx264','-preset','ultrafast','-crf','25',out]);
  }
  for(const n of SONAR) {
    const out=path.join(ASSETS,`${n}.mp4`), source=path.join(stage,n,'index.html');
    const flag=path.join(ASSETS,`${n}.preview-only`);
    const existing=path.join(RENDERS,'scene2','sonar',`${n}.mp4`),dur=n==='sonar_a'?7:6;
    if(fs.existsSync(existing)) {verifyVideo(existing,dur);linked(existing,out);if(fs.existsSync(flag))fs.unlinkSync(flag);}
    else if(fresh(out,[source]) || ((!preview&&!prepareOnly)&&fs.existsSync(flag))) {
      run('hyperframes.cmd',['check'],path.join(stage,n));
      try {run('hyperframes.cmd',['render','-q','standard','-f','30','-o',out],path.join(stage,n));if(fs.existsSync(flag))fs.unlinkSync(flag);}
      catch(e) {if(!preview&&!prepareOnly)throw e;console.warn(`Preview sonar fallback for ${n}: ${String(e.message).split('\n')[2]}`);visualFallback(out,dur,SONAR.indexOf(n));fs.writeFileSync(flag,'Preview visual only. Rebuild on the render machine.\n');}
    }
    verifyVideo(out,dur);
  }
  still(path.join(ASSETS,'sonar_b.mp4'),path.join(ASSETS,'sonar_end.jpg'),5.8);
}
function prepareCamera() {
  ffvideo(path.join(ROOT,'Video/normalpart1.mp4'),path.join(ASSETS,'bench.mp4'),0,10.83);
  ffvideo(path.join(ROOT,'Video/normalpart6.mp4'),path.join(ASSETS,'yash.mp4'),0,12.647);
  for(const [src,out,at] of [['bench.mp4','bench_start.jpg',0],['bench.mp4','bench_end.jpg',10.75],['yash.mp4','yash_mid.jpg',8.23],['yash.mp4','yash_end.jpg',12.55]])
    still(path.join(ASSETS,src),path.join(ASSETS,out),at);
  walkPlate();
}
function writePage(T,app) {
  const tpl=fs.readFileSync(path.join(HERE,'index.html.tpl'),'utf8');
  const by=Object.fromEntries(T.segments.map(s=>[s.name,s]));
  let page=tpl.replaceAll('{{TIMELINE}}',JSON.stringify(T)).replaceAll('{{SLOTS}}',JSON.stringify(app)).replaceAll('{{DURATION}}',String(T.duration));
  for(const [name,row] of Object.entries(by)) {
    const key=name.toUpperCase();
    page=page.replaceAll(`{{${key}_START}}`,String(row.start)).replaceAll(`{{${key}_DURATION}}`,String(+(row.end-row.start).toFixed(3)));
  }
  page=page.replaceAll('{{YASH_REPLY_START}}',String(+(by.yash_app.start+12.23).toFixed(3)));
  if(/\{\{[A-Z_]+\}\}/.test(page))throw Error('Unfilled composition placeholder');
  const index=path.join(HERE,'index.html'),timelinePath=path.join(HERE,'timeline.json'),tjson=JSON.stringify(T,null,2)+'\n';
  if(!fs.existsSync(index)||fs.readFileSync(index,'utf8')!==page)fs.writeFileSync(index,page);
  if(!fs.existsSync(timelinePath)||fs.readFileSync(timelinePath,'utf8')!==tjson)fs.writeFileSync(timelinePath,tjson);
}
function verifyAll(T) {
  const req={bench:10.83,yash:12.64,walk:6,vachana_send:slots.vachana_send.duration,maps:3.5,yash_app:slots.yash_app.duration,sonar_a:7,relay_1:6,relay_2:6,relay_3:6,sonar_b:6};
  for(const [name,dur] of Object.entries(req)) verifyVideo(path.join(ASSETS,`${name}.mp4`),dur,['vachana_send','maps','yash_app'].includes(name));
  for(const name of ['bench_start','bench_end','yash_mid','yash_end','sonar_end','vachana_send_last','maps_last','yash_app_last'])
    if(!fs.existsSync(path.join(ASSETS,`${name}.jpg`))) throw Error(`Missing still: ${name}`);
  if(T.segments.at(-1).end!==T.duration) throw Error('Timeline end mismatch');
}
function decode(p,filter='') {
  const argv=['-v','error','-i',p];if(filter) argv.push('-af',filter);
  argv.push('-ar',SR,'-ac','1','-f','f32le','-');
  const b=cp.spawnSync('ffmpeg',argv,{cwd:REPO,maxBuffer:100*1024*1024});
  if(b.status!==0) throw Error(`Decode failed: ${p}: ${b.stderr.toString()}`);
  return new Float32Array(b.stdout.buffer.slice(b.stdout.byteOffset,b.stdout.byteOffset+b.stdout.byteLength));
}
function put(dst,src,at,srcA=0,srcB=src.length/SR,gain=1,fade=.03) {
  const lo=Math.max(0,Math.round(srcA*SR)),hi=Math.min(src.length,Math.round(srcB*SR)),d=Math.round(at*SR),f=Math.round(fade*SR);
  for(let j=lo;j<hi;j++) {const k=d+j-lo;if(k<0||k>=dst.length)continue; const m=Math.min(1,(j-lo)/f,(hi-j-1)/f);dst[k]+=src[j]*gain*Math.max(0,m);}
}
function writeWav(p,a) {
  const h=Buffer.alloc(44),pcm=Buffer.alloc(a.length*2);h.write('RIFF',0);h.writeUInt32LE(36+pcm.length,4);h.write('WAVEfmt ',8);h.writeUInt32LE(16,16);h.writeUInt16LE(1,20);h.writeUInt16LE(1,22);h.writeUInt32LE(SR,24);h.writeUInt32LE(SR*2,28);h.writeUInt16LE(2,32);h.writeUInt16LE(16,34);h.write('data',36);h.writeUInt32LE(pcm.length,40);
  for(let i=0;i<a.length;i++)pcm.writeInt16LE(Math.round(Math.max(-1,Math.min(1,a[i]))*32767),i*2);
  fs.writeFileSync(p,Buffer.concat([h,pcm]));
}
function synth(spec) {
  const a=new Float32Array(Math.round(spec.duration*SR));
  for(const [start,dur,low,high,level,harm] of spec.notes) for(let i=0;i<Math.min(Math.round(dur*SR),a.length-Math.round(start*SR));i++) {
    const t=i/SR, attack=Math.min(spec.attack,dur/3),release=Math.min(spec.release,dur/2);
    const fi=Math.min(1,t/attack),fo=Math.min(1,(dur-t)/release);
    const env=Math.sin(fi*Math.PI/2)**2*Math.sin(fo*Math.PI/2)**2*Math.exp(-1.2*t/dur);
    const phase=2*Math.PI*(low*t+(high-low)*t*t/(2*dur));
    a[Math.round(start*SR)+i]+=level*env*(Math.sin(phase)+harm*Math.sin(2*phase));
  }
  let peak=0;for(const v of a)peak=Math.max(peak,Math.abs(v));
  for(let i=0;i<a.length;i++)a[i]=a[i]/peak*Math.pow(10,-12/20);
  return a;
}
function music(a,start) {
  const begin=Math.round(start*SR),total=Math.min(31*SR,a.length-begin),chords=[[73.42,174.62,220],[116.54,146.84,174.62],[98,146.84,233.08],[116.54,174.62,261.62],[110,293.66,329.62]];
  for(let i=0;i<total;i++) {const t=i/SR,section=Math.min(4,Math.floor(t/6.2)),ch=chords[section],duck=(t<4.2||t>29)?0.38:1,edge=Math.min(1,t/.5,(31-t)/.5); let v=0;
    for(const f of ch)v+=Math.sin(2*Math.PI*f*t)*0.004;
    a[begin+i]+=v*duck*Math.max(0,edge);
  }
}
function audio(T,app) {
  const n=Math.round(T.duration*SR),dialogue=new Float32Array(n),musicTrack=new Float32Array(n),by=Object.fromEntries(T.segments.map(s=>[s.name,s]));
  const models=['cb.rnnn','sh.rnnn'].map(x=>path.join(REPO,'local/models/rnnoise',x));
  let chain='highpass=f=100:poles=2,afftdn=nr=18:nf=-45:tn=0,agate=threshold=0.025:ratio=3:range=0.1:attack=5:release=200:knee=4,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3000:t=q:w=1:g=2,deesser=i=0.3:m=0.5:f=0.5,acompressor=threshold=-20dB:ratio=2:attack=10:release=150,loudnorm=I=-16:TP=-1.5:LRA=11';
  if(models.every(fs.existsSync)) chain='highpass=f=100:poles=2,arnndn=m=local/models/rnnoise/cb.rnnn,arnndn=m=local/models/rnnoise/sh.rnnn:mix=0.6,'+chain;
  const vach=decode(path.join(ROOT,'Audio/normalpart1.mp3'),chain),yash=decode(path.join(ROOT,'Audio/Normalpart6.mp3'),chain);
  // Rule B: exactly first word - 0.12 through last word + 0.30, 30 ms edges.
  put(dialogue,vach,by.bench.start-.068+4.83,4.83,9.83);
  put(dialogue,yash,by.yash_before_notification.start-.3705,0,3.02);
  const replyAt=by.yash_app.start+slots.yash_app.ptt_down+.10;
  put(dialogue,yash,replyAt-.12,8.48,10.94);
  const voiceCfg=path.join(REPO,'film/common/narration.json');
  const voice=fs.existsSync(voiceCfg)?JSON.parse(fs.readFileSync(voiceCfg,'utf8')).voice:'david';
  if(!['david','vivek'].includes(voice))throw Error(`Bad narration voice: ${voice}`);
  for(const [key,at] of Object.entries(T.narration_starts)) {
    const file=voice==='david'?path.join(RENDERS,'scene2/narration/david',`${key}.wav`):path.join(RENDERS,'narration/vivek',`${key}.wav`);
    if(!fs.existsSync(file)) {if(!preview)throw Error(`Missing narration ${voice} ${key}: ${file}`); console.warn(`Preview has no narration ${key}`);continue;}
    const v=decode(file,'loudnorm=I=-16:TP=-1.5:LRA=11');
    const max={N1:3.4,N2:4.2,N3:1.8}[key];if(v.length/SR>max)console.warn(`${key} exceeds ${max}s: ${v.length/SR}s`);
    put(dialogue,v,at,0,Math.min(v.length/SR,max));
  }
  const specs=JSON.parse(fs.readFileSync(path.join(REPO,'film/sound/designs.json'),'utf8'));
  const sound=id=>synth(specs.find(s=>s.id===id));
  put(dialogue,sound('sent_a'),by.vachana_send.start+slots.vachana_send.sent_at,0,.32,.28);
  put(dialogue,sound('message_a'),by.yash_app.start+slots.yash_app.notification_at,0,.62,.28);
  put(dialogue,sound('sent_a'),by.yash_app.start+slots.yash_app.sent_at,0,.32,.28);
  const tts=path.join(RENDERS,'tts_itantra/tts_msg.wav');
  if(fs.existsSync(tts))put(dialogue,decode(tts,'loudnorm=I=-16:TP=-1.5:LRA=11'),by.yash_app.start+slots.yash_app.play_at+.15);
  else if(!preview)throw Error(`Missing iTantra TTS: ${tts}`);
  // Screen-recording audio is intentionally excluded. Dialogue comes only from the gated clean tracks;
  // iTantra TTS and the three procedural interaction sounds have explicit cues above.
  // Use v1's procedural sonar stems when present; otherwise keep a quiet local preview fallback.
  for(const [seg,cues] of Object.entries({sonar_a:[.35,2.25,4.3],relay_1:[.65,3],relay_2:[.65,3],relay_3:[.65,3],sonar_b:[.15,1.1,1.72,2.42,3.12]})) {
    const sfx=path.join(REPO,'film/scene2/sonar',seg,'assets',`${seg}_sfx.wav`);
    if(fs.existsSync(sfx))put(dialogue,decode(sfx),by[seg].start,0,by[seg].end-by[seg].start);
    else for(const cue of cues)put(dialogue,sound(cue===3?'tick_b':'sos_pulse_a'),by[seg].start+cue,0,undefined,.15);
  }
  const sonarMusic=path.join(REPO,'film/scene2/sonar/music/sonar_music.wav');
  if(fs.existsSync(sonarMusic))put(musicTrack,decode(sonarMusic),by.sonar_a.start,0,31);
  else music(musicTrack,by.sonar_a.start);
  const base=path.join(RENDERS,'scene2');mkdir(base);
  writeWav(path.join(base,'scene2_dialogue_sfx.wav'),dialogue);
  writeWav(path.join(base,'scene2_music.wav'),musicTrack);
  const sum=new Float32Array(n);for(let i=0;i<n;i++)sum[i]=dialogue[i]+musicTrack[i];
  writeWav(path.join(OUT,'mix_music.wav'),sum);writeWav(path.join(OUT,'mix_nomusic.wav'),dialogue);
  return {music:path.join(OUT,'mix_music.wav'),nomusic:path.join(OUT,'mix_nomusic.wav')};
}
function mux(raw,mix,out) {
  run('ffmpeg',['-v','error','-y','-i',raw,'-i',mix,'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','loudnorm=I=-16:TP=-1.5:LRA=11','-c:a','aac','-b:a','192k','-t',timeline().duration,'-movflags','+faststart',out]);
}
function main() {
  mkdir(OUT);mkdir(ASSETS);
  const T=timeline();
  prepareCamera();const app=prepareSlots();prepareSonar();writePage(T,app);verifyAll(T);
  if(!args.has('--audio-only')) run('hyperframes.cmd',['check'],HERE);
  if(args.has('--audio-only')) audio(T,app);
  else if(!prepareOnly) {
    const raw=path.join(OUT,'scene2_picture.mp4');
    if(fresh(raw,[path.join(HERE,'index.html')]))run('hyperframes.cmd',['render','-q','high','-f','30','-o',raw],HERE);
    verifyVideo(raw,T.duration);
    const tracks=audio(T,app);
    mux(raw,tracks.nomusic,path.join(OUT,'scene2_draft_nomusic.mp4'));
    mux(raw,tracks.music,path.join(OUT,'scene2_draft_music.mp4'));
  }
  console.log(JSON.stringify({duration:T.duration,voice_config:'film/common/narration.json',picture:'RENDERS:scene2/v2/scene2_picture.mp4',prepared:prepareOnly,preview}));
}
try {main();} catch(e) {console.error(e.stack||e);process.exit(1);}
