<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080">
<link rel="stylesheet" href="assets/glass/glass.css"><script src="./gsap.min.js"></script><script src="assets/glass/glass.js"></script>
<style>
@font-face{font-family:SceneSans;src:local('Segoe UI Variable Display'),local('Segoe UI Variable'),local('Segoe UI')}
*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#0a0d12;color:var(--text);font-family:SceneSans,'Segoe UI',sans-serif}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#0a0d12}
#push,#sonar,#sos{position:absolute;inset:0;overflow:hidden}
#push{background:#0a0d12;transform-origin:50% 50%}
#phone{position:absolute;left:50%;top:50%;width:450px;height:1000px;transform:translate(-50%,-50%);border-radius:32px;overflow:hidden;background:#0c131b;border:1px solid rgba(255,255,255,.14);box-shadow:0 22px 65px rgba(0,0,0,.65);transform-origin:50% 50%}
#phone video,#phone img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
#phone img{z-index:1}#phone video{z-index:2}#phoneDark{position:absolute;inset:0;background:#050910;z-index:3;opacity:0}
#sonar video{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}
#sonarFade{position:absolute;inset:0;background:#050910;pointer-events:none}
#redTint{position:absolute;inset:0;background:radial-gradient(circle at 55% 48%,rgba(255,77,94,.46),rgba(116,20,38,.72));opacity:0;pointer-events:none}
#frost{position:absolute;inset:0;background:rgba(14,18,26,.12);backdrop-filter:blur(0px) saturate(1.4);opacity:0;pointer-events:none}
#sos{display:grid;place-items:center;opacity:0;pointer-events:none}
#sos .glass-card.full{display:grid;place-items:center;text-align:center}
#sos .card-title{max-width:1500px}
#lines{position:absolute;inset:0;pointer-events:none}
#lines .techline{display:none;top:64px;z-index:20}
#captions{position:absolute;inset:0;pointer-events:none}
#captions .caption{display:none;z-index:21}
</style></head><body>
<div id="root" data-composition-id="scene2_v3b" data-start="0" data-duration="32.4" data-width="1920" data-height="1080">
  <div id="push"><div id="phone"><img src="assets/yash_slot.jpg" alt=""><video id="yashSlot" class="clip" src="assets/yash_app.mp4" data-start="0" data-duration="1.4" data-media-start="11.724" muted playsinline></video><div id="phoneDark"></div></div></div>
  <div id="sonar">
    <video id="sonar_a" class="clip" src="assets/sonar_a.mp4" data-start="1.4" data-duration="7" data-media-start="0" muted playsinline></video>
    <video id="relay_1" class="clip" src="assets/relay_1.mp4" data-start="8.4" data-duration="6" data-media-start="0" muted playsinline></video>
    <video id="relay_2" class="clip" src="assets/relay_2.mp4" data-start="14.4" data-duration="6" data-media-start="0" muted playsinline></video>
    <video id="relay_3" class="clip" src="assets/relay_3.mp4" data-start="20.4" data-duration="6" data-media-start="0" muted playsinline></video>
    <video id="sonar_b" class="clip" src="assets/sonar_b.mp4" data-start="26.4" data-duration="6" data-media-start="0" muted playsinline></video>
    <div id="sonarFade"></div><div id="redTint"></div><div id="frost"></div>
  </div>
  <div id="sos"><div class="glass-card full"><h1 class="card-title">SOS: help from anyone nearby</h1></div></div>
  <div id="lines"><div class="techline">Speech becomes text on the phone</div><div class="techline">Encrypted: relays can't read it</div><div class="techline">Hops phone to phone over Bluetooth LE<small>6 hops shown on real phones</small></div></div>
  <div id="captions"></div>
  <audio id="narrationN2" class="clip" src="assets/N2.wav" data-start="1.4" data-duration="3.35"></audio>
  <audio id="narrationN3" class="clip" src="assets/N3.wav" data-start="30.4" data-duration="1.55"></audio>
  <audio id="sonarASfx" class="clip" src="assets/sonar_a_sfx.wav" data-start="1.4" data-duration="7"></audio>
  <audio id="relay1Sfx" class="clip" src="assets/relay_1_sfx.wav" data-start="8.4" data-duration="6"></audio>
  <audio id="relay2Sfx" class="clip" src="assets/relay_2_sfx.wav" data-start="14.4" data-duration="6"></audio>
  <audio id="relay3Sfx" class="clip" src="assets/relay_3_sfx.wav" data-start="20.4" data-duration="6"></audio>
  <audio id="sonarBSfx" class="clip" src="assets/sonar_b_sfx.wav" data-start="26.4" data-duration="6"></audio>
</div>
<script>
const T={{TIMELINE}},C={{CAPTIONS}};
const by=Object.fromEntries(T.segments.map(s=>[s.name,s]));
const id=x=>document.getElementById(x),clamp=x=>Math.max(0,Math.min(1,x));
const smooth=x=>{x=clamp(x);return x*x*(3-2*x)};
const capRoot=id('captions'),lineEls=[...document.querySelectorAll('#lines .techline')];
const capEls=C.map(c=>{const e=document.createElement('div');e.className='caption';e.textContent=c.text;capRoot.appendChild(e);return e});
function render(t){
  const push=id('push'),phone=id('phone'),sonar=id('sonar'),fade=id('sonarFade');
  const opening=smooth(t/1.4),darker=smooth((t-.48)/.65);
  push.style.display=t<1.4?'block':'none';
  phone.style.transform=`translate(-50%,-50%) scale(${(1+4.45*opening).toFixed(4)})`;
  id('phoneDark').style.opacity=darker.toFixed(3);
  sonar.style.display=t>=.84?'block':'none';sonar.style.opacity=smooth((t-.82)/.4).toFixed(3);
  const inFade=smooth((t-.84)/.56);
  fade.style.opacity=(1-inFade).toFixed(3);
  for(const n of ['sonar_a','relay_1','relay_2','relay_3','sonar_b']){
    const s=by[n],e=id(n);e.style.display=t>=s.start&&t<s.end?'block':'none';
  }
  if(t>=32.4)id('sonar_b').style.display='block';
  // The tint, blur and tiny scale motion carry the last moving sonar image into a frosted SOS field.
  const out=smooth((t-30.9)/1.5);
  id('redTint').style.opacity=(.68*out).toFixed(3);
  const frost=id('frost');frost.style.opacity=out.toFixed(3);frost.style.backdropFilter=`blur(${(32*out).toFixed(1)}px) saturate(1.4)`;
  const b=id('sonar_b');b.style.transform=t>=30.9?`scale(${(1+.025*out).toFixed(4)})`:'scale(1)';
  id('sos').style.opacity=smooth((t-31.1)/.8).toFixed(3);
  T.tech_lines.forEach((r,i)=>{const e=lineEls[i],active=t>=r.start&&t<r.end;e.style.display=active?'block':'none';
    if(active)e.style.opacity=(smooth((t-r.start)/.22)*smooth((r.end-t)/.22)).toFixed(3);
  });
  C.forEach((r,i)=>{const e=capEls[i],active=t>=r.start&&t<r.end;e.style.display=active?'block':'none';
    if(active)e.style.opacity=(smooth((t-r.start)/.1)*smooth((r.end-t)/.1)).toFixed(3);
  });
}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({}, {duration:T.duration},0);
window.addEventListener('hf-seek',e=>render(e.detail.time));window.__timelines=window.__timelines||{};window.__timelines.scene2_v3b=tl;render(0);
</script></body></html>
