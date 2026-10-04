/* Scene 2b build: narration lengths are the timing source. */
const fs=require('fs'),path=require('path'),cp=require('child_process');
const HERE=__dirname,REPO=path.resolve(HERE,'../../..');
const machine=JSON.parse(fs.readFileSync(path.join(REPO,'machine.local.json')));
const RENDERS=machine.renders_dir,ASSETS=path.join(HERE,'assets');
const lines=JSON.parse(fs.readFileSync(path.join(REPO,'film/common/narration_v4.json'))).lines;
const names=['N2','N2a','N2b','N2c','N2d','N2e','N2f','N3'];
const order=['sonar_a','relay_1','relay_2','relay_3','sonar_b'];
const lens={sonar_a:7,relay_1:6,relay_2:6,relay_3:6,sonar_b:6},missing=[];
const round=n=>Math.round(n*1000)/1000;
function run(exe,args,cwd=REPO){
  const p=cp.spawnSync(exe,args.map(String),{cwd,encoding:'utf8',shell:exe.endsWith('.cmd'),maxBuffer:8*1024*1024});
  if(p.error||p.status!==0)throw Error(exe+': '+(p.error||p.stderr||p.stdout));
  return p.stdout;
}
function stage(src,dst){if(fs.existsSync(dst))fs.unlinkSync(dst);try{fs.linkSync(src,dst)}catch{fs.copyFileSync(src,dst)}}
function video(name,src,seconds,size,portrait=false){
  const dst=path.join(ASSETS,name+'.mp4');
  let ok=false;
  if(fs.existsSync(src)){
    const p=JSON.parse(run('ffprobe',['-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',src]));
    const v=p.streams.find(s=>s.codec_type==='video');
    ok=!!v&&Number(p.format.duration)+.07>=seconds&&(!portrait||v.height>v.width);
  }
  if(ok)stage(src,dst);
  else{missing.push(name);run('ffmpeg',['-v','error','-y','-f','lavfi','-i',`color=c=0x0a0d12:s=${size}:r=30:d=${seconds}`,'-an','-c:v','libx264','-preset','ultrafast','-crf','30','-pix_fmt','yuv420p',dst])}
}
function sound(name,src,seconds){
  const dst=path.join(ASSETS,name+'.wav');
  if(fs.existsSync(src))stage(src,dst);
  else{missing.push(name);run('ffmpeg',['-v','error','-y','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',seconds,dst])}
}
function timing(){
  const T={fps:30,segments:[],narration_starts:{},beats:[],start_state:{field:'#0a0d12',screen_height:1000,phone_center:[960,540],slot:'RENDERS:scene2/app/yash_app.mp4'},end_state:{
    card_html:'<div class="glass-card full"><h1 class="card-title"><span style="color:var(--red)">SOS</span></h1><p>help from anyone nearby, no saved contact needed</p></div>',
    class:'glass-card full',title:'SOS',subline:'help from anyone nearby, no saved contact needed'}};
  const seg=(name,start,end)=>T.segments.push({name,start:round(start),end:round(end)});
  const duration=id=>{const d=Number(lines[id].duration);if(!(d>0))throw Error('Invalid '+id+' duration');return d+.4};
  seg('push_in',0,1.4);T.narration_starts.N2=1.4;
  let t=1.4+duration('N2');
  T.beats.push({id:'N2',start:1.4,end:round(t)});
  seg('sonar_a',1.4,t);
  const loopStart=t;
  for(const id of ['N2a','N2b','N2c','N2d','N2e']){
    T.narration_starts[id]=round(t);T.beats.push({id,start:round(t),end:round(t+duration(id))});t+=duration(id);
  }
  seg('sonar_loop',loopStart,t);
  T.narration_starts.N2f=round(t);T.beats.push({id:'N2f',start:round(t),end:round(t+duration('N2f'))});
  for(const id of ['relay_1','relay_2','relay_3']){seg(id,t,t+6);t+=6}
  const arrivalLength=Math.max(6,3.4+duration('N3')+.63);
  seg('sonar_b',t,t+arrivalLength);
  T.narration_starts.N3=round(t+3.4);
  T.beats.push({id:'N3',start:round(t+3.4),end:round(t+3.4+duration('N3'))});
  const cardStart=t+3.4+duration('N3')+.03;
  seg('to_sos',cardStart,t+arrivalLength);T.duration=round(t+arrivalLength);
  for(const b of T.beats)if(Math.abs(b.end-b.start-duration(b.id))>.002)throw Error('Narration beat length mismatch: '+b.id);
  return T;
}
function join(T){
  const A=JSON.parse(fs.readFileSync(path.join(REPO,'film/scene2/v3a/timeline.json'))).end_state;
  if(!A||A.slot!=='yash_app'||Math.abs(A.position.x-735)>.5||Math.abs(A.position.y-40)>.5||A.position.width!==450||A.position.height!==1000||A.background.toLowerCase()!=='#0a0d12')
    throw Error('s2a/s2b phone join does not match');
  const t=round(A.slot_time+1/30);T.start_state.slot_time=t;
  T.start_state.derivation=`s2a end_state.slot_time ${A.slot_time} + 1/30 (read at build)`;return t;
}
function main(){
  fs.mkdirSync(ASSETS,{recursive:true});fs.mkdirSync(path.join(ASSETS,'glass'),{recursive:true});
  for(const f of ['glass.css','glass.js','noise.png'])fs.copyFileSync(path.join(REPO,'film/common/glass',f),path.join(ASSETS,'glass',f));
  fs.copyFileSync(path.join(REPO,'film/vendor/gsap/gsap.min.js'),path.join(HERE,'gsap.min.js'));
  const T=timing(),slotTime=join(T),slot=JSON.parse(fs.readFileSync(path.join(REPO,'film/scene2/v2/slots.json'))).yash_app;
  video('yash_app',path.join(RENDERS,slot.path.slice(8).split('/').join(path.sep)),slot.duration,'1080x2400',true);
  run('ffmpeg',['-v','error','-y','-ss',slotTime,'-i',path.join(ASSETS,'yash_app.mp4'),'-frames:v','1',path.join(ASSETS,'yash_slot.jpg')]);
  const sonarDir=path.join(RENDERS,'scene2','sonar'),sfxDir=path.join(RENDERS,'scene2','sonar_work','film','scene2','sonar');
  for(const n of order){video(n,path.join(sonarDir,n+'.mp4'),lens[n],'1920x1080');sound(n+'_sfx',path.join(sfxDir,n,'assets',n+'_sfx.wav'),lens[n])}
  for(const [name,time] of [['sonar_open',2.5],['sonar_loop',6.5]])
    run('ffmpeg',['-v','error','-y','-ss',time,'-i',path.join(ASSETS,'sonar_a.mp4'),'-frames:v','1','-q:v','2',path.join(ASSETS,name+'.jpg')]);
  run('ffmpeg',['-v','error','-y','-ss',5.2,'-i',path.join(ASSETS,'sonar_b.mp4'),'-frames:v','1','-q:v','2',path.join(ASSETS,'sonar_end.jpg')]);
  for(const id of names)sound(id,path.join(RENDERS,'narration','v4',id+'.wav'),Number(lines[id].duration));
  // Utkarsh's own call audio (camera audio of FOOTAGE:Video/normalpart4.mp4, src 0.7-3.8 s, cleaned, soft fades) under his live relay footage
  sound('utk_call',path.join(RENDERS,'scene2','v3b','utk_call.wav'),3.1);
  const C=names.filter(id=>lines[id].text).map(id=>({start:T.narration_starts[id],end:round(T.narration_starts[id]+Number(lines[id].duration)),text:lines[id].text}));
  fs.writeFileSync(path.join(HERE,'timeline.json'),JSON.stringify(T,null,2)+'\n');
  fs.writeFileSync(path.join(REPO,'film/captions/v3/s2b.json'),JSON.stringify(C,null,2)+'\n');
  fs.writeFileSync(path.join(HERE,'meta.json'),JSON.stringify({id:'scene2_v3b',name:'Scene 2 second half',width:1920,height:1080,fps:30,duration:T.duration})+'\n');
  const tpl=fs.readFileSync(path.join(HERE,'index.html.tpl'),'utf8');
  const clips=order.map(n=>{const s=T.segments.find(x=>x.name===n),offset=n==='sonar_a'?Math.max(0,round(lens[n]-(s.end-s.start))):0;return `<video id="${n}" class="clip" src="assets/${n}.mp4" data-start="${s.start}" data-duration="${Math.min(lens[n],round(s.end-s.start))}" data-media-start="${offset}" muted playsinline></video>`}).join('\n');
  const sounds=[
    ...names.map(n=>({id:n,start:T.narration_starts[n],duration:Number(lines[n].duration),file:n+'.wav'})),
    {id:'utk_call',start:round(T.segments.find(x=>x.name==='relay_2').start+0.5),duration:3.1,file:'utk_call.wav'},
    ...order.map(n=>{const s=T.segments.find(x=>x.name===n);return {id:n+'_sfx',start:s.start,duration:Math.min(lens[n],round(s.end-s.start)),offset:n==='sonar_a'?Math.max(0,round(lens[n]-(s.end-s.start))):0,file:n+'_sfx.wav'}})
  ].map(x=>`<audio id="audio_${x.id}" class="clip" src="assets/${x.file}" data-start="${x.start}" data-duration="${x.duration}" data-media-start="${x.offset||0}"></audio>`).join('\n');
  fs.writeFileSync(path.join(HERE,'index.html'),tpl.replaceAll('{{TIMELINE}}',JSON.stringify(T)).replaceAll('{{CAPTIONS}}',JSON.stringify(C)).replaceAll('{{SLOT_TIME}}',String(slotTime)).replaceAll('{{DURATION}}',String(T.duration)).replaceAll('{{CLIPS}}',clips).replaceAll('{{SOUNDS}}',sounds));
  if(process.argv.includes('--render')&&missing.length)throw Error('Missing final assets: '+missing.join(', '));
  run('hyperframes.cmd',['check'],HERE);
  if(process.argv.includes('--render')){
    const out=path.join(RENDERS,'scene2','v3b','scene2_v3b.mp4');
    fs.mkdirSync(path.dirname(out),{recursive:true});
    run('hyperframes.cmd',['render','-q','high','-f','30','-o',out],HERE);
  }
  if(process.argv.includes('--preview')){
    const out=path.join(REPO,'results','F0063','preview');fs.mkdirSync(out,{recursive:true});
    const early=T.beats.filter(b=>b.id!=='N3'),n3=T.beats.find(b=>b.id==='N3');
    const times=[.1,...early.map(b=>round(b.start+(b.id==='N2f'?.45:.7)*(b.end-b.start))),...['relay_1','relay_2','relay_3'].map(n=>round(T.segments.find(s=>s.name===n).start+3.6)),round(n3.start+.7*(n3.end-n3.start)),round(T.duration-1/30)];
    const ids=['push',...early.map(b=>b.id),'relay1','relay2','relay3','N3','sos'];
    const tmp=path.join(out,'snapshots');fs.mkdirSync(tmp,{recursive:true});
    run('hyperframes.cmd',['snapshot','--at',times.join(','),'--no-end','-o',tmp],HERE);
    const pngs=fs.readdirSync(tmp).filter(x=>x.endsWith('.png')).sort();
    if(pngs.length!==times.length)throw Error(`Expected ${times.length} snapshots, got ${pngs.length}`);
    for(let i=0;i<pngs.length;i++)fs.renameSync(path.join(tmp,pngs[i]),path.join(out,`${String(i).padStart(2,'0')}-${ids[i]}-1920.png`));
    fs.rmSync(tmp,{recursive:true,force:true});
    run('python',['-c',`from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__import__('sys').argv[1]); fs=sorted(p.glob('*-1920.png')); sheet=Image.new('RGB',(480,300*len(fs)),'#0a0d12'); d=ImageDraw.Draw(sheet)
for i,f in enumerate(fs):
 im=Image.open(f).convert('RGB').resize((480,270),Image.Resampling.LANCZOS); im.save(f.with_name(f.stem.replace('-1920','-480')+'.png')); sheet.paste(im,(0,i*300)); d.text((8,i*300+274),f.stem,fill='white')
sheet.save(p/'sheet-480.jpg',quality=92)`,out]);
  }
  console.log(JSON.stringify({duration:T.duration,placeholder_assets:missing,preview:process.argv.includes('--preview')}));
}
try{main()}catch(e){console.error(e.stack||e);process.exit(1)}
