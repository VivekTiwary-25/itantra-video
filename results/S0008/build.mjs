// Node equivalent of film/captions/build.py for this machine without Python.
import { readFileSync, writeFileSync, copyFileSync, mkdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

const repo = resolve(import.meta.dirname, '../..');
const here = join(repo, 'film/captions');
const data = JSON.parse(readFileSync(join(here, 'captions.json'), 'utf8'));
const scenes = ['scene1', 'scene2', 'scene3'];
const scene3 = JSON.parse(readFileSync(join(repo, 'film/scene3/main/timeline.json'), 'utf8'));
const scene2 = JSON.parse(readFileSync(join(repo, 'film/scene2/main/timeline.json'), 'utf8'));
if (data.fps !== 30 || JSON.stringify(data.size) !== '[1920,1080]') throw Error('Bad format');
if (data.durations.scene2 !== scene2.duration || data.durations.scene3 !== scene3.duration) throw Error('Stale scene duration');
for (const key of ['s3_open','vachana_sos','sos_in','sos_sonar','sos_dive','lab_a','vivek_sos','lab_b','vivek_reply','vachana_response']) {
  if (data.scene3_timing[key] !== scene3.segments.find(s => s.name === key).start) throw Error(`Stale scene 3 segment: ${key}`);
}
if (data.scene3_timing.end !== scene3.duration) throw Error('Stale scene 3 end');

const time = seconds => {
  let ms = Math.round(seconds * 1000);
  const h = Math.floor(ms / 3600000); ms %= 3600000;
  const m = Math.floor(ms / 60000); ms %= 60000;
  const s = Math.floor(ms / 1000); ms %= 1000;
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')},${String(ms).padStart(3,'0')}`;
};

function html(scene, duration, rows) {
  const payload = JSON.stringify(rows).replaceAll('<', '\\u003c');
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=1920,height=1080">
<script src="./gsap.min.js"></script>
<style>
@font-face{font-family:CaptionSans;src:local('Segoe UI Variable Display'),local('Segoe UI Variable'),local('Segoe UI');font-weight:100 900}
*{box-sizing:border-box}
html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:transparent}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:transparent}
#caption{position:absolute;bottom:42px;left:50%;transform:translateX(-50%);
  max-width:1200px;width:max-content;padding:12px 20px;border-radius:18px;
  color:#f3f5f8;background:rgba(5,7,10,.82);font:600 46px/1.16 CaptionSans,'Segoe UI',sans-serif;
  white-space:pre-line;text-align:center;box-shadow:0 3px 16px rgba(0,0,0,.2);
  visibility:hidden;opacity:0;pointer-events:none}
#caption.left{left:42px;right:auto;transform:none;max-width:650px;text-align:left}
#caption.right{left:auto;right:42px;transform:none;max-width:650px;text-align:right}
</style></head><body>
<div id="root" data-composition-id="${scene}_captions" data-start="0" data-duration="${duration}"
  data-width="1920" data-height="1080"><div id="caption" aria-live="off"></div></div>
<script>
const rows=${payload};
const caption=document.getElementById('caption');
function render(t){
  const row=rows.find(r=>t>=r.start&&t<r.end);
  if(!row){caption.style.visibility='hidden';caption.style.opacity='0';return}
  caption.className=row.position==='bottom'?'':row.position;
  caption.textContent=row.text;
  caption.style.visibility='visible';
  const alpha=Math.min(1,(t-row.start)/.12,(row.end-t)/.12);
  caption.style.opacity=String(Math.max(0,alpha));
}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});
tl.to({},{duration:${duration}},0);
window.__timelines=window.__timelines||{};
window.__timelines['${scene}_captions']=tl;
window.addEventListener('hf-seek',e=>render(e.detail.time));
render(0);
</script></body></html>
`;
}

for (const scene of scenes) {
  const folder = join(here, scene);
  const rows = data.captions.filter(r => r.scene === scene);
  const duration = data.durations[scene];
  let previousEnd = 0;
  for (const r of rows) {
    if (!(r.start >= 0 && r.start < r.end && r.end <= duration && r.start >= previousEnd - .001)) throw Error(`Invalid cue in ${scene}: ${r.text}`);
    if (!['bottom','left','right'].includes(r.position)) throw Error(`Invalid position in ${scene}`);
    const lines = r.text.split('\n');
    if (lines.length > 2 || lines.some(line => !line || line.length > 42)) throw Error(`Invalid text in ${scene}`);
    previousEnd = r.end;
  }
  mkdirSync(folder, {recursive:true});
  writeFileSync(join(folder, 'index.html'), html(scene, duration, rows));
  writeFileSync(join(folder, 'meta.json'), JSON.stringify({id:`${scene}_captions`,name:`${scene} captions`},null,2)+'\n');
  writeFileSync(join(folder, 'hyperframes.json'), JSON.stringify({paths:{blocks:'compositions',components:'compositions/components',assets:'assets'},media:{autoProxy:false}},null,2)+'\n');
  copyFileSync(join(repo,'film/vendor/gsap/gsap.min.js'),join(folder,'gsap.min.js'));
  writeFileSync(join(here,`${scene}.srt`),rows.map((r,i)=>`${i+1}\n${time(r.start)} --> ${time(r.end)}\n${r.text}`).join('\n\n')+'\n');
  process.stdout.write(`${scene}: ${rows.length} cues, ${duration.toFixed(3)} s\n`);
}
