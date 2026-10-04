<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080">
<link rel="stylesheet" href="./assets/glass/glass.css"><script src="./assets/glass/glass.js"></script><script src="./gsap.min.js"></script>
<style>
@font-face{font-family:SceneSans;src:local('Segoe UI Variable Display'),local('Segoe UI Variable'),local('Segoe UI');font-weight:100 900}
*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#0e121a;color:var(--text);font-family:SceneSans,'Segoe UI',sans-serif}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#0e121a}
.camera{position:absolute;width:2950px;height:1660px;top:-290px;object-fit:fill;transform-origin:50% 50%}
#opening-camera{left:-1030px}#explain-camera{left:-700px}#bench-camera{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}
#shade{position:absolute;inset:0;background:linear-gradient(90deg,transparent 47%,rgba(5,8,13,.17) 58%,rgba(5,8,13,.43) 100%);pointer-events:none}
#opening-panel{position:absolute;left:1020px;top:238px;width:800px;padding:48px 54px 54px;box-shadow:0 30px 80px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.24)}
#opening-panel strong{display:block;font-size:76px;font-weight:650;letter-spacing:-.035em;line-height:1.04}
#opening-panel .secondary{font-size:46px;line-height:1.27;color:var(--text);margin-top:20px;font-weight:530}
#stage{position:absolute;left:1020px;top:145px;width:800px;height:790px;overflow:hidden;padding:0;border-radius:30px;box-shadow:0 30px 80px rgba(0,0,0,.42),inset 0 1px 0 rgba(255,255,255,.24)}
#stage:before{content:'';position:absolute;inset:15px;border:1px solid rgba(255,255,255,.08);border-radius:20px;pointer-events:none}
#orbit{position:absolute;left:75px;top:75px;width:650px;height:650px;border:1px solid rgba(255,255,255,.19);border-radius:50%;opacity:.65}
#orbit:after{content:'';position:absolute;inset:56px;border:1px dashed rgba(255,255,255,.14);border-radius:50%}
.badge{position:absolute;width:160px;height:150px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:5px;padding:10px;font-size:32px;line-height:1.02;font-weight:650;white-space:normal;background:linear-gradient(160deg,rgba(255,255,255,.18),rgba(255,255,255,.03) 35%),rgba(28,34,44,.75);border:1px solid rgba(255,255,255,.3);box-shadow:0 12px 32px #0006,inset 0 1px #ffffff31;transform-origin:center}
.badge:nth-child(1){left:28px;top:92px}.badge:nth-child(2){left:610px;top:92px}.badge:nth-child(3){left:13px;top:335px}.badge:nth-child(4){left:627px;top:335px}.badge:nth-child(5){left:305px;top:620px;width:190px;height:150px}
.badge .icon{position:relative;display:block;width:48px;height:48px;flex:none}.badge .glass-icon{stroke-width:2.2}
.badge.gold{color:var(--gold);border-color:rgba(245,196,81,.52);box-shadow:0 0 36px rgba(245,196,81,.28),inset 0 1px rgba(255,255,255,.4)}
.badge.gold .icon{filter:drop-shadow(0 0 9px rgba(245,196,81,.9))}
#phone-a,#phone-b{position:absolute;top:153px;--glass-screen-height:445px;transform-origin:center center;overflow:visible!important}
#phone-a{left:286px}#phone-b{left:530px}
.glass-phone{border-color:#101319!important;background:linear-gradient(110deg,#090b10,#282d34 15%,#0b0d12 25%,#090b10 80%,#3a4148 97%,#0c0e13)!important;box-shadow:0 24px 62px rgba(0,0,0,.62),inset 2px 0 2px rgba(255,255,255,.28),inset -2px 0 3px rgba(255,255,255,.20)!important}
.glass-phone-screen{border:1px solid rgba(255,255,255,.14)}
.side-button{position:absolute;right:-19px;top:22%;width:5px;height:55px;border-radius:0 4px 4px 0;background:linear-gradient(90deg,#4b535d,#1b2027)}
.side-button.short{top:35%;height:31px}
#speech{position:absolute;left:12px;right:12px;top:39%;min-height:106px;padding:14px 12px;border-radius:14px;background:rgba(11,19,31,.92);border:1px solid rgba(77,163,255,.65);box-shadow:0 0 22px rgba(77,163,255,.19);font-size:22px;font-weight:630;line-height:1.12;text-align:center;overflow:hidden}
#wave{height:64px;display:flex;align-items:center;justify-content:center;gap:2px}#wave i{display:block;width:3px;min-height:3px;border-radius:3px;background:#f6f9ff;box-shadow:0 0 8px #fff8}
#speech-text{display:block;overflow:hidden;white-space:normal}
#packet{position:absolute;left:250px;top:390px;width:105px;height:65px;border-radius:17px;background:linear-gradient(145deg,#283950,#111923);border:1px solid rgba(77,163,255,.7);box-shadow:0 0 22px rgba(77,163,255,.3),0 12px 25px #0009;display:flex;align-items:center;justify-content:center;gap:8px}
#packet .glass-icon{width:27px;height:27px;color:#f3f5f8}
#packet-lines{width:43px}#packet-lines i{display:block;height:4px;border-radius:4px;background:#d8e4f4;margin:5px 0}#packet-lines i:last-child{width:65%}
#link{position:absolute;left:290px;top:406px;width:315px;height:130px;overflow:visible;pointer-events:none}
#link path{fill:none;stroke:var(--blue);stroke-width:3;stroke-dasharray:8 10;opacity:.75}
#bt{position:absolute;left:393px;top:325px;width:60px;height:60px;color:var(--gold);filter:drop-shadow(0 0 16px var(--gold))}
#sound{position:absolute;left:650px;top:112px;width:115px;height:95px;color:#f3f5f8}
#sound path{fill:none;stroke:currentColor;stroke-width:6;stroke-linecap:round}
#title{position:absolute;left:0;top:0;width:1920px;height:1080px;display:grid;place-items:center;text-align:center;border-radius:0;background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,0) 30%),rgba(14,18,26,.86);z-index:8}
#title h1{font-size:82px}
#caption{position:absolute;bottom:54px;left:50%;z-index:10;visibility:hidden}
</style></head><body>
<main id="root" data-composition-id="intro_v3" data-start="0" data-duration="33.6" data-width="1920" data-height="1080" data-fps="30">
  <video id="opening-camera" class="camera" src="./assets/opening.mp4" data-start="0" data-duration="6.842" data-media-start="0" muted playsinline></video>
  <video id="explain-camera" class="camera" src="./assets/explain.mp4" data-start="6.842" data-duration="25.758" data-media-start="0" muted playsinline></video>
  <video id="bench-camera" src="./assets/bench.mp4" data-start="32.6" data-duration="1" data-media-start="0" muted playsinline></video>
  <div id="shade"></div>
  <div id="opening-panel" class="glass-panel"><strong>Vachana</strong><span class="secondary">Team chmod 777<br>Problem statement SIH26173</span></div>
  <div id="stage" class="glass-panel"><div id="orbit"></div><div id="badges"></div><div id="phone-a"><div id="speech"><div id="wave"></div><span id="speech-text">Speech to text on the phone, without internet</span></div></div><div id="phone-b"></div><svg id="link" viewBox="0 0 315 130"><path d="M0 70 Q150 -35 315 70"/></svg><div id="packet"><span id="packet-lock"></span><span id="packet-lines"><i></i><i></i></span></div><span id="bt"></span><svg id="sound" viewBox="0 0 115 95"><path d="M17 33 Q50 48 17 63 M42 19 Q91 48 42 77 M68 7 Q129 48 68 89"/></svg></div>
  <div id="title" class="glass-card full" data-layout-allow-overflow><h1>How the app works</h1></div>
  <div id="caption" class="caption"></div>
  <audio id="voice" src="./assets/voice.wav" data-start="0.4619" data-duration="30.88" preload="auto"></audio>
</main>
<script>
const D={{DATA}}, T=D.timeline.beats, $=id=>document.getElementById(id), clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const ease=gsap.parseEase('power2.inOut'), out=gsap.parseEase('power3.out');
function show(el,yes){el.style.visibility=yes?'visible':'hidden'}
const speech=$('speech');
Glass.phone($('phone-a'),{src:'./assets/home.png',kind:'img'});
Glass.phone($('phone-b'),{src:'./assets/home.png',kind:'img'});
for(const id of ['phone-a','phone-b']){const host=$(id);for(const cls of ['side-button','side-button short']){const button=document.createElement('span');button.className=cls;host.append(button)}}
// The supplied screen stays intact; the speech overlay is a separate temporary layer.
$('phone-a').append(speech);
const badgeInfo=[['tower','Tower'],['mobile-data','Mobile data'],['wifi','Wi-Fi'],['internet','Internet'],['bluetooth','Bluetooth LE']];
const badges=badgeInfo.map(([icon,label],i)=>{const tile=document.createElement('div');tile.className='badge glass-panel'+(i===4?' gold':'');const mark=document.createElement('span');mark.className='icon';mark.append(Glass.icon(icon));tile.append(mark,document.createTextNode(label));$('badges').append(tile);return {tile,mark}});
$('packet-lock').append(Glass.icon('lock'));$('bt').append(Glass.icon('bluetooth'));
const bars=[];for(let i=0;i<35;i++){const bar=document.createElement('i');$('wave').append(bar);bars.push(bar)}
function render(t){
  const intro=t<T.bench,short=t<D.timeline.cut;
  show($('opening-camera'),short);show($('explain-camera'),!short&&intro);show($('bench-camera'),!intro);show($('shade'),intro);
  if(short)$('opening-camera').style.transform=`scale(${1+.04*t/13.16})`;
  else if(intro)$('explain-camera').style.transform=`scale(${1+.04*(t-D.timeline.cut)/25.758})`;
  show($('opening-panel'),short&&t>=.582);
  if(short){const p=out(clamp((t-.582)/.62));$('opening-panel').style.opacity=p;$('opening-panel').style.transform=`translateX(${60*(1-p)+8*t/13.8}px)`}
  $('stage').style.display=!short&&intro?'block':'none';
  const badgesPhase=t<T.wave,merge=ease(clamp((t-T.wave)/.7));
  $('orbit').style.opacity=badgesPhase?'.65':String(.65*(1-merge));
  badges.forEach(({tile,mark},i)=>{
    const appear=out(clamp((t-(T.badges+i*.8))/.45));
    tile.style.opacity=String(appear*(1-merge));
    tile.style.transform=`scale(${.65+.35*appear-.25*merge}) translateY(${-24*(1-appear)-38*merge}px)`;
    if(i<4)Glass.cross(mark,clamp((t-(T.badges+i*.8+.35))/.35));
  });
  const shifting=ease(clamp((t-T.message)/.65));
  $('phone-a').style.transform=`translateX(${-242*shifting}px)`;
  const second=out(clamp((t-(T.message+.55))/.65));
  show($('phone-b'),second>0);$('phone-b').style.transform=`translateX(${255*(1-second)}px)`;
  const wavePhase=t>=T.wave&&t<T.message+.55;
  show($('speech'),wavePhase);
  if(wavePhase){
    const textIn=ease(clamp((t-(T.wave+2.25))/1.15)),fold=ease(clamp((t-T.message)/.55));
    $('speech').style.transform=`scale(${1-.77*fold}) translate(${55*fold}px,${-5*fold}px)`;
    $('speech').style.opacity=String(1-fold);
    $('wave').style.opacity=String(1-textIn);
    $('speech-text').style.opacity=String(textIn);
    $('speech-text').style.maxHeight=`${115*textIn}px`;
    const centre=Math.round((t-D.envelope.starts_at_film)*30);
    for(let i=0;i<bars.length;i++){
      const n=clamp(centre+i-17,0,D.envelope.rms.length-1),a=D.envelope.rms[n];
      bars[i].style.height=`${3+56*Math.pow(clamp(a/.36),.8)*(1-textIn)}px`;
    }
  }
  const flight=ease(clamp((t-(T.message+.85))/3.0));
  show($('link'),t>=T.message+.45&&t<T.read);$('link').style.opacity=String(Math.sin(Math.PI*clamp((t-T.message-.45)/(T.read-T.message-.45)))*.6);
  show($('bt'),t>=T.message+.45&&t<T.read+.5);$('bt').style.opacity=String(Math.min(1,Math.max(0,(t-T.message-.45)*2),Math.max(0,(T.read+.5-t)*2)));
  show($('packet'),t>=T.message&&t<T.read+.15);
  if(t>=T.message){$('packet').style.transform=`translate(${310*flight}px,${-95*Math.sin(Math.PI*flight)}px) scale(${1-.2*flight})`;$('packet').style.opacity=String(1-ease(clamp((t-(T.read-.25))/.4)))}
  show($('sound'),t>=T.read&&t<T.title);if(t>=T.read){const p=out(clamp((t-T.read)/.35));$('sound').style.opacity=String(p*(.55+.25*Math.sin(t*8)**2));$('sound').style.transform=`scale(${.9+.1*Math.sin(t*8)**2})`}
  const titleY=t<T.title?-1080:t<T.title_hold?-1080*(1-out(clamp((t-T.title)/.2))):t<T.bench?0:1080*ease(clamp((t-T.bench)/.55));
  $('title').style.transform=`translateY(${titleY}px)`;
  const cap=D.captions.find(c=>t>=c.start&&t<c.end);show($('caption'),!!cap&&t<T.title);if(cap)$('caption').textContent=cap.text;
}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({},{duration:D.timeline.duration},0);
window.__timelines=window.__timelines||{};window.__timelines.intro_v3=tl;
window.addEventListener('hf-seek',e=>render(e.detail.time));render(0);
</script></body></html>
