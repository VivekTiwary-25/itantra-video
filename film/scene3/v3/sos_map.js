/* Scene 3 SOS explanation. All motion derives from the scene time, so seeks and
   rebuilds with longer narration remain deterministic. This is our own map
   render; no camera frame or app recording is held. */
(function () {
  'use strict';
  const V = [330, 598], K = [350, 722];
  const DOTS = [[370, 540], [440, 590], [405, 690], [540, 550], [505, 740],
                [610, 620], [650, 775]];
  const cam = {tx:350,tz:660,D:640,pitch:57,yaw:-2};
  const clamp = x => Math.max(0, Math.min(1, x));
  function createSOSMap(root, timeline) {
    const sonar = window.Sonar(root.querySelector('#sos-map'), window.GEO);
    const waves = [root.querySelector('#wave-0'),root.querySelector('#wave-1')];
    const pinV = root.querySelector('#pin-v'), pinK = root.querySelector('#pin-k');
    const label = root.querySelector('#sos-label');
    const timer = root.querySelector('#sos-timer');
    const accept = root.querySelector('#sos-accept');
    const dotRoot = root.querySelector('#search-dots');
    const dots = DOTS.map(() => {
      const el = document.createElement('div');
      el.className = 'search-dot'; el.innerHTML = '<i></i>';
      dotRoot.appendChild(el); return el;
    });
    const beats = Object.fromEntries(timeline.sos_beats.map(x=>[x.name,x]));
    const start = timeline.segments.find(x=>x.name==='sos_sonar').start;
    const q = sonar.project(V[0],V[1],0), k = sonar.project(K[0],K[1],0);
    function place(el, p) {el.style.transform=`translate(${p.x.toFixed(1)}px,${p.y.toFixed(1)}px)`;}
    function render(t) {
      const st=t-start;
      sonar.render(st, {cam,pulses:[{x:V[0],y:V[1],t0:-30,speed:300}],floor:.85,ringFade:0});
      const v=sonar.project(V[0],V[1],0), h=sonar.project(K[0],K[1],0);
      place(pinV,v);place(pinK,h);
      const inN5b=t>=beats.N5b.start&&t<beats.N5b.end;
      const inN6=t>=beats.N6.start;
      const bdur=beats.N5b.end-beats.N5b.start;
      const bf=inN5b?clamp((t-beats.N5b.start)/bdur):inN6?1:0;
      pinK.style.opacity=inN6?'1':'0';
      DOTS.forEach((p,i)=>{
        const el=dots[i];place(el,sonar.project(p[0],p[1],0));
        el.classList.toggle('lit',i<3?bf>=.08:i<5?bf>=.34:i===5?bf>=.60:bf>=.84);
        el.style.opacity=inN5b||inN6?'1':'0';
      });
      waves.forEach((el,i)=>{
        const f=((st/2.4+i*.5)%1+1)%1;
        const source=i===1&&bf>=.60?(bf>=.84?DOTS[5]:DOTS[4]):V;
        const centre=source===V?v:sonar.project(source[0],source[1],0);
        const reach=bf<.34?220:bf<.60?330:250;
        el.setAttribute('cx',centre.x.toFixed(1));el.setAttribute('cy',centre.y.toFixed(1));
        el.setAttribute('r',(24+reach*f).toFixed(1));
        el.style.opacity=(Math.sin(Math.PI*f)*.72).toFixed(3);
      });
      label.style.left=(v.x+70).toFixed(1)+'px';
      label.style.top=(v.y-225).toFixed(1)+'px';
      if(t<beats.N5b.start){label.textContent='No saved contact needed';label.style.display='block';}
      else if(t<beats.N6.start){
        label.textContent=bf<.34?'3 strongest phones':bf<.60?'5 phones at 10 s':bf<.84?'2 hops at 25 s':'3 hops at 60 s';
        label.style.display='block';
      } else label.style.display='none';
      timer.style.left=(v.x+70).toFixed(1)+'px';timer.style.top=(v.y-140).toFixed(1)+'px';
      timer.style.display=inN5b?'block':'none';
      if(inN5b){
        const knots=[[0,0],[.34,10],[.60,25],[.84,60],[1,60]];
        let seconds=60;
        for(let i=1;i<knots.length;i++)if(bf<=knots[i][0]){
          const a=knots[i-1],b=knots[i];
          seconds=a[1]+(b[1]-a[1])*(bf-a[0])/(b[0]-a[0]);break;
        }
        timer.textContent=Math.round(seconds)+' s';
      }
      accept.style.left=(h.x+38).toFixed(1)+'px';accept.style.top=(h.y+16).toFixed(1)+'px';
      accept.style.display=inN6?'flex':'none';
      const af=inN6?clamp((t-beats.N6.start)/(beats.N6.end-beats.N6.start)):0;
      accept.children[0].classList.toggle('active',af>=.55);
    }
    return {render};
  }
  window.createSOSMap=createSOSMap;
})();
