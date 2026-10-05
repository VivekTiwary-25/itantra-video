<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080">
<link rel="stylesheet" href="assets/glass/glass.css"><script src="./gsap.min.js"></script><script src="assets/glass/glass.js"></script>
<style>
*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#0a0d12;color:var(--text);font-family:SceneSans,"Segoe UI",sans-serif}
#root,#push,#sonar,#mapFX,#card{position:absolute;inset:0;overflow:hidden}#root{background:#0a0d12}
#push{background:#0a0d12}#yStatusMask{position:absolute;z-index:5;left:0;right:0;top:0;height:4.8%;background:#07111c;pointer-events:none}#phone{position:absolute;left:735px;top:40px;width:450px;height:1000px;transform-origin:center;border-radius:32px;overflow:hidden;background:#0c131b;border:1px solid #ffffff24;box-shadow:0 22px 65px #000a}
#phone video,#phone img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}#phone video{z-index:2}#phoneDark{position:absolute;inset:0;z-index:3;background:#050910;opacity:0}
#sonar{display:none}#sonar>video,#sonar>img{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}#sonarOpen{z-index:0}#sonar>video{z-index:1}#sonarLoop{z-index:2;opacity:0}#sonarEnd{z-index:3;display:none}
#mapFX{z-index:4;display:none;pointer-events:none}#mapFX svg{position:absolute;inset:0;width:1920px;height:1080px;overflow:visible}
#mapFX .blue{stroke:var(--blue);fill:none}#mapFX .dots{stroke-dasharray:5 14;stroke-width:3;opacity:.8}#pulse{stroke-width:3;filter:drop-shadow(0 0 12px var(--blue))}
#wave{stroke-width:5;stroke-linecap:round;filter:drop-shadow(0 0 10px var(--blue))}
.pill{position:absolute;display:none;border-radius:22px;padding:19px 28px;font-size:46px;font-weight:590;line-height:1.14;max-width:1050px;white-space:nowrap}
.pill small{display:block;color:var(--text-dim);font-size:32px;margin-top:7px}.pill .blue-text{color:var(--blue)}.pill .gold-text{color:var(--gold)}
#msg{left:760px;top:345px;width:900px;white-space:normal;font-size:44px;line-height:1.25}
#label{left:750px;top:175px}
#size{left:935px;top:475px;font-size:44px}
#capsule{position:absolute;left:800px;top:410px;width:86px;height:48px;border-radius:16px;background:var(--blue);box-shadow:0 0 22px #4da3ff99;display:none}
#lock{position:absolute;left:817px;top:395px;width:52px;height:50px;display:none}
#lock:before{content:"";position:absolute;left:13px;top:0;width:26px;height:26px;border:5px solid #f3f5f8;border-bottom:0;border-radius:17px 17px 0 0}
#lock:after{content:"";position:absolute;left:6px;top:21px;width:40px;height:30px;border-radius:7px;background:#f3f5f8}
.relayLock{position:absolute;display:none;width:30px;height:27px;border:3px solid var(--blue);border-radius:6px;box-shadow:0 0 14px #4da3ff88}
.relayLock:before{content:"";position:absolute;left:6px;top:-15px;width:12px;height:14px;border:3px solid var(--blue);border-bottom:0;border-radius:12px 12px 0 0}
#lock1{left:520px;top:545px}#lock2{left:630px;top:675px}#lock3{left:902px;top:708px}
#timer{position:absolute;left:610px;top:668px;width:75px;height:75px;border-radius:50%;display:none;background:conic-gradient(var(--blue) 0deg,transparent 0deg);mask:radial-gradient(transparent 53%,black 56%);-webkit-mask:radial-gradient(transparent 53%,black 56%)}
#walker{position:absolute;left:642px;top:713px;width:18px;height:18px;border-radius:50%;background:var(--blue);box-shadow:0 0 20px var(--blue);display:none}
#hop{left:1000px;top:715px;font-size:52px;min-width:90px;text-align:center}
#relayName{position:absolute;z-index:7;display:none;white-space:nowrap;font-size:44px;padding:12px 24px}
#relayMask{position:absolute;z-index:6;display:none;pointer-events:none;background:linear-gradient(180deg,rgba(255,255,255,.06),transparent 30%),rgba(14,18,26,.72);backdrop-filter:blur(36px) saturate(1.4);-webkit-backdrop-filter:blur(36px) saturate(1.4);border:1px solid rgba(255,255,255,.09);border-radius:18px;box-shadow:0 0 22px 16px rgba(14,18,26,.22)}
#relayTxt{position:absolute;top:50%;transform:translateY(-50%);left:30px;right:30px;font-size:32px;line-height:1.3;color:var(--text);white-space:nowrap}#relayTxt.right{text-align:right}#relayTxt .l1{font-weight:600;letter-spacing:.005em}#relayTxt .l2{font-weight:450;color:#DCE4EC}
#frost{position:absolute;inset:0;z-index:8;background:#0e121a99;backdrop-filter:blur(0);opacity:0;pointer-events:none}
#card{z-index:9;display:grid;place-items:center;text-align:center;opacity:0;pointer-events:none}
#card .glass-card.full{display:flex;flex-direction:column;align-items:center;justify-content:center}
#captions{position:absolute;inset:0;z-index:12;pointer-events:none}#captions .caption{display:none}
</style></head><body>
<div id="root" data-composition-id="scene2_v3b" data-start="0" data-duration="{{DURATION}}" data-width="1920" data-height="1080">
 <div id="push"><div id="phone"><img src="assets/yash_slot.jpg" alt=""><video id="yashSlot" class="clip" src="assets/yash_app.mp4" data-start="0" data-duration="1.4" data-media-start="{{SLOT_TIME}}" muted playsinline></video><div id="yStatusMask"></div><div id="phoneDark"></div></div></div>
 <div id="sonar"><img id="sonarOpen" src="assets/sonar_open.jpg" alt=""><img id="sonarLoop" src="assets/sonar_loop.jpg" alt=""><img id="sonarEnd" src="assets/sonar_end.jpg" alt="">{{CLIPS}}
  <div id="mapFX">
   <svg viewBox="0 0 1920 1080"><circle id="pulse" class="blue" cx="689" cy="381" r="0"></circle><path id="wave" class="blue" d=""></path><path id="route" class="blue dots" d="M689 381 Q525 410 534 586 Q600 650 644 715 Q790 670 916 749 Q1070 760 1211 822"></path><path id="leader" class="blue" stroke-width="2" d=""></path></svg>
   <div id="label" class="label-pin pill"></div><div id="msg" class="label-pin pill">Hey dude, I'm in the campus near the entry benches, where are you?</div>
   <div id="capsule"></div><div id="lock"></div><div id="size" class="label-pin pill">~1.2 KB</div>
   <div class="relayLock" id="lock1"></div><div class="relayLock" id="lock2"></div><div class="relayLock" id="lock3"></div>
   <div id="timer"></div><div id="walker"></div><div id="hop" class="label-pin pill"></div>
  </div>
  <div id="relayMask"><div id="relayTxt"><div class="l1"></div><div class="l2"></div></div></div><div id="relayName" class="label-pin"></div><div id="frost"></div>
 </div>
 <div id="card"><div class="glass-card full"><h1 class="card-title"><span style="color:var(--red)">SOS</span></h1><p>help from anyone nearby, no saved contact needed</p></div></div>
 <div id="captions"></div>{{SOUNDS}}
</div>
<script>
const T={{TIMELINE}},C={{CAPTIONS}},by=Object.fromEntries(T.segments.map(s=>[s.name,s]));
const id=x=>document.getElementById(x),clamp=x=>Math.max(0,Math.min(1,x)),smooth=x=>{x=clamp(x);return x*x*(3-2*x)};
const capEls=C.map(c=>{const e=document.createElement('div');e.className='caption';e.textContent=c.text;id('captions').appendChild(e);return e});
const pins={relay_1:[534,586],relay_2:[644,715],relay_3:[916,749]};
const people={relay_1:[850,195],relay_2:[590,190],relay_3:[400,190]};
// v2 (Vivek, 5 Oct): the glass box carries the relay plates' own caption (film/scene2/sonar/cues.py)
const relayText={relay_1:['Her phone passes the message on.','She just keeps walking.',0],relay_2:['His phone relays it in the background.','His call carries on.',0],relay_3:['Her phone hands it forward.','She keeps going.',1]};
const relayNames={relay_1:'Trisha',relay_2:'Utkarsh',relay_3:'Vaishnavi'};
const maskBoxes={relay_1:[1240,378,660,124],relay_2:[115,288,640,130],relay_3:[0,580,505,130]};
function show(el,yes){el.style.display=yes?'block':'none'}
function drawBeat(t){
 const loop=by.sonar_loop, active=t>=Math.min(loop.start,by.sonar_a.start+7)&&t<loop.end,fx=id('mapFX');show(fx,active);
 if(!active)return;
 const phase=(((t-loop.start)%2.8+2.8)%2.8)/2.8;
 id('pulse').setAttribute('r',(35+300*phase).toFixed(1));
 id('pulse').style.opacity=(.42*Math.sin(Math.PI*phase)).toFixed(3);
 const beat=T.beats.find(b=>t>=b.start&&t<b.end),name=beat?.id||'',u=beat?clamp((t-beat.start)/(beat.end-beat.start)):0;
 const label=id('label'),msg=id('msg'),cap=id('capsule'),lock=id('lock'),size=id('size'),route=id('route'),timer=id('timer'),walker=id('walker'),hop=id('hop');
 for(const e of [label,msg,cap,lock,size,route,timer,walker,hop,id('lock1'),id('lock2'),id('lock3')])show(e,false);
 id('wave').setAttribute('d','');id('leader').setAttribute('d','');
 if(!beat)return;
 show(label,true);label.style.opacity=(smooth(u/.15)*smooth((1-u)/.08)).toFixed(3);
 if(name==='N2a'){
   msg.style.transform='';
   label.textContent='Speech to text on the phone, without internet';label.style.left='750px';label.style.top='170px';
   id('leader').setAttribute('d','M689 381 L752 272');
   if(u<.5){
     let d='M699 377';for(let i=0;i<20;i++){const x=702+i*14,amp=28*Math.sin(i*2.4+t*14)*(1-smooth((u-.28)/.22));d+=` L${x} ${(377+amp).toFixed(1)}`}id('wave').setAttribute('d',d);
   }
   show(msg,u>.35);msg.style.opacity=smooth((u-.35)/.2).toFixed(3);
 }else if(name==='N2b'){
   label.innerHTML='Sealed for Yash only<small>Google Tink</small>';label.style.left='905px';label.style.top='235px';
   id('leader').setAttribute('d','M689 381 L800 435');
   show(msg,u<.34);msg.style.transformOrigin='0 50%';msg.style.transform=`translate(${Math.round(40*smooth(u/.34))}px,${Math.round(65*smooth(u/.34))}px) scale(${(1-.91*smooth(u/.34)).toFixed(3)})`;
   show(cap,true);show(lock,u>.28);show(size,u>.45);
   cap.style.transform=`scale(${(.65+.35*smooth(u/.45)).toFixed(3)})`;
   size.style.opacity=smooth((u-.45)/.28).toFixed(3);
 }else if(name==='N2c'){
   label.innerHTML='<span class="gold-text">Bluetooth LE</span>, encrypted at every hop';label.style.left='815px';label.style.top='185px';
   id('leader').setAttribute('d','M689 381 L780 288');
   show(route,true);route.style.opacity=smooth(u/.2).toFixed(3);
   ['lock1','lock2','lock3'].forEach((x,i)=>show(id(x),u>.2+i*.18));
 }else if(name==='N2d'){
   label.textContent='Waits up to 24 h and moves as people walk';label.style.left='795px';label.style.top='540px';
   id('leader').setAttribute('d','M644 715 L790 630');
   show(cap,true);cap.style.left='650px';cap.style.top='695px';show(timer,true);show(walker,true);
   timer.style.background=`conic-gradient(var(--blue) ${Math.round(360*u)}deg,transparent 0deg)`;
   walker.style.transform=`translate(${Math.round(140*smooth((u-.48)/.5))}px,${Math.round(-26*smooth((u-.48)/.5))}px)`;
 }else if(name==='N2e'){
   label.textContent='6 hops, tested on real phones';label.style.left='870px';label.style.top='535px';
   id('leader').setAttribute('d','M916 749 L946 635');
   show(hop,true);hop.textContent=String(Math.min(6,Math.floor(u*6)+1));hop.style.opacity=smooth(u/.1).toFixed(3);
 }
}
function render(t){
 const opening=smooth((t-.45)/.95),sonar=id('sonar');show(id('push'),t<1.4);
 id('phone').style.transform=`scale(${(1+4.45*opening).toFixed(4)})`;
 id('phoneDark').style.opacity=smooth((t-.1)/.35).toFixed(3);
 show(sonar,t>=.84);sonar.style.opacity=smooth((t-.82)/.4).toFixed(3);
 const loop=by.sonar_loop;
 id('sonarOpen').style.display=t<by.sonar_a.start?'block':'none';
 for(const n of ['sonar_a','relay_1','relay_2','relay_3','sonar_b']){const s=by[n];show(id(n),t>=s.start&&t<s.end||n==='sonar_b'&&t>=T.duration)}
 id('sonar_a').style.opacity=smooth((t-by.sonar_a.start)/.35).toFixed(3);
 const loopFade=Math.min(loop.start-.5,by.sonar_a.start+6.5);
 show(id('sonarLoop'),t>=loopFade&&t<loop.end);id('sonarLoop').style.opacity=smooth((t-loopFade)/.5).toFixed(3);
 show(id('sonarEnd'),t>=by.sonar_b.start+5.2&&t<by.sonar_b.end);
 drawBeat(t);
 const rn=id('relayName'),seg=['relay_1','relay_2','relay_3'].find(n=>t>=by[n].start&&t<by[n].end);show(rn,!!seg);
 if(seg){const u=t-by[seg].start,p=pins[seg],q=people[seg],f=smooth((u-.45)/.7);rn.textContent=relayNames[seg];rn.style.left=(p[0]+(q[0]-p[0])*f)+'px';rn.style.top=(p[1]-65+(q[1]-(p[1]-65))*f)+'px';rn.style.opacity=(smooth(u/.25)*smooth((6-u)/.35)).toFixed(3)}
 const mask=id('relayMask'),maskOn=seg&&t-by[seg].start>=2.85&&t-by[seg].start<5.55;show(mask,maskOn);
 if(maskOn){const [x,y,w,h]=maskBoxes[seg],u=t-by[seg].start;Object.assign(mask.style,{left:x+'px',top:y+'px',width:w+'px',height:h+'px',opacity:(smooth((u-2.85)/.25)*smooth((5.55-u)/.25)).toFixed(3)});const rt=id('relayTxt'),[t1,t2,r]=relayText[seg];rt.querySelector('.l1').textContent=t1;rt.querySelector('.l2').textContent=t2;rt.className=r?'right':''}
 const out=smooth((t-by.to_sos.start)/1.5);
 id('frost').style.opacity=out.toFixed(3);id('frost').style.backdropFilter=`blur(${Math.round(32*out)}px) saturate(1.4)`;
 id('card').style.opacity=smooth((t-by.to_sos.start)/Math.min(.5,by.to_sos.end-by.to_sos.start)).toFixed(3);
 C.forEach((c,i)=>{const e=capEls[i],on=t>=c.start&&t<c.end;show(e,on);if(on)e.style.opacity=(smooth((t-c.start)/.1)*smooth((c.end-t)/.1)).toFixed(3)});
}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({},{duration:T.duration},0);
window.addEventListener('hf-seek',e=>render(e.detail.time));window.__timelines=window.__timelines||{};window.__timelines.scene2_v3b=tl;render(0);
</script></body></html>
