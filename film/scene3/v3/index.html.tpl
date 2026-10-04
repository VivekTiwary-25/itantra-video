<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080">
<script src="./gsap.min.js"></script><script src="./assets/glass/glass.js"></script>
<link rel="stylesheet" href="./assets/glass/glass.css">
<style>
@font-face{font-family:SceneSans;src:local('Segoe UI Variable Display'),local('Segoe UI Variable'),local('Segoe UI');font-weight:100 900}
*{box-sizing:border-box}
html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#0a0d12;color:#f3f5f8;font-family:SceneSans,'Segoe UI',sans-serif}
#root{position:relative;width:1920px;height:1080px;overflow:hidden}
.scene{position:absolute;inset:0;display:none;overflow:hidden;background:#0a0d12}
.full{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}
/* F0024: matched to scene 2 v3b's last frame (same red radial as its #redTint at .68, footage dimmed): mean abs diff 1.7/255 */
.card-footage{filter:blur(40px) brightness(.22) saturate(.2);transform:scale(1.07)}
.card-red{position:absolute;inset:0;background:radial-gradient(circle at 55% 48%,rgba(255,77,94,.46),rgba(116,20,38,.72));opacity:.68}
#sos-card{display:grid;place-items:center;text-align:center;transform-origin:50% 50%;z-index:2}
#sos-card h1{font-size:64px;font-weight:650;line-height:1.08;margin:0}
.split .camera{position:absolute;left:0;top:0;width:1232px;height:1080px;overflow:hidden;background:#0a0d12}
.camera-motion{position:absolute;left:-250px;top:0;width:1920px;height:1080px;max-width:none;object-fit:cover}
.camera-vivek .camera-motion{left:-200px}
.feather{position:absolute;right:0;top:0;bottom:0;width:24px;background:linear-gradient(90deg,transparent,#0a0d12);pointer-events:none}
.app-field{position:absolute;left:1232px;top:0;width:688px;height:1080px;background:#0a0d12;display:flex;align-items:center;justify-content:center;overflow:hidden}
.screen{position:relative;height:1000px;max-width:560px;border-radius:32px;border:1px solid rgba(255,255,255,.14);overflow:hidden;background:#101820;box-shadow:0 22px 65px #000a;flex:none}
.screen video{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:#101820}
.accept-tap-ring{position:absolute;left:8%;top:14.35%;width:17.5%;height:4%;border:3px solid rgba(255,255,255,.95);border-radius:999px;box-shadow:0 0 0 5px rgba(255,255,255,.14);opacity:0;pointer-events:none}
#techline-layer,#caption-layer{position:absolute;inset:0;pointer-events:none;z-index:20}
#techline{display:none}
#caption{display:none}
</style></head>
<body><div id="root" data-composition-id="scene3-v3" data-start="0" data-duration="{{DURATION}}" data-width="1920" data-height="1080">
{{LAYERS}}
<div id="techline-layer"><div class="techline" id="techline"></div></div>
<div id="caption-layer"><div class="caption" id="caption"></div></div>
</div>
<script>
const T={{TIMELINE}},CAPTIONS={{CAPTIONS}},rows=T.segments;
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),ease=gsap.parseEase('power2.inOut');
const windowPunch=(t,up,upEnd,down,downEnd)=>ease(clamp((t-up)/(upEnd-up)))*(1-ease(clamp((t-down)/(downEnd-down))));
function takeover(field,camera,amount){
  const f=ease(clamp(amount));
  field.style.left=(1232*(1-f))+'px';field.style.width=(688+1232*f)+'px';
  field.querySelector('.screen').style.transform=`scale(${1+.08*f})`;
  if(camera){camera.style.transform=`translateX(${-1232*f}px)`;camera.style.opacity=1-f;}
}
function render(t){
  document.querySelectorAll('.scene').forEach(el=>el.style.display='none');
  for(const [id,name] of [['vachana-field','vachana_sos'],['vivek-field','vivek_app']]){
    const field=document.getElementById(id),parent=document.getElementById('seg_'+name);
    if(field.parentElement!==parent)parent.appendChild(field);
    field.style.left='1232px';field.style.width='688px';field.style.opacity='1';
    field.querySelector('.screen').style.transform='';
  }
  const tech=T.techlines.find(x=>t>=x.start&&t<x.end),te=document.getElementById('techline');
  te.style.display=tech?'block':'none';if(tech)te.textContent=tech.text;
  const cap=CAPTIONS.find(x=>t>=x.start&&t<x.end),ce=document.getElementById('caption');
  ce.style.display=cap?'block':'none';if(cap)ce.textContent=cap.text;
  const r=rows.find(x=>t>=x.start&&t<x.end);if(!r)return;
  const e=document.getElementById('seg_'+r.name);if(!e)return;e.style.display='block';
  const st=t-r.start;
  const phoneCentered=r.name==='vivek_app'&&!(st>=T.vivek_camera.m1_from&&st<T.vivek_camera.m1_to)&&!(st>=T.vivek_camera.m2_from&&st<T.vivek_camera.m2_to);
  const phoneSplit=r.name==='vachana_sos'||r.name==='vivek_app';
  ce.style.left=phoneCentered?'350px':phoneSplit?'550px':'50%';
  ce.style.maxWidth=phoneCentered?'640px':phoneSplit?'1020px':'1560px';
  if(r.name==='card_out'){
    const f=ease(clamp(st/1.6)),card=document.getElementById('sos-card');
    card.style.transform=`scale(${1-.78*f})`;
    card.style.opacity=1-clamp((st-.9)/.7);
  }
  if(r.name==='s3_open'&&st>=2.4){
    const f=ease(clamp((st-2.4)/.466667));
    const v=e.querySelector('video');v.style.width=(1920-688*f)+'px';v.style.objectPosition='36.337% center';
    e.style.background='#0a0d12';
    const field=document.getElementById('vachana-field');e.appendChild(field);
    field.style.left=(1232+688*(1-f))+'px';field.style.opacity=f;
  }
  if(r.name==='vachana_sos'){
    const camera=e.querySelector('.camera'),field=document.getElementById('vachana-field');
    const stillMoving=st<10.64-2.866667;
    camera.style.display=stillMoving?'block':'none';
    takeover(field,camera,(st-(10.64-2.866667-.5))/.5);
  }
  if(r.name==='lab_open'&&st>=r.end-r.start-.5){
    const field=document.getElementById('vivek-field');e.appendChild(field);
    const f=ease(clamp((st-(r.end-r.start-.5))/.5));
    takeover(field,null,1);field.style.opacity=f;
  }
  if(r.name==='vivek_app'){
    const C=T.vivek_camera,camera=e.querySelector('.camera'),field=document.getElementById('vivek-field');
    const v=e.querySelectorAll('.camera-motion');
    const in1=st>=C.m1_from&&st<C.m1_to,in2=st>=C.m2_from&&st<C.m2_to;
    v[0].style.display=in1?'block':'none';v[1].style.display=in2?'block':'none';
    camera.style.display=(in1||in2)?'block':'none';
    const visibility=in1?clamp((st-C.m1_from)/.25)*clamp((C.m1_to-st)/.25):
      in2?clamp((st-C.m2_from)/.25)*clamp((C.m2_to-st)/.25):0;
    takeover(field,camera,1-visibility);
    const banner=windowPunch(st,.6,1.2,T.slot_fields.vivek_app.accept_at+1,T.slot_fields.vivek_app.accept_at+1.6);
    const reply=windowPunch(st,17.9,18.5,19.0,19.6);
    const normal=1+.08*ease(clamp(1-visibility));
    field.querySelector('.screen').style.transformOrigin=banner||reply?'50% 0':'50% 50%';
    field.querySelector('.screen').style.transform=`scale(${normal+(1.9-normal)*banner+(1.6-normal)*reply})`;
    field.querySelector('.accept-tap-ring').style.opacity=ease(clamp((st-3.0)/.08))*(1-ease(clamp((st-3.12)/.12)));
  }
}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({}, {duration:T.duration},0);
window.addEventListener('hf-seek',event=>render(event.detail.time));
window.__timelines=window.__timelines||{};window.__timelines['scene3-v3']=tl;render(0);
</script></body></html>
