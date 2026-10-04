<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080">
<script src="./gsap.min.js"></script>
<style>
@font-face{font-family:Segoe;src:local('Segoe UI Variable')}*{box-sizing:border-box}
html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#05070a;color:#f3f5f8;font-family:Segoe,'Segoe UI',sans-serif}
#root{position:relative;width:1920px;height:1080px;overflow:hidden}.scene{position:absolute;inset:0;display:none;overflow:hidden}
.full{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}
.intro-picture{position:absolute;inset:0;background-size:cover;background-position:center}
#intro-door{position:absolute;overflow:hidden;border:1px solid rgba(255,255,255,.24);background:rgba(5,7,10,.97);box-shadow:0 28px 80px rgba(0,0,0,.45)}
#intro-door .picture{position:absolute;inset:-60px;background-size:cover;background-position:center;filter:blur(40px) brightness(.42);opacity:.94}
#intro-door .matte{position:absolute;inset:0;background:rgba(10,13,18,.72)}
#intro-door .title{position:absolute;inset:0;display:grid;place-items:center;text-align:center;padding:0 90px;font-size:64px;font-weight:600;letter-spacing:-.015em;text-shadow:0 2px 16px #000;opacity:0}
.split .camera{position:absolute;left:0;top:0;width:1232px;height:1080px;overflow:hidden;background:#080b0e}
.camera-motion,.camera-still,.camera-last{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center center;background-position:center;background-size:cover}
.camera-motion{width:1920px;max-width:none;left:0;object-fit:cover;object-position:left center}
.camera-vachana .camera-motion{left:-250px}.camera-vivek .camera-motion{left:-200px}
.camera-still,.camera-last{background-size:1920px 1080px;background-repeat:no-repeat;background-position:left center}.camera-last{display:none}
.camera-vachana .camera-still,.camera-vachana .camera-last{background-position:-250px center}.camera-vivek .camera-still,.camera-vivek .camera-last{background-position:-200px center}
.feather{position:absolute;right:0;top:0;bottom:0;width:24px;background:linear-gradient(90deg,transparent,#0a0d12);pointer-events:none}
.app-field{position:absolute;left:1232px;top:0;width:688px;height:1080px;background:#0a0d12;display:flex;align-items:center;justify-content:center}
.push{position:absolute;inset:0;transform-origin:50% 45%}
.screen{height:1000px;max-width:560px;border-radius:32px;border:1px solid rgba(255,255,255,.14);overflow:hidden;background:#101820;box-shadow:0 22px 65px #000a}
.split .screen{position:relative;height:1000px;max-width:560px;border-radius:32px;border:1px solid rgba(255,255,255,.14);overflow:hidden;background:#101820;box-shadow:0 22px 65px #000a}
.screen video{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:#101820}
.app-only .sides{position:absolute;inset:-60px;background:#101820;background-size:cover;background-position:center;filter:blur(40px) brightness(.55);transform:scale(1.04)}
.app-only .screen{position:absolute;top:40px;left:50%;transform:translateX(-50%)}
.freeze{position:absolute;inset:0;background-position:center;background-size:contain;background-repeat:no-repeat;background-color:#101820}
.mock{position:absolute;inset:0;background:linear-gradient(180deg,#172630,#0b151c);font-family:Segoe,'Segoe UI',sans-serif;color:#e7eff2}
.mock-brand{height:95px;padding:45px 35px 0;font-size:30px;font-weight:600;border-bottom:1px solid #ffffff20}
.mock-content{position:absolute;left:25px;right:25px;top:180px;bottom:40px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:32px;line-height:1.35}
.mock-banner{width:100%;border-radius:20px;padding:32px 18px;background:#263947;box-shadow:0 8px 30px #0005}
.mock-caption{font-size:22px;color:#b9cbd3;margin:14px 0 30px}.mock-actions{display:flex;gap:12px;justify-content:center}.mock-btn{padding:17px 34px;border-radius:14px;background:#a83e4d;color:#fff;font-size:23px}.mock-btn.secondary{background:#33454d}
.sonar-preview{background:radial-gradient(circle at 51% 47%,#172025,#05080b 58%)}
.sonar-grid{position:absolute;inset:180px 380px;opacity:.22;transform:perspective(900px) rotateX(52deg);background:repeating-linear-gradient(0deg,transparent 0 79px,#9bb8c2 80px 81px),repeating-linear-gradient(90deg,transparent 0 79px,#9bb8c2 80px 81px)}
.sonar-point{position:absolute;left:50%;top:48%;width:12px;height:12px;border-radius:50%;background:#ff7884;box-shadow:0 0 24px 10px #c43c5070}
.sonar-ring{position:absolute;left:50%;top:48%;width:520px;height:520px;border:3px solid #db4e5eaa;border-radius:50%;transform:translate(-50%,-50%);box-shadow:0 0 40px #b43f4d35}
</style></head><body><div id="root" data-composition-id="scene3-v2" data-start="0" data-duration="{{DURATION}}" data-width="1920" data-height="1080">{{LAYERS}}</div>
<script>
const T={{TIMELINE}},rows=T.segments,by=Object.fromEntries(rows.map(r=>[r.name,r]));
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),ease=gsap.parseEase('power2.inOut'),easeDoor=gsap.parseEase('power3.inOut');
function mock(name,t){
  if(name==='vachana_sos')return t<9.1?'<div class="mock-banner">SOS message<div class="mock-caption">Preparing your request</div></div>':'<div class="mock-banner">Searching for nearby help…</div>';
  if(name==='vivek_app')return t<2.6?'<div class="mock-banner">SOS request nearby<div class="mock-caption">Someone needs help</div><div class="mock-actions"><div class="mock-btn secondary">Decline</div><div class="mock-btn">Accept</div></div></div>':t<7.63?'<div class="mock-banner">SOS request<div class="mock-caption">Accepted</div></div>':t<12.76?'<div class="mock-banner">SOS request<div class="mock-caption">Play message</div></div>':t<19.77?'<div class="mock-banner">Reply<div class="mock-caption">Recording response</div></div>':'<div class="mock-banner">Reply sent</div>';
  return t<4.96?'<div class="mock-banner">New response<div class="mock-caption">Open message</div></div>':'<div class="mock-banner">Vivek replied<div class="mock-caption">Help is coming</div></div>';
}
function render(t){
  for(const [id,seg] of [['vachana-field','vachana_sos'],['vivek-field','vivek_app']]){const field=document.getElementById(id),parent=document.getElementById('seg_'+seg);if(field.parentElement!==parent)parent.appendChild(field);field.style.transform='';field.style.opacity=1;}
  document.querySelectorAll('.scene').forEach(e=>e.style.display='none');
  const r=rows.find(x=>t>=x.start&&t<x.end);if(!r)return;const e=document.getElementById('seg_'+r.name);if(!e)return;e.style.display='block';
  if(r.name==='s3_open'||r.name==='lab_open'){const v=e.querySelector('video');v.style.width='1920px';v.style.left='0';v.style.objectPosition='center center';e.style.background='';}
  if(r.name==='intro'){
    const door=document.getElementById('intro-door'),shr=easeDoor(clamp((t-2.5)/.5));
    door.style.left=(734*shr)+'px';door.style.top=(70*shr)+'px';door.style.width=(1920-1468*shr)+'px';door.style.height=(1080-140*shr)+'px';door.style.borderRadius=(64*shr)+'px';door.style.opacity=1-shr;
    door.querySelector('.title').style.opacity=clamp((t-.3)/.35)*clamp((2.5-t)/.3);
  }
  if((r.name==='s3_open'&&t>=r.start+2.4)||(r.name==='lab_open'&&t>=r.end-.5)){
    const sos=r.name==='s3_open',f=ease(clamp((t-(sos?r.start+2.4:r.end-.5))/(sos ? .466667 : .5)));
    const v=e.querySelector('video');v.style.width=(1920-688*f)+'px';v.style.left='0';v.style.objectPosition=sos?'36.337% center':'29.07% center';
    e.style.background='#0a0d12';
    const app=document.getElementById(sos?'vachana-field':'vivek-field');
    app.style.transform=`translateX(${(1-f)*688}px)`;app.style.opacity=f;e.appendChild(app);
  }
  if(r.name==='vivek_app'){
    const st=t-r.start,C=T.vivek_camera,len=r.end-r.start,v=e.querySelectorAll('.camera-motion');
    const show=(el,on)=>{el.style.display=on?'block':'none'};
    show(e.querySelector('.hold-a'),st<C.m1_from);show(v[0],st>=C.m1_from&&st<C.m1_to);
    show(e.querySelector('.hold-b'),st>=C.m1_to&&st<C.m2_from);show(v[1],st>=C.m2_from&&st<C.m2_to);
    show(e.querySelector('.camera-last'),st>=C.m2_to);
    const s=1+.02*clamp(st/C.m1_from)+.01*clamp((st-C.m1_to)/Math.max(C.m2_from-C.m1_to,.001))+.01*clamp((st-C.m2_to)/Math.max(len-C.m2_to,.001));
    e.querySelector('.push').style.transform=`scale(${s})`;
  }
  if(r.name==='vachana_sos'){
    const st=t-r.start,motion=e.querySelector('.camera-motion'),initial=e.querySelector('.camera-still'),last=e.querySelector('.camera-last');
    const from=r.name==='vachana_sos'?0:9.99,stop=r.name==='vachana_sos'?7.77:15.94;
    motion.style.display=st>=from&&st<stop?'block':'none';initial.style.display=st<from?'block':'none';last.style.display=st>=stop?'block':'none';
    const push=st<from?st/Math.max(from,1):(st-stop)/Math.max(r.end-r.start-stop,1);
    const target=st<from?initial:last;target.style.transform=`scale(${1+.02*clamp(push)})`;
    // Leaving move (last 0.5 s): settle into the centred phone over the blurred camera frame that sos_in opens on.
    const f=ease(clamp((st-(r.end-r.start-.5))/.5)),cam=e.querySelector('.camera'),field=document.getElementById('vachana-field'),scr=field.querySelector('.screen');
    cam.style.width=(1232+688*f)+'px';last.style.backgroundPosition=`${-250*(1-f)}px center`;
    last.style.filter=f>0?`blur(${40*f}px) brightness(${1-.45*f})`:'';e.querySelector('.feather').style.opacity=1-f;
    field.style.background=`rgba(10,13,18,${1-f})`;
    const w=scr.offsetWidth,x0=1232+(688-w)/2,k=1080/1000;
    scr.style.transformOrigin='0 0';scr.style.transform=f>0?`translate(${((1920-w*k)/2-x0)*f}px,${-40*f}px) scale(${1+(k-1)*f})`:'';
  }
  for(const m of e.querySelectorAll('.mock'))m.querySelector('.mock-content').innerHTML=mock(m.dataset.slot,r.name==='end_hold'?T.slot_fields.vachana_response.duration:t-r.start);
}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({}, {duration:T.duration},0);
window.addEventListener('hf-seek',event=>render(event.detail.time));window.__timelines=window.__timelines||{};window.__timelines['scene3-v2']=tl;render(0);
</script></body></html>
