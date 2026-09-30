// Local layout preview when Python is unavailable. build.py is the production builder.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const slots=JSON.parse(fs.readFileSync(path.join(here,'slots.json'),'utf8'));
const fps=30,rows=[];let frame=0;
function add(name,seconds,extra={}){const n=Math.round(seconds*fps);rows.push({name,start:frame/fps,end:(frame+n)/fps,...extra});frame+=n;}
add('intro',3,{source:'FOOTAGE:Video/sospart1.mp4'});
add('s3_open',2.866667,{source:'FOOTAGE:Video/sospart1.mp4',source_in:0});
add('vachana_sos',slots.vachana_sos.duration,{camera:'FOOTAGE:Video/sospart1.mp4',camera_in:2.866667});
add('sos_in',2);add('sos_sonar',9);add('sos_dive',1.5);
add('lab_open',53/fps,{source:'FOOTAGE:Video/sospart2.mp4',source_in:3});
add('vivek_app',slots.vivek_app.duration,{camera:'FOOTAGE:Video/sospart2.mp4',camera_in:4.75});
add('vachana_response',slots.vachana_response.duration);add('end_hold',.5);
const by=Object.fromEntries(rows.map(r=>[r.name,r]));
const T={fps,duration:frame/fps,segments:rows,narration_starts:{N5:by.s3_open.start+.3,N6:by.sos_sonar.start+1},slot_fields:Object.fromEntries(Object.entries(slots).map(([k,v])=>[k,Object.fromEntries(Object.entries(v).filter(([key])=>key!=='path'))]))};
function video(src,start,duration,media=0,cls='full'){
 const id=`video_${src.replace(/[^a-z0-9]/gi,'_')}_${Math.round(start*fps)}`;
 return `<video id="${id}" class="${cls}" src="assets/${src}" data-start="${start.toFixed(6)}" data-duration="${duration.toFixed(6)}" data-media-start="${media}" muted playsinline></video>`;
}
function screen(name,r,hold=false){
 const slot=slots[name],w=(1000*1080/2290).toFixed(2);
 const mock=`<div class="mock" data-slot="${name}"><div class="mock-brand">iTantra</div><div class="mock-content"></div></div>`;
 const contents=hold?'<div class="freeze" style="background-image:url(assets/vachana_response_last.jpg)"></div>'+mock:video(`${name}.mp4`,r.start,r.end-r.start,0,'')+mock;
 return `<div class="screen" style="width:${w}px">${contents}</div>`;
}
const layers=[];
for(const r of rows){const {name,start,end}=r,d=end-start;
 if(name==='intro')layers.push('<div class="scene" id="seg_intro"><div class="intro-picture" style="background-image:url(assets/vachana_first.jpg)"></div><div id="intro-door"><div class="picture" style="background-image:url(assets/vachana_first.jpg)"></div><div class="matte"></div><div class="title">SOS: help from anyone nearby</div></div></div>');
 else if(name==='s3_open'||name==='lab_open')layers.push(`<div class="scene" id="seg_${name}">${video(name==='s3_open'?'vachana.mp4':'vivek.mp4',start,d)}</div>`);
 else if(name==='vachana_sos'||name==='vivek_app'){
  const key=name==='vachana_sos'?'vachana':'vivek',from=key==='vachana'?0:9.99,stop=key==='vachana'?7.77:15.94;
  const motion=video(`${key}.mp4`,start+from,stop-from,key==='vachana'?2.866667:1.75,'camera-motion');
  const first=key==='vachana'?'vachana_last.jpg':'vivek_first.jpg';
  layers.push(`<div class="scene split" id="seg_${name}"><div class="camera camera-${key}"><div class="camera-still" style="background-image:url(assets/${first})"></div>${motion}<div class="camera-last" style="background-image:url(assets/${key}_last.jpg)"></div><div class="feather"></div></div><div class="app-field" id="${key==='vachana'?'vachana-field':'vivek-field'}">${screen(name,r)}</div></div>`);
 }else if(name.startsWith('sos_'))layers.push(`<div class="scene sonar-preview" id="seg_${name}"><div class="sonar-grid"></div><div class="sonar-ring"></div><div class="sonar-point"></div></div>`);
 else if(name==='vachana_response')layers.push(`<div class="scene app-only" id="seg_${name}"><div class="sides"></div>${screen(name,r)}</div>`);
 else layers.push(`<div class="scene app-only" id="seg_end_hold"><div class="sides"></div>${screen('vachana_response',r,true)}</div>`);
}
let page=fs.readFileSync(path.join(here,'index.html.tpl'),'utf8');
page=page.replace('{{DURATION}}',T.duration.toFixed(6)).replace('{{TIMELINE}}',JSON.stringify(T)).replace('{{LAYERS}}',layers.join('\n'));
fs.writeFileSync(path.join(here,'index.html'),page);
fs.writeFileSync(path.join(here,'timeline.json'),JSON.stringify(T,null,2)+'\n');
console.log(`Wrote scene 3 v2 preview, ${T.duration.toFixed(3)} s`);
