<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080">
<link rel="stylesheet" href="./assets/glass/glass.css">
<script src="./assets/glass/glass.js"></script><script src="./gsap.min.js"></script>
<style>
@font-face{font-family:SceneSans;src:local('Segoe UI Variable Display'),local('Segoe UI Variable'),local('Segoe UI');font-weight:100 900}
*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#0e121a;color:var(--text);font-family:SceneSans,'Segoe UI',sans-serif}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#0e121a}
#camera{position:absolute;width:2208px;height:1242px;left:-288px;top:-81px;object-fit:fill}
#shade{position:absolute;inset:0;background:linear-gradient(90deg,transparent 40%,rgba(6,9,14,.22));pointer-events:none}
.phase{position:absolute;visibility:hidden}
#panel{left:1130px;top:260px;width:700px;transform:translateX(35px);opacity:0}
#panel strong{font-size:42px;font-weight:650}
#wave{left:1130px;top:425px;width:700px;height:178px;padding:32px 38px;border-radius:22px}
#wave-bars{height:110px;display:flex;align-items:center;justify-content:center;gap:5px}
#wave-bars i{display:block;width:7px;min-height:3px;border-radius:5px;background:#f3f5f8;box-shadow:0 0 9px rgba(77,163,255,.45)}
#typed{left:1130px;top:440px;width:700px;height:150px;padding:26px 34px;border-radius:22px;font-size:39px;font-weight:610;line-height:1.15}
#typed:before{content:'';position:absolute;left:34px;right:34px;top:99px;height:2px;background:rgba(77,163,255,.65)}
#packet{left:1195px;top:472px;min-width:475px;padding:21px 24px;border-radius:20px;display:flex;align-items:center;gap:16px;font-size:31px;font-weight:600;white-space:nowrap}
#packet svg{width:34px;height:34px;color:var(--blue);flex:none}
#phone{left:1390px;top:215px;--glass-screen-height:615px;transform-origin:center center}
.notification{position:absolute;z-index:2;top:83px;left:22px;right:22px;min-height:76px;display:flex;align-items:center;gap:10px;padding:12px;border-radius:15px;background:rgba(246,248,252,.96);color:#111821;box-shadow:0 12px 24px #0006;font-size:22px;font-weight:650;transform:translateY(-125px)}
.app-dot{width:29px;height:29px;border-radius:8px;background:#4da3ff;flex:none}
#circle{left:1087px;top:167px;width:780px;height:780px;display:block}
#circle-content{position:relative;width:100%;height:100%}
#icons{position:absolute;left:28px;right:28px;top:104px;display:flex;align-items:start;justify-content:space-between;gap:10px}
.icon-tile{position:relative;width:130px;text-align:center;color:#14181f;font-size:26px;font-weight:620;line-height:1.08}
.icon-drawing{position:relative;display:block;width:66px;height:66px;margin:0 auto 14px}
.icon-tile.gold{color:#7b5510;text-shadow:0 0 15px rgba(245,196,81,.65)}
.icon-tile.gold .icon-drawing{filter:drop-shadow(0 0 10px var(--gold))}
#circle-phone{position:absolute;left:285px;top:290px;--glass-screen-height:420px;transform-origin:center center}
#circle-phone .notification{top:53px;left:12px;right:12px;min-height:52px;padding:7px;font-size:15px;border-radius:11px;transform:none}
#circle-phone .app-dot{width:18px;height:18px;border-radius:5px}
#full{position:absolute;inset:0;display:grid;place-items:center;text-align:center;visibility:hidden;clip-path:circle(0px at 1477px 557px)}
#full h1{font-size:64px}
#caption{position:absolute;bottom:54px;left:50%;z-index:10;visibility:hidden}
</style></head><body>
<main id="root" data-composition-id="intro_v3" data-start="0" data-duration="13.8" data-width="1920" data-height="1080" data-fps="30">
  <video id="camera" src="./assets/camera.mp4" data-start="0" data-duration="13.16" data-media-start="0" muted playsinline></video>
  <div id="shade"></div>
  <div id="panel" class="glass-panel phase"> <strong>Vachana</strong><span class="secondary">Team chmod 777<br>Problem statement SIH26173</span></div>
  <div id="wave" class="glass-panel phase"><div id="wave-bars"></div></div>
  <div id="typed" class="glass-panel phase"><span id="typed-words"></span></div>
  <div id="packet" class="glass-panel phase"><span id="packet-lock"></span><span>message travels from phone to phone</span></div>
  <div id="phone" class="phase"></div>
  <div id="circle" class="glass-circle phase"><div id="circle-content"><div id="icons"></div><div id="circle-phone"></div></div></div>
  <div id="full" class="glass-card full"><h1>How the app works</h1></div>
  <div id="caption" class="caption"></div>
  <audio id="voice" src="./assets/voice.wav" data-start="0.4619" data-duration="12.78" preload="auto"></audio>
  <audio id="sfx" src="./assets/sfx.wav" data-start="0" data-duration="13.8" preload="auto"></audio>
</main>
<script>
const D={{DATA}}, T=D.timings, $=id=>document.getElementById(id), clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const ease=gsap.parseEase('power2.inOut');
const bars=$('wave-bars');for(let i=0;i<56;i++){const b=document.createElement('i');bars.append(b)}
Glass.phone($('phone'),{src:'./assets/home.png',kind:'img'});
Glass.phone($('circle-phone'),{src:'./assets/home.png',kind:'img'});
// Glass.phone replaces children, so the local notification overlays are added afterward.
for(const id of ['phone','circle-phone']){const host=$(id);const banner=document.createElement('div');banner.className='notification';banner.innerHTML='<span class="app-dot"></span>New notification';host.append(banner)}
$('packet-lock').append(Glass.icon('lock'));
const names=[['tower','Tower'],['mobile-data','Mobile data'],['wifi','Wi-Fi'],['internet','Internet'],['bluetooth','Bluetooth LE']];
const tiles=names.map(([name,label])=>{const tile=document.createElement('div');tile.className='icon-tile'+(name==='bluetooth'?' gold':'');const drawing=document.createElement('span');drawing.className='icon-drawing';drawing.append(Glass.icon(name));tile.append(drawing);const text=document.createElement('span');text.textContent=label;tile.append(text);$('icons').append(tile);return drawing});
const typed=D.words.slice(16,22);
function show(el,on){el.style.visibility=on?'visible':'hidden'}
function render(t){
  const camera=t<T.camera_end;show($('camera'),camera);show($('shade'),camera);
  const panel=t>=T.panel&&t<T.built+.18;show($('panel'),panel);
  if(panel){const p=ease(clamp((t-T.panel)/.42));$('panel').style.opacity=p*(1-clamp((t-T.built)/.18));$('panel').style.transform=`translateX(${35*(1-p)}px)`}
  const wave=t>=T.built&&t<T.message+.15;show($('wave'),wave);
  if(wave){let current=t+.7781-1.24;const vals=D.envelope;for(let i=0;i<56;i++){const index=Math.round(current*30)+(i-28);const amp=clamp((vals[Math.max(0,Math.min(vals.length-1,index))]||0)/.36);bars.children[i].style.height=(4+96*amp)+'px'}$('wave').style.opacity=ease(clamp((t-T.built)/.25))*(1-clamp((t-T.message)/.15))}
  const typing=t>=T.message&&t<T.phone2+.12;show($('typed'),typing);
  if(typing){$('typed-words').textContent=typed.filter(w=>w.s-.7781<=t).map(w=>w.w).join(' ');$('typed').style.opacity=1}
  const packet=t>=T.phone2+.12&&t<T.phone2+.52;show($('packet'),packet);
  if(packet){const p=ease(clamp((t-T.phone2-.12)/.4));$('packet').style.transform=`translate(${p*175}px,${-p*165-65*Math.sin(Math.PI*p)}px) scale(${1-.72*p})`;$('packet').style.opacity=1-clamp((p-.72)/.28)}
  const phone=t>=T.phone2+.27&&t<T.no+.15;show($('phone'),phone);
  if(phone){$('phone').style.opacity=ease(clamp((t-T.phone2-.27)/.2))*(1-clamp((t-T.no)/.15));$('phone').querySelector('.notification').style.transform=`translateY(${(-120+120*ease(clamp((t-T.phone2-.39)/.18)))}px)`}
  const circle=t>=T.no-.05&&t<T.full;show($('circle'),circle);
  if(circle){$('circle').style.opacity=ease(clamp((t-T.no+.05)/.23));$('circle').style.transform=`scale(${.86+.14*ease(clamp((t-T.no+.05)/.35))})`}
  const crossStarts=[T.no,T.network,T.needed,T.needed+.18];
  tiles.forEach((drawing,i)=>{if(i<4)Glass.cross(drawing,clamp((t-crossStarts[i])/.17))});
  const full=t>=T.lets;show($('full'),full);
  if(full){const p=ease(clamp((t-T.lets)/1.2));$('full').style.clipPath=p>=1?'none':`circle(${350+2100*p}px at 1477px 557px)`;$('full').querySelector('h1').style.opacity=clamp((t-(T.full-.31))/.24)}
  const cap=D.captions.find(c=>t>=c.start&&t<c.end);show($('caption'),!!cap&&t<T.full);if(cap)$('caption').textContent=cap.text;
}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({},{duration:D.duration},0);
window.__timelines=window.__timelines||{};window.__timelines.intro_v3=tl;
window.addEventListener('hf-seek',e=>render(e.detail.time));render(0);
</script></body></html>
