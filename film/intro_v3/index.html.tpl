<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080">
<link rel="stylesheet" href="./assets/glass/glass.css">
<script src="./assets/glass/glass.js"></script><script src="./gsap.min.js"></script>
<style>
@font-face{font-family:SceneSans;src:local('Segoe UI Variable Display'),local('Segoe UI Variable'),local('Segoe UI');font-weight:100 900}
*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#0e121a;color:var(--text);font-family:SceneSans,'Segoe UI',sans-serif}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#0e121a}
#camera{position:absolute;width:2950px;height:1660px;left:-1030px;top:-290px;object-fit:fill;transform-origin:50% 50%}
#shade{position:absolute;inset:0;background:linear-gradient(90deg,transparent 51%,rgba(5,8,13,.13) 61%,rgba(5,8,13,.42) 100%);pointer-events:none}
.phase{position:absolute;visibility:hidden}
#panel,#wave,#typed,#packet{box-shadow:0 30px 80px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.24)}
#panel{left:1020px;top:238px;width:800px;padding:48px 54px 54px;opacity:0}
#panel strong{display:block;font-size:76px;font-weight:650;letter-spacing:-.035em;line-height:1.04}
#panel .secondary{font-size:46px;line-height:1.27;color:var(--text);margin-top:20px;font-weight:530}
#wave{left:1020px;top:286px;width:820px;height:440px;padding:30px 18px;border-radius:30px}
#wave-bars{height:376px;display:flex;align-items:center;justify-content:center;gap:2px}
#wave-bars i{display:block;width:12px;flex:none;min-height:8px;border-radius:10px;background:#f7f9fc;box-shadow:0 0 11px rgba(255,255,255,.45),0 0 30px rgba(255,255,255,.18)}
#typed{left:1020px;top:338px;width:820px;height:338px;padding:47px 42px 48px;border-radius:30px;font-size:66px;font-weight:650;line-height:1.09;letter-spacing:-.035em}
#typed:before{content:'';position:absolute;left:42px;right:42px;bottom:42px;height:5px;border-radius:5px;background:rgba(255,255,255,.88);box-shadow:0 0 18px rgba(255,255,255,.38)}
#typed-words{position:relative;z-index:2;display:flex;align-content:center;align-items:center;flex-wrap:wrap;gap:3px 16px;height:100%}
#typed-words span{display:inline-block;opacity:0;transform:translateY(8px)}
#packet{left:1080px;top:492px;width:560px;padding:20px 25px;border-radius:25px;display:flex;align-items:center;gap:14px;font-size:28px;font-weight:640;line-height:1.14}
#packet svg{width:43px;height:43px;color:var(--text);flex:none;stroke-width:2.4}
#phone{left:1295px;top:106px;--glass-screen-height:760px;transform-origin:center center}
.glass-phone{overflow:visible!important;border-color:#101319!important;background:linear-gradient(110deg,#090b10,#282d34 15%,#0b0d12 25%,#090b10 80%,#3a4148 97%,#0c0e13)!important;box-shadow:0 32px 75px rgba(0,0,0,.52),0 54px 35px -42px rgba(0,0,0,.55),inset 2px 0 2px rgba(255,255,255,.28),inset -2px 0 3px rgba(255,255,255,.20)!important;transform-style:preserve-3d}
.glass-phone-screen{border:1px solid rgba(255,255,255,.14)}
.glass-phone::after{content:'';position:absolute;z-index:5;top:12%;left:4%;width:34%;height:70%;transform:skewX(-28deg);background:linear-gradient(90deg,transparent,rgba(255,255,255,.10),transparent);pointer-events:none}
.side-button{position:absolute;right:-19px;top:22%;width:5px;height:76px;border-radius:0 4px 4px 0;background:linear-gradient(90deg,#4b535d,#1b2027);box-shadow:1px 1px 2px #0008}
.side-button.short{top:35%;height:42px}
.notification{position:absolute;z-index:6;top:80px;left:20px;right:20px;min-height:83px;display:flex;align-items:center;gap:13px;padding:14px 17px;border-radius:18px;background:rgba(246,248,252,.97);color:#111821;box-shadow:0 15px 35px #0009;font-size:26px;font-weight:680;transform:translateY(-130px)}
.app-dot{width:35px;height:35px;border-radius:11px;background:linear-gradient(145deg,#f7f9fc,#a9b1bc);flex:none;box-shadow:inset 0 1px 0 #fff}
#circle{left:980px;top:80px;width:880px;height:880px;display:block;box-shadow:0 30px 80px rgba(0,0,0,.35),inset 0 2px 0 rgba(255,255,255,.72)}
#circle-content{position:relative;width:100%;height:100%}
#icons{position:absolute;inset:0}
.icon-tile{position:absolute;width:136px;text-align:center;color:#14181f;font-size:30px;font-weight:650;line-height:1.02;white-space:normal}
.icon-tile:nth-child(1){left:82px;top:165px}.icon-tile:nth-child(2){left:194px;top:78px}.icon-tile:nth-child(3){left:372px;top:45px}.icon-tile:nth-child(4){left:550px;top:78px}.icon-tile:nth-child(5){left:662px;top:165px}
.icon-drawing{position:relative;display:block;width:92px;height:92px;margin:0 auto 14px}
.icon-drawing .glass-icon{stroke-width:2.35}
.glass-cross path:nth-child(2){stroke:#14181f!important}
.icon-tile.gold{color:#5c410e;text-shadow:0 0 13px rgba(245,196,81,.56)}
.icon-tile.gold .icon-drawing{filter:drop-shadow(0 0 13px var(--gold))}
#circle-phone{position:absolute;left:311px;top:315px;--glass-screen-height:510px;transform-origin:center center}
#circle-phone .notification{top:55px;left:12px;right:12px;min-height:57px;padding:8px;font-size:17px;border-radius:11px;transform:none}
#circle-phone .app-dot{width:21px;height:21px;border-radius:6px}
#circle-phone .side-button{right:-19px;height:55px}
#circle-phone .side-button.short{height:30px}
#full{position:absolute;inset:0;display:grid;place-items:center;text-align:center;visibility:hidden;clip-path:circle(0px at 1477px 557px)}
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
const move=gsap.parseEase('power2.inOut'), enter=gsap.parseEase('power3.out');
const bars=$('wave-bars');for(let i=0;i<56;i++){const b=document.createElement('i');bars.append(b)}
const smoothed=[];let level=0;for(const sample of D.envelope){const tau=sample>level?.04:.16;level+=(sample-level)*(1-Math.exp(-1/(30*tau)));smoothed.push(level)}
Glass.phone($('phone'),{src:'./assets/home.png',kind:'img'});
Glass.phone($('circle-phone'),{src:'./assets/home.png',kind:'img'});
// Glass.phone replaces children, so the local notification overlays are added afterward.
for(const id of ['phone','circle-phone']){const host=$(id);for(const cls of ['side-button','side-button short']){const button=document.createElement('span');button.className=cls;host.append(button)}const banner=document.createElement('div');banner.className='notification';banner.innerHTML='<span class="app-dot"></span>New notification';host.append(banner)}
$('packet-lock').append(Glass.icon('lock'));
const names=[['tower','Tower'],['mobile-data','Mobile data'],['wifi','Wi-Fi'],['internet','Internet'],['bluetooth','Bluetooth LE']];
const tiles=names.map(([name,label])=>{const tile=document.createElement('div');tile.className='icon-tile'+(name==='bluetooth'?' gold':'');const drawing=document.createElement('span');drawing.className='icon-drawing';drawing.append(Glass.icon(name));tile.append(drawing);const text=document.createElement('span');text.textContent=label;tile.append(text);$('icons').append(tile);return drawing});
const typed=D.words.slice(16,22).map(w=>{const span=document.createElement('span');span.textContent=w.w;$('typed-words').append(span);return {time:w.s-.7781,el:span}});
function show(el,on){el.style.visibility=on?'visible':'hidden'}
function render(t){
  const camera=t<T.camera_end;show($('camera'),camera);show($('shade'),camera);
  if(camera)$('camera').style.transform=`scale(${1+.04*t/T.camera_end})`;
  const drift=8*t/D.duration;
  const panel=t>=T.panel&&t<T.built+.18;show($('panel'),panel);
  if(panel){const p=enter(clamp((t-T.panel)/.62));$('panel').style.opacity=p*(1-clamp((t-T.built)/.18));$('panel').style.transform=`translateX(${60*(1-p)+drift}px)`}
  const wave=t>=T.built&&t<T.message+.22;show($('wave'),wave);
  if(wave){const current=t+.7781-1.24,flat=move(clamp((t-T.message)/.22));for(let i=0;i<56;i++){const index=Math.max(0,Math.min(smoothed.length-1,Math.round(current*30)+(i-28)));const amp=Math.pow(clamp(smoothed[index]/.33),.8);bars.children[i].style.height=(8+352*amp*(1-flat))+'px'}const p=enter(clamp((t-T.built)/.62));$('wave').style.opacity=p*(1-clamp((t-T.message-.11)/.11));$('wave').style.transform=`translateX(${60*(1-p)+drift}px)`}
  const typing=t>=T.message&&t<T.phone2+.12;show($('typed'),typing);
  if(typing){const p=enter(clamp((t-T.message)/.52));$('typed').style.opacity=p;$('typed').style.transform=`translateX(${28*(1-p)+drift}px)`;for(const w of typed){const q=enter(clamp((t-w.time)/.18));w.el.style.opacity=q;w.el.style.transform=`translateY(${8*(1-q)}px)`}}
  const packet=t>=T.phone2+.12&&t<T.phone2+.52;show($('packet'),packet);
  if(packet){const p=move(clamp((t-T.phone2-.12)/.4));$('packet').style.transform=`translate(${drift+270*p}px,${-185*p-75*Math.sin(Math.PI*p)}px) scale(${1-.65*p}) rotate(${7*p}deg)`;$('packet').style.opacity=1-clamp((p-.72)/.28)}
  const phone=t>=T.phone2+.27&&t<T.no+.38;show($('phone'),phone);
  if(phone){const p=enter(clamp((t-T.phone2-.27)/.55)),fade=1-move(clamp((t-T.no-.05)/.33));$('phone').style.opacity=p*fade;$('phone').style.transform=`perspective(1100px) translateX(${drift+52*(1-p)}px) rotateY(${-6+6*p}deg) scale(${.91+.09*p})`;const b=clamp((t-(T.phone2+.27))/.45),drop=b<.78?enter(b/.78)*7:7*(1-move((b-.78)/.22));$('phone').querySelector('.notification').style.transform=`translateY(${-130*(1-enter(b))+drop}px)`}
  show($('phone').querySelector('.notification'),phone&&t<T.no+.08);
  const circle=t>=T.no-.05&&t<T.full-.3;show($('circle'),circle);
  show($('circle-phone').querySelector('.notification'),circle&&t>=T.no+.08);
  if(circle){const p=enter(clamp((t-T.no+.05)/.55));$('circle').style.opacity=p;$('circle').style.transform=`translateX(${drift}px) scale(${.93+.07*p})`;const settle=move(clamp((t-T.no+.05)/.48));$('circle-phone').style.transform=`perspective(1000px) translateY(${-220*(1-settle)}px) rotateY(${6-6*settle}deg) scale(${1.4-.4*settle})`;$('circle-phone').style.opacity=settle;tiles[4].parentElement.style.filter=`drop-shadow(0 0 ${12+8*Math.sin(t*9)**2}px rgba(245,196,81,.55))`}
  const crossStarts=[T.no,T.network,T.needed,T.needed+.18];
  tiles.forEach((drawing,i)=>{if(i<4)Glass.cross(drawing,clamp((t-crossStarts[i])/.35))});
  const full=t>=T.lets;show($('full'),full);
  if(full){const p=move(clamp((t-T.lets)/1.2));$('full').style.clipPath=p>=1?'none':`circle(${350+2100*p}px at 1420px 520px)`;$('full').querySelector('h1').style.opacity=clamp((t-(T.full-.31))/.24)}
  const cap=D.captions.find(c=>t>=c.start&&t<c.end);show($('caption'),!!cap&&t<T.full);if(cap)$('caption').textContent=cap.text;
}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({},{duration:D.duration},0);
window.__timelines=window.__timelines||{};window.__timelines.intro_v3=tl;
window.addEventListener('hf-seek',e=>render(e.detail.time));render(0);
</script></body></html>
