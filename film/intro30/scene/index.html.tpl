<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080">
<script src="./gsap.min.js"></script>
<style>
@font-face{font-family:SceneSans;src:local('Segoe UI Variable Display'),local('Segoe UI Variable'),local('Segoe UI');font-weight:100 900}
*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#090b0c;color:#f3f5f8;font-family:SceneSans,sans-serif}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#090b0c}
.shot{position:absolute;inset:0;display:none;overflow:hidden}.shot video{width:100%;height:100%;object-fit:cover}
.placeholder{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;padding:80px;background:#555b60;color:#f3f5f8;font-size:52px;font-weight:600;letter-spacing:-.01em}
.placeholder:before{content:'FOOTAGE SLOT';position:absolute;top:48px;left:54px;color:#c1c8d2;font-size:23px;font-weight:700;letter-spacing:.16em}
.placeholder span{max-width:1050px}#shot_airplane_mode .placeholder span,#shot_push_to_talk .placeholder span{position:absolute;left:110px;width:900px;text-align:left}
#screen{position:absolute;width:360px;height:800px;overflow:hidden;transform-origin:0 0;transform:matrix3d({{MATRIX}});display:none;border:5px solid rgba(255,255,255,.68);border-radius:20px;box-shadow:0 18px 50px #0009}
#screen video{width:100%;height:100%;object-fit:fill}#screen:not(.preview){border:0;box-shadow:none}.screen-placeholder{width:100%;height:100%;display:grid;place-items:center;text-align:center;padding:25px;background:#747a7e;color:#fff;font-size:40px;font-weight:650}
#airplane{position:absolute;bottom:112px;left:210px;right:210px;display:none;text-align:center;background:rgba(9,12,17,.86);border:1px solid rgba(255,255,255,.11);border-radius:22px;padding:22px 35px;font-size:54px;font-weight:650;box-shadow:0 25px 65px #0007}
#shade{position:absolute;inset:0;background:#05070a;opacity:0;pointer-events:none}
/* Glass matches scene1; its position is supplied by shots.json panel_top. */
#glass{position:absolute;left:175px;width:1570px;height:250px;display:none;overflow:hidden;background:rgba(9,12,17,.86);border:1px solid rgba(255,255,255,.11);border-radius:30px;box-shadow:0 40px 90px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.08);backdrop-filter:blur(20px) saturate(115%)}
#glass:before{content:'';position:absolute;top:0;left:0;right:0;height:120px;background:linear-gradient(180deg,rgba(255,255,255,.06),transparent);pointer-events:none}
#glass .content{position:absolute;inset:35px 55px;display:flex;flex-direction:column;justify-content:center;gap:20px}
#glass .id{font-size:60px;font-weight:650;line-height:1.1;color:#f3f5f8}
#glass .id small{font-size:25px;color:#8fe3d4;font-weight:650;letter-spacing:.14em;vertical-align:middle;margin-right:24px}
#glass .promise{font-size:58px;line-height:1.1;font-weight:620;letter-spacing:-.018em;white-space:nowrap}
#handoff{position:absolute;bottom:105px;left:0;width:100%;text-align:center;font-size:58px;font-weight:620;text-shadow:0 3px 18px #000;display:none}
/* The expansion resolves into the existing title card's dark radial look and local type. */
#title{position:absolute;inset:0;display:none;place-items:center;background:radial-gradient(ellipse 1150px 700px at 50% 46%,#171c1b 0%,#0d1010 53%,#090b0c 100%);font-size:70px;font-weight:620;letter-spacing:-.018em;opacity:0}
</style></head><body>
<main id="root" data-composition-id="intro30" data-width="1920" data-height="1080" data-fps="30" data-duration="30">
  <div id="shots"></div><div id="screen" data-layout-allow-overlap></div><div id="airplane">No internet. No network. No Wi-Fi.</div>
  <div id="shade"></div>
  <div id="glass"><div class="content"><div class="id"><small>ISRO · PROBLEM STATEMENT</small>SIH26173</div><div class="promise">Speak. Phone to phone. No network.</div></div></div>
  <div id="handoff">Let's see it work.</div><div id="title" data-layout-allow-overlap>How the app works</div>
</main>
<script>
const D={{DATA}}, PREVIEW={{PREVIEW}};
const shots=document.getElementById('shots'), screen=document.getElementById('screen');
screen.classList.toggle('preview',PREVIEW);
for(const s of D.shots){
  const layer=document.createElement('div');layer.className='shot';layer.id='shot_'+s.id;
  if(s.asset){const v=document.createElement('video');v.src=s.asset;v.muted=true;v.playsInline=true;
    v.setAttribute('data-start',s.start);v.setAttribute('data-duration',s.dur);v.setAttribute('data-media-start','0');layer.appendChild(v)}
  else{const p=document.createElement('div');p.className='placeholder';const label=document.createElement('span');label.textContent=s.label;p.appendChild(label);layer.appendChild(p)}
  shots.appendChild(layer);
}
if(D.screen.asset){const v=document.createElement('video');v.src=D.screen.asset;v.muted=true;v.playsInline=true;
  v.setAttribute('data-start',D.screen.start);v.setAttribute('data-duration',D.screen.dur);v.setAttribute('data-media-start','0');screen.appendChild(v)}
else{const p=document.createElement('div');p.className='screen-placeholder';p.textContent='PHONE SCREEN\nAIRPLANE MODE / PTT';p.style.whiteSpace='pre-line';screen.appendChild(p)}
for(const s of D.sound){if(!s.asset)continue;const a=document.createElement('audio');a.src=s.asset;
  a.setAttribute('data-start',s.start);a.setAttribute('data-duration',s.dur);a.preload='auto';document.body.appendChild(a)}
const glass=document.getElementById('glass'),shade=document.getElementById('shade'),title=document.getElementById('title');
const handoff=document.getElementById('handoff'),airplane=document.getElementById('airplane');
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const ease=gsap.parseEase('power3.inOut');
function render(t){
  for(const s of D.shots)document.getElementById('shot_'+s.id).style.display=t>=s.start&&t<s.start+s.dur?'block':'none';
  screen.style.display=t>=12&&t<18?'block':'none';
  airplane.style.display=t>=12&&t<14?'block':'none';
  glass.style.display=t>=18?'block':'none';
  glass.style.top=D.panel_top+'px';
  handoff.style.display=t>=28&&t<29.2?'block':'none';
  if(t>=18){
    const grow=ease(clamp((t-28.15)/1.3));
    glass.style.left=(175*(1-grow))+'px';glass.style.top=(D.panel_top*(1-grow))+'px';
    glass.style.width=(1570+350*grow)+'px';glass.style.height=(250+830*grow)+'px';
    glass.style.borderRadius=(30*(1-grow))+'px';
    glass.style.opacity=1-clamp((t-29.0)/.5);
    glass.querySelector('.content').style.opacity=clamp((t-18)/.45)*(1-clamp((t-28.15)/.55));
  }
  shade.style.opacity=.83*ease(clamp((t-28.1)/1.35));
  title.style.display=t>=29?'grid':'none';title.style.opacity=clamp((t-29)/.5);
}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({}, {duration:30},0);
window.__timelines=window.__timelines||{};window.__timelines.intro30=tl;
window.addEventListener('hf-seek',e=>render(e.detail.time));render(0);
</script></body></html>
