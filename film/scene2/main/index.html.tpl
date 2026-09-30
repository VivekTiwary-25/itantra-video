<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080">
<script src="./gsap.min.js"></script>
<style>
@font-face{font-family:Segoe;src:local('Segoe UI Variable')}*{box-sizing:border-box}
html,body{margin:0;width:1920px;height:1080px;background:#05070a;color:#f3f5f8;font-family:Segoe,'Segoe UI',sans-serif;overflow:hidden}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#05070a}
.scene{position:absolute;inset:0;display:none;overflow:hidden}
.full{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}
#benchVideo{transform-origin:0 0}
#door{position:absolute;overflow:hidden;border:1px solid rgba(255,255,255,.24);background:rgba(5,7,10,.97);box-shadow:0 28px 80px rgba(0,0,0,.45)}
#door .picture{position:absolute;inset:-60px;background-size:cover;background-position:center;filter:blur(40px) brightness(.42);opacity:.94}
#door .matte{position:absolute;inset:0;background:rgba(10,13,18,.72)}
#door .title{position:absolute;inset:0;display:grid;place-items:center;font-size:64px;font-weight:600;letter-spacing:-.015em;text-shadow:0 2px 16px #000;opacity:0}
.sides{position:absolute;inset:-60px;background-size:cover;background-position:center;filter:blur(40px) brightness(.55);transform:scale(1.04)}
.sides video{width:100%;height:100%;object-fit:cover}
.sides.self{background:#080d13;filter:blur(40px) brightness(.55)}
.screen{position:absolute;left:717px;top:0;width:486px;height:1080px;border-radius:28px;overflow:hidden;background:#0a0e14;box-shadow:0 12px 58px #000c,0 0 0 1px #ffffff22}
.screen video{width:100%;height:100%;object-fit:contain;background:#05070a}
.placeholder{width:100%;height:100%;display:grid;place-items:center;color:#8a939e;background:#0b1018;font-size:28px;letter-spacing:.04em;text-align:center}
.freeze{position:absolute;inset:0;background-size:cover;background-position:center}
#fade{position:absolute;inset:0;background:#05070a;pointer-events:none;display:none}
</style></head><body>
<div id="root" data-composition-id="scene2" data-start="0" data-duration="{{DURATION}}" data-width="1920" data-height="1080">
  <div class="scene" id="bench"><video id="benchVideo" class="clip full" src="{{BENCH}}" data-start="3" data-duration="5.2" data-media-start="0" muted playsinline></video></div>
  <div id="door"><div class="picture"></div><div class="matte"></div><div class="title">How the app works</div></div>
  <div id="sections">{{LAYERS}}</div><div id="fade"></div>
</div>
<script>
const T={{TIMELINE}}, A={{ASSETS}}, S={{SLOTS}};
const rows=T.segments, by=Object.fromEntries(rows.map(x=>[x.name,x]));
const bench=document.getElementById('bench'), bv=document.getElementById('benchVideo'), door=document.getElementById('door');
door.querySelector('.picture').style.backgroundImage=`url('${A.bench_start}')`;
const fade=document.getElementById('fade');
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), ease=gsap.parseEase('power3.inOut');
function render(t){
  document.querySelectorAll('.scene').forEach(e=>e.style.display='none');
  if(t<3.4){
    const grow=ease(clamp((t-.2)/1.2)), shrink=ease(clamp((t-2.6)/.8));
    const f=t<2.6?grow:1-shrink;
    door.style.display='block';door.style.left=(734*(1-f))+'px';door.style.top=(70*(1-f))+'px';
    door.style.width=(452+1468*f)+'px';door.style.height=(940+140*f)+'px';door.style.borderRadius=(64*(1-f))+'px';
    door.style.opacity=t<2.6?1:1-shrink;
    door.querySelector('.picture').style.opacity=.94*clamp((t-.2)/.6);
    door.querySelector('.title').style.opacity=clamp((t-1)/.35)*clamp((2.6-t)/.3);
  }else door.style.display='none';
  if(t>=2.6&&t<by.vachana_send.start+.5){
    bench.style.display='block';
    const f=ease(clamp((t-5.4)/2.3)), scale=1+0.8*f;
    const cx=820+80*f,cy=930-350*f;
    bv.style.transform=`translate(${f*(960-scale*cx)}px,${f*(540-scale*cy)}px) scale(${scale})`;
  }
  let active=rows.find(r=>t>=r.start&&t<r.end&&r.name!=='doorway'&&r.name!=='bench');
  if(active){const e=document.getElementById('seg_'+active.name);if(e)e.style.display='block'}
  if(t>=by.vachana_send.start&&t<by.vachana_send.start+.5){
    const e=document.getElementById('seg_vachana_send');e.style.display='block';e.style.opacity=clamp((t-by.vachana_send.start)/.5);
  }else document.getElementById('seg_vachana_send').style.opacity=1;
  fade.style.display=active&&active.name==='sonar_b_fade'?'block':'none';
  if(fade.style.display==='block')fade.style.opacity=.91*clamp((t-by.sonar_b_fade.start)/2.6);
}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({}, {duration:T.duration},0);
window.addEventListener('hf-seek',e=>render(e.detail.time));
window.__timelines=window.__timelines||{};window.__timelines.scene2=tl;render(0);
</script></body></html>
