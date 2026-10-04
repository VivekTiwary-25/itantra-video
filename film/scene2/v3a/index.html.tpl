<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080">
<script src="./gsap.min.js"></script>{{GLASS_LINK}}{{OVERHEAD_LINK}}
<style>
@font-face{font-family:SceneSans;src:local('Segoe UI Variable Display'),local('Segoe UI Variable'),local('Segoe UI');font-weight:100 900}*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#0a0d12;color:#f6f7fa;font-family:SceneSans,'Segoe UI',sans-serif}
#root{position:relative;width:1920px;height:1080px;overflow:hidden;background:#0a0d12}video,img{display:block}.layer{position:absolute;inset:0;display:none;overflow:hidden}.full{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}
/* Normal mode card: same glass design and type as scene 3's SOS card, centred, over the moving bench shot */
#modeCard{position:absolute;left:50%;top:50%;z-index:8;min-width:900px;padding:60px 84px 64px;text-align:center;transform:translate(-50%,-50%);opacity:0;
 background:linear-gradient(180deg,rgba(255,255,255,.055),rgba(255,255,255,0) 30%),rgba(14,18,26,.86)}
#modeCard h1{font-size:64px;font-weight:650;line-height:1.08;margin:0}#modeCard p{font-size:38px;margin:18px 0 0;color:var(--text,#f3f5f8)}
.camera{position:absolute;left:0;top:0;width:1232px;height:1080px;overflow:hidden;background:#0a0d12}.camera video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center}.camera:after{content:'';position:absolute;right:0;top:0;width:24px;height:100%;background:linear-gradient(90deg,transparent,rgba(4,7,11,.85))}
/* App recordings: shown whole and stable (spec 005 G2). The phone box has the recording's own aspect, so nothing is cropped or zoomed. */
.phone{position:absolute;top:40px;height:1000px;border-radius:32px;overflow:hidden;background:#0c131b;border:1px solid rgba(255,255,255,.14);box-shadow:0 22px 65px rgba(0,0,0,.65)}.phone video,.phone .screen-bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background-size:cover;background-position:center}
#vScene,#yScene{position:absolute;inset:0;display:none;background:#0a0d12}#vScene .phone,#yScene .phone{z-index:2}
#messageCard{position:absolute;z-index:6;width:470px;display:none;padding:22px 26px;font-size:30px;line-height:1.22;font-weight:500}
#walkLabel{position:absolute;left:48px;bottom:92px;z-index:3;font-size:34px}.label-pin{padding:13px 20px;border-radius:18px;background:rgba(10,22,31,.82);border:1px solid rgba(255,255,255,.23);font-weight:600;box-shadow:0 8px 26px #0007}
#walk{z-index:2}
#overhead{position:absolute;inset:0;z-index:1;display:none;background:radial-gradient(ellipse at 52% 55%,#1a2934 0%,#101b25 45%,#0a0d12 90%);overflow:hidden}
.caption{z-index:20;bottom:54px;max-width:1560px;display:none}.caption.side{left:350px;max-width:680px}.caption.splitSide{left:616px;max-width:1130px}
</style></head><body>
<div id="root" data-composition-id="scene2" data-start="0" data-duration="{{DURATION}}" data-width="1920" data-height="1080">
 <div class="layer" id="bench"><video id="benchVideo" class="clip full" src="assets/bench.mp4" data-start="0" data-duration="{{BENCH_DUR}}" data-media-start="{{S0}}" muted playsinline></video></div>
 <div id="modeCard" class="glass-card"><h1>Normal</h1><p>a private message to someone you trust</p></div>
 <div id="vScene"><div class="camera"><video id="vCam" class="clip" src="assets/bench.mp4" data-start="{{VCAM_START}}" data-duration="6.53" data-media-start="4.3" muted playsinline></video></div><div class="phone"><div class="screen-bg" style="background-image:url('assets/vachana_send_first.jpg')"></div><video id="vApp" class="clip" src="assets/vachana_send.mp4" data-start="{{VAPP_START}}" data-duration="13.133" data-media-start="0" muted playsinline></video><img id="sentState" class="screen-bg" src="assets/vachana_sent.jpg" alt=""></div></div>
 <div id="messageCard" class="glass-panel">Hey dude, I'm in the campus near the entry benches, where are you?</div>
 <div class="layer" id="walk"><video id="walkVideo" class="clip full" src="assets/walk.mp4" data-start="{{WALK_START}}" data-duration="{{WALK_DURATION}}" data-media-start="0" muted playsinline></video><div id="walkLabel" class="label-pin">Sped up {{SPEED}}×</div></div>
 <div id="overhead"><video id="overheadWalkVideo" class="clip" src="assets/walk.mp4" data-start="{{OVERHEAD_START}}" data-duration="0.88" data-media-start="{{OVERHEAD_WALK_START}}" muted playsinline></video><video id="overheadYashVideo" class="clip" src="assets/yash.mp4" data-start="{{OVERHEAD_YASH_START}}" data-duration="0.98" data-media-start="0" muted playsinline></video></div>
 <div class="layer" id="yashFull"><video id="yashFullVideo" class="clip full" src="assets/yash.mp4" data-start="{{YASH_START}}" data-duration="{{YASH_FULL_DUR}}" data-media-start="0.98" muted playsinline></video></div>
 <div id="yScene"><div class="camera"><video id="yCamA" class="clip" src="assets/yash.mp4" data-start="{{CAM_A_START}}" data-duration="{{CAM_A_DUR}}" data-media-start="{{CAM_A_MEDIA}}" muted playsinline></video><video id="yCamB" class="clip" src="assets/yash.mp4" data-start="{{CAM_B_START}}" data-duration="{{CAM_B_DUR}}" data-media-start="{{CAM_B_MEDIA}}" muted playsinline></video></div><div class="phone"><div class="screen-bg" style="background-image:url('assets/yash_app_first.jpg')"></div>{{YAPP_PIECES}}</div></div>
 <div id="caption" class="caption"></div>
</div>
<script>
const T={{TIMELINE}},S={{SLOTS}},C={{CAPTIONS}},by=Object.fromEntries(T.segments.map(x=>[x.name,x]));const el=id=>document.getElementById(id),clamp=x=>Math.max(0,Math.min(1,x)),ease=gsap.parseEase('power2.inOut');
const v=el('vScene'),y=el('yScene'),vp=v.querySelector('.phone'),yp=y.querySelector('.phone'),yPieces=[...document.querySelectorAll('.yapp')],YA=by.yash_app;vp.style.width=S.vachana_send.width+'px';yp.style.width=S.yash_app.width+'px';
const camA=YA.camera_a,camB=YA.camera_b;
let mounted=false;function mountOverhead(){if(mounted||!window.Overhead)return;window.Overhead.mount(el('overhead'),{walkVideo:el('overheadWalkVideo'),yashVideo:el('overheadYashVideo'),geo:window.OVERHEAD_GEO});mounted=true;}
function layout(scene,p,entry,show){const cam=scene.querySelector('.camera');cam.style.width=(1920-688*entry)+'px';cam.style.transform=`translateX(${-1232*(1-show)}px)`;cam.style.opacity=show;
 const width=parseFloat(p.style.width),right=1232+(688-width)/2,centre=(1920-width)/2,x=centre+(right-centre)*show;p.style.left=x+'px';p.style.transform=`translateX(${688*(1-entry)}px)`;p.style.opacity=entry;}
/* Yash camera visibility in the split: window A (continues the full shot), app takeover, window B (listening + reply) */
function yShow(dt){const a=1-ease(clamp((dt-1.0)/.5)),bIn=ease(clamp((dt-camB.dt[0])/.5)),bOut=1-ease(clamp((dt-(camB.dt[1]-.5))/.5));return dt<camA.dt[1]?a:(dt>=camB.dt[0]?bIn*bOut:0);}
function render(t){const b=el('bench'),w=el('walk'),oh=el('overhead'),yf=el('yashFull'),mc=el('messageCard'),mode=el('modeCard');for(const x of [b,w,oh,yf,v,y])x.style.display='none';mc.style.display='none';
 if(t<by.vachana_split_in.start)b.style.display='block';
 const mIn=ease(clamp((t-by.mode_card.start)/.3)),mOut=1-ease(clamp((t-(by.mode_card.end-.4))/.4));mode.style.opacity=(mIn*mOut).toFixed(3);mode.style.display=t<by.mode_card.end?'block':'none';mode.style.transform=`translate(-50%,calc(-50% + ${(12*(1-mIn)).toFixed(1)}px))`;
 if(t>=by.vachana_split_in.start&&t<by.walk.start){v.style.display='block';const dt=t-by.vachana_send.start,entry=ease(clamp((dt+.5)/.5)),show=Math.min(1,1-ease(clamp((dt-5.53)/.5)));layout(v,vp,entry,show);el('vCam').style.display=t<by.vachana_send.start+6.03?'block':'none';el('vApp').style.display=t>=by.vachana_send.start?'block':'none';el('sentState').style.display=t>=by.send_fly.start?'block':'none';v.querySelector('.screen-bg').style.backgroundImage=t<by.vachana_send.start?"url('assets/vachana_send_first.jpg')":"url('assets/vachana_send_last.jpg')";}
 if(t>=by.send_fly.start&&t<by.send_fly.end){const q=ease(clamp((t-by.send_fly.start)/.8));mc.style.display='block';mc.style.left=(740+1510*q)+'px';mc.style.top=(405-165*Math.sin(Math.PI*q))+'px';mc.style.transform=`rotate(${-8+14*q}deg) scale(${1-.34*q})`;}
 if(t>=by.walk.start&&t<by.walk.end){w.style.display='block';const dt=t-by.walk.start,enter=ease(clamp(dt/.4));w.style.transform=`translateX(${-1920*(1-enter)}px)`;w.style.opacity=1;}
 if(t>=by.overhead.start&&t<by.overhead.end){oh.style.display='block';mountOverhead();if(mounted)window.Overhead.render(t-by.overhead.start);}
 if(t>=by.yash_before_notification.start&&t<by.yash_before_notification.end)yf.style.display='block';
 let ySplit=0;if(t>=YA.start&&t<YA.end){y.style.display='block';const dt=t-YA.start;ySplit=yShow(dt);layout(y,yp,ease(clamp(dt/.5)),ySplit);el('yCamA').style.display=dt<camA.dt[1]?'block':'none';el('yCamB').style.display=dt>=camB.dt[0]?'block':'none';
  const k=YA.edl.findLastIndex(p=>dt>=p.dt-1e-6);yPieces.forEach((e,i)=>e.style.display=i===Math.max(0,k)?'block':'none');}
 const cap=C.find(c=>t>=c.start&&t<c.end),ce=el('caption');ce.style.display=cap?'block':'none';ce.textContent=cap?.text||'';
 ce.className='caption'+(!cap?'':(t>=YA.start&&t<YA.end)?(ySplit>.5?' splitSide':' side'):(t>=by.vachana_split_in.start&&t<by.walk.start)?' splitSide':'');}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({}, {duration:T.duration},0);window.addEventListener('hf-seek',e=>render(e.detail.time));window.__timelines=window.__timelines||{};window.__timelines.scene2=tl;render(0);
</script></body></html>
