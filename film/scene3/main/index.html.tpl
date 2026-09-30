<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080"><script src="./gsap.min.js"></script>
<style>
@font-face{font-family:Segoe;src:local('Segoe UI Variable')}*{box-sizing:border-box}
html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#05070a;color:#eef1f4;font-family:Segoe,'Segoe UI',sans-serif}
#root{position:relative;width:1920px;height:1080px;overflow:hidden}.scene{position:absolute;inset:0;display:none;overflow:hidden}
.full{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover}
.sides{position:absolute;inset:-60px;background-position:center;background-size:cover;filter:blur(40px) brightness(.55);transform:scale(1.04)}
.sides video{width:100%;height:100%;object-fit:cover}.screen{position:absolute;top:0;height:1080px;border-radius:28px;overflow:hidden;background:#0a0e14;box-shadow:0 12px 58px #000c,0 0 0 1px #ffffff22}
.screen video{width:100%;height:100%;object-fit:contain;background:#05070a}.placeholder{width:100%;height:100%;display:grid;place-items:center;background:#0b1018;color:#8a939e;font-size:28px;letter-spacing:.04em;text-align:center}
.freeze{position:absolute;inset:0;background-position:center;background-size:cover}.sonar-card{position:absolute;inset:0;display:grid;place-items:center;background:radial-gradient(circle at center,#291116,#070a0e 58%);color:#d9767e;font-size:32px;letter-spacing:.08em}
</style></head><body><div id="root" data-composition-id="scene3" data-start="0" data-duration="{{DURATION}}" data-width="1920" data-height="1080">{{LAYERS}}</div>
<script>
const T={{TIMELINE}},rows=T.segments;
function render(t){document.querySelectorAll('.scene').forEach(e=>e.style.display='none');const r=rows.find(x=>t>=x.start&&t<x.end);if(r){const e=document.getElementById('seg_'+r.name);if(e)e.style.display='block'}}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({}, {duration:T.duration},0);
window.addEventListener('hf-seek',e=>render(e.detail.time));window.__timelines=window.__timelines||{};window.__timelines.scene3=tl;render(0);
</script></body></html>
