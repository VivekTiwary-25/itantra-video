// Deterministic renderer: every visible state is a pure function of segment time.
function initScene4(){
const T=window.SCENE4, CAP=window.SCENE4_CAPTIONS;
document.getElementById('root').dataset.duration=String(T.duration);
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const ease=x=>{x=clamp(x);return x*x*(3-2*x)};
const lerp=(a,b,k)=>a+(b-a)*k;
const vis=(t,a,b,r=.3)=>ease((t-a)/r)*(1-ease((t-b+r)/r));
const renderer=new THREE.WebGLRenderer({canvas:document.getElementById('phoneCanvas'),alpha:true,antialias:true,preserveDrawingBuffer:true});
renderer.setSize(1920,1080,false);renderer.setPixelRatio(1);renderer.outputColorSpace=THREE.SRGBColorSpace;
const scene=new THREE.Scene(),camera=new THREE.OrthographicCamera(-8.89,8.89,5,-5,.1,100);
camera.position.set(0,0,20);camera.lookAt(0,0,0);
scene.add(new THREE.AmbientLight(0xb7c9db,1.0));
function light(c,i,x,y,z){const l=new THREE.PointLight(c,i,40);l.position.set(x,y,z);scene.add(l)}
light(0xc6e8ff,135,-5,7,9);light(0x6d9ec5,85,8,2,5);light(0xffffff,32,0,-6,8);
function rounded(w,h,r){const s=new THREE.Shape(),x=-w/2,y=-h/2;s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);return s}
const texture=new THREE.TextureLoader().load('./assets/home.png');texture.colorSpace=THREE.SRGBColorSpace;
function makePhone(){
  const group=new THREE.Group();scene.add(group);
  const frame=new THREE.Mesh(new THREE.ExtrudeGeometry(rounded(2.63,5.82,.28),{depth:.19,bevelEnabled:true,bevelSegments:3,steps:1,bevelSize:.045,bevelThickness:.04,curveSegments:12}),new THREE.MeshStandardMaterial({color:0x647684,metalness:.85,roughness:.24}));frame.position.z=-.16;group.add(frame);
  const bezel=new THREE.Mesh(new THREE.ShapeGeometry(rounded(2.54,5.72,.25)),new THREE.MeshStandardMaterial({color:0x05080c,metalness:.28,roughness:.24}));bezel.position.z=.10;group.add(bezel);
  const display=new THREE.Mesh(new THREE.PlaneGeometry(2.44,5.52),new THREE.MeshBasicMaterial({map:texture,side:THREE.DoubleSide}));display.position.z=.113;group.add(display);
  const rim=new THREE.Mesh(new THREE.ShapeGeometry(rounded(2.55,5.73,.25)),new THREE.MeshBasicMaterial({color:0xc2d9eb,transparent:true,opacity:.045,side:THREE.DoubleSide}));rim.position.z=.119;group.add(rim);
  const punch=new THREE.Mesh(new THREE.CircleGeometry(.035,20),new THREE.MeshBasicMaterial({color:0x030609}));punch.position.set(0,2.76,.121);group.add(punch);
  return {group,display};
}
const A=makePhone(),B=makePhone();
const E=id=>document.getElementById(id);
if(window.SCENE4_BLENDER){E('phoneCanvas').style.display='none';E('teardown').style.display='none';E('processorGlow').style.left='755px';E('processorGlow').style.top='265px'}
E('bt').appendChild(Glass.icon('bluetooth'));
const numbers=[
  {main:'One speech model for 9 Indian languages'},
  {main:'697 MB',minor:'~5.9 GB',bar:true},
  {main:'English: 98 MB'},
  {main:'10 s of speech to text in ~1.3 s'},
  {main:'Ordinary mid-range phone, ~0.9 GB of memory in use'}
];
function render(t){
  t=clamp(t,0,T.duration);const b=T.beats,n=T.narration;
  const bridge=ease(t/1.36),lift=ease((t-.72)/.65),open=ease((t-b.open[0])/(b.open[1]-b.open[0]));
  const shut=ease((t-b.close[0])/(b.close[1]-b.close[0]));
  const layers=open*(1-shut),pair=ease((t-b.pair[0])/.75),end=ease((t-b.end[0])/.5);
  if(window.SCENE4_BLENDER)E('blenderPhone').style.transform=`scale(${1+.045*ease((t-b.open[0])/(b.close[0]-b.open[0]))*(1-shut)})`;
  E('lab').style.opacity=String(1-ease((t-.85)/.5));
  E('lab').style.transform=`scale(${lerp(1,2.12,bridge)})`;
  E('labShade').style.opacity=String(.8*ease((t-.35)/.95));
  E('studio').style.opacity=String(ease((t-.85)/.55));
  if(window.SCENE4_BLENDER)E('blenderPhone').style.opacity=String(ease((t-.7)/.22));
  E('turntableA').style.opacity=String(ease((t-1.1)/.45)*(1-.34*layers));
  E('turntableA').style.left=(lerp(625,375,pair))+'px';
  E('turntableB').style.opacity=String(pair*(1-end*.25));
  const g=A.group;
  g.position.set(lerp(-2.95,-.35,lift)-2.5*pair,lerp(.80,-.15,lift),0);
  g.scale.setScalar(lerp(.20,1.03,lift)*(1-.03*pair));
  g.rotation.set(-.10,lerp(-.18,.42,lift)+.13*Math.sin(Math.max(0,t-1.4)*.38),lerp(-1.13,-.12,lift));
  g.visible=layers<.98;A.display.material.opacity=1-layers;A.display.material.transparent=true;
  // The yaw remains inside +/- 0.55 rad: the generic back stays turned away.
  B.group.visible=pair>.01;B.group.position.set(lerp(9.1,4.3,pair),-.28,0);B.group.scale.setScalar(.85*pair);
  B.group.rotation.set(-.06,-.27+.08*Math.sin(t*.45),.08);
  E('teardown').style.opacity=String(layers);
  if(!window.SCENE4_BLENDER){
    E('layerBack').style.transform=`translate(${260*layers}px,${24*layers}px) rotate(-3deg)`;
    E('layerMid').style.transform=`translate(${10*layers}px,0px) rotate(-3deg)`;
    E('layerScreen').style.transform=`translate(${-240*layers}px,${-20*layers}px) rotate(-3deg)`;
  }
  E('processorGlow').style.opacity=String(layers*(.48+.18*Math.sin(t*2.4)));
  const numStart=b.numbers[0],numEnd=b.numbers[1],per=(numEnd-numStart)/numbers.length;
  const idx=Math.min(numbers.length-1,Math.floor((t-numStart)/per));
  const inNumbers=t>=numStart&&t<numEnd;
  const item=numbers[Math.max(0,idx)],phase=t-(numStart+Math.max(0,idx)*per);
  E('numberPanel').style.opacity=String(inNumbers?vis(phase,0,per,.23):0);
  E('numberMain').textContent=item.main;E('numberMinor').textContent=item.minor||'';
  E('bar').style.display=item.bar?'block':'none';E('barFill').style.width=(item.bar?lerp(100,11.8,ease(phase/per)):100)+'%';
  const p=clamp((t-n.N7c.start)/(n.N7c.duration));
  E('packetTrack').style.opacity=String(vis(t,n.N7c.start,n.N7c.end,.3));
  E('packet').style.opacity=String(vis(p,.12,.84,.15));
  E('packet').style.left=(lerp(680,1240,ease((p-.13)/.65)))+'px';
  E('packet').style.top=(457-52*Math.sin(Math.PI*clamp((p-.13)/.65)))+'px';
  E('bt').style.opacity=String(vis(p,.27,.78,.14));
  E('packetText').style.opacity=String(vis(t,n.N7c.start+.15,n.N7c.end,.3));
  E('waves').style.opacity=String(vis(p,.68,1,.18));
  E('waves').style.transform=`scale(${1+.05*Math.sin(t*11)})`;
  E('endline').style.opacity=String(vis(t,n.N7d.start,T.duration,.35));
  const cap=CAP.find(c=>t>=c.start&&t<c.end),ce=E('caption');
  ce.style.display=cap?'block':'none';if(cap)ce.textContent=cap.text;
  if(!window.SCENE4_BLENDER)renderer.render(scene,camera);
}
const tl=gsap.timeline({paused:true,onUpdate:()=>render(tl.time())});tl.to({}, {duration:T.duration},0);
window.__timelines=window.__timelines||{};window.__timelines.scene4=tl;
window.addEventListener('hf-seek',e=>render(e.detail.time));render(0);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initScene4);else initScene4();
