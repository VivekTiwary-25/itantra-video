// Small local feature matcher for frame-search evidence. Reads footage via machine.local.json.
// FAST-like corners, gradient-histogram descriptors, mutual ratio test, similarity RANSAC.
const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const config = JSON.parse(fs.readFileSync('machine.local.json', 'utf8'));
const W=480,H=270, SZ=W*H;
const video = n => path.join(config.footage_root, 'Video', n);
function frames(file, start, duration, fps) {
  const p=cp.spawnSync('ffmpeg',['-v','error','-ss',String(start),'-t',String(duration),'-i',file,
    '-vf',`fps=${fps},scale=${W}:${H},format=gray`,'-f','rawvideo','-'],{maxBuffer:SZ*250});
  if(p.status!==0) throw new Error(p.stderr.toString());
  const out=[]; for(let i=0;i+SZ<=p.stdout.length;i+=SZ) out.push(p.stdout.subarray(i,i+SZ));
  return out;
}
const ring=[[-3,0],[-3,1],[-2,2],[-1,3],[0,3],[1,3],[2,2],[3,1],[3,0],[3,-1],[2,-2],[1,-3],[0,-3],[-1,-3],[-2,-2],[-3,-1]];
function features(a, mask) {
  const pts=[];
  for(let y=12;y<H-12;y+=2) for(let x=12;x<W-12;x+=2) {
    if(mask && mask(x,y)) continue;
    const c=a[y*W+x], dif=ring.map(([dy,dx])=>a[(y+dy)*W+x+dx]-c);
    let best=0;
    for(let q=0;q<16;q++) {let b=0,d=0; for(let k=0;k<9;k++){const v=dif[(q+k)%16];if(v>18)b++;if(v< -18)d++;}best=Math.max(best,b,d);}
    if(best<9) continue;
    let score=0; for(const v of dif) score+=Math.abs(v);
    pts.push({x,y,score});
  }
  pts.sort((a,b)=>b.score-a.score);
  const kept=[], perCell=new Map();
  for(const p of pts){const key=`${p.x>>5}:${p.y>>5}`;const n=perCell.get(key)||0;if(n>=8)continue;
    if(kept.some(q=>Math.abs(q.x-p.x)<5&&Math.abs(q.y-p.y)<5))continue;
    kept.push(p);perCell.set(key,n+1);if(kept.length>=350)break;}
  for(const p of kept){const hist=new Float32Array(32);
    for(let dy=-8;dy<8;dy+=2)for(let dx=-8;dx<8;dx+=2){const xx=p.x+dx,yy=p.y+dy,idx=yy*W+xx;
      const gx=a[idx+1]-a[idx-1],gy=a[idx+W]-a[idx-W], mag=Math.hypot(gx,gy);
      const cell=(dy>=0?2:0)+(dx>=0?1:0),bin=(Math.floor((Math.atan2(gy,gx)+Math.PI)*4/Math.PI))%8;
      hist[cell*8+bin]+=mag;}
    let norm=Math.hypot(...hist)||1;for(let i=0;i<32;i++)hist[i]/=norm;p.d=hist;}
  return kept;
}
function dist(a,b){let s=0;for(let k=0;k<32;k++){const d=a[k]-b[k];s+=d*d;}return s;}
function matches(ref,cand){const f=[];for(const p of ref){let b1=1e9,b2=1e9,j=-1;for(let i=0;i<cand.length;i++){
  const v=dist(p.d,cand[i].d);if(v<b1){b2=b1;b1=v;j=i;}else if(v<b2)b2=v;}
  if(j>=0&&b1<0.72*b2&&b1<0.58)f.push({p,q:cand[j],d:b1});}
  f.sort((a,b)=>a.d-b.d);return f;}
function consensus(m){if(m.length<2)return 0;let best=0;
  for(let i=0;i<Math.min(m.length,60);i++)for(let j=i+1;j<Math.min(m.length,60);j++){
    const a=m[i],b=m[j],dx=b.p.x-a.p.x,dy=b.p.y-a.p.y,ux=b.q.x-a.q.x,uy=b.q.y-a.q.y;
    const den=dx*dx+dy*dy;if(den<100)continue;
    const c=(dx*ux+dy*uy)/den,s=(dx*uy-dy*ux)/den,scale=Math.hypot(c,s);if(scale<0.2||scale>3)continue;
    const tx=a.q.x-c*a.p.x+s*a.p.y,ty=a.q.y-s*a.p.x-c*a.p.y;
    let n=0;for(const z of m){const ex=c*z.p.x-s*z.p.y+tx-z.q.x,ey=s*z.p.x+c*z.p.y+ty-z.q.y;if(ex*ex+ey*ey<144)n++;}
    if(n>best)best=n;}
  return best;}
function scan(name, refName, refTime, start, duration, mask){
  const r=features(frames(video(refName),refTime,1,1)[0],mask), fs2=frames(video('normalpart2.mp4'),start,duration,2);
  const rows=fs2.map((f,i)=>{const q=features(f),m=matches(r,q);return {time:start+i*0.5,features:q.length,matches:m.length,inliers:consensus(m)};});
  rows.sort((a,b)=>b.inliers-a.inliers||b.matches-a.matches);
  console.log(name, 'reference features',r.length,'top candidates',JSON.stringify(rows.slice(0,20)));
}
scan('start','normalpart1.mp4',1,6,32,(x,y)=>x>180&&x<340&&y>35);
scan('end','normalpart6.mp4',1,145,57,(x,y)=>x>170&&x<330&&y>40);
