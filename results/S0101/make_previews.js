/* Extract S0101 review frames and measure adjacent-frame motion. */
const fs = require('fs'), path = require('path'), cp = require('child_process');
const repo = path.resolve(__dirname, '../..'), preview = path.join(__dirname, 'preview');
const render = path.join(repo, 'local/renders/scene2/v3a/scene2_picture_540.mp4');
const assets = path.join(repo, 'film/scene2/v3a/assets');
fs.mkdirSync(preview, {recursive:true});
function ff(args) {const p=cp.spawnSync('ffmpeg',['-v','error','-y',...args],{maxBuffer:8*1024*1024}); if(p.status!==0)throw Error(p.stderr.toString()); return p.stdout;}
function gray(file,n){const x=ff(['-i',file,'-vf',`select=eq(n\\,${n}),scale=480:270`,'-frames:v','1','-pix_fmt','gray','-f','rawvideo','-']);if(x.length!==480*270)throw Error(`Bad gray frame ${n}: ${x.length}`);return x;}
function mean(a,b){let total=0;for(let i=0;i<a.length;i++)total+=Math.abs(a[i]-b[i]);return +(total/a.length).toFixed(2);}
const frames=[['overhead_0p2',723],['overhead_0p6',735],['overhead_4p3',846],['overhead_4p97',866],['yash_full_first',867],['s2a_last',1298]];
const srcIndex={723:160,735:172,846:8,866:28}, evidence=[];
for(const [name,n] of frames){const dst=path.join(preview,name+'.jpg');ff(['-i',render,'-vf',`select=eq(n\\,${n}),scale=960:540`,'-frames:v','1','-q:v','3',dst]);if(!fs.existsSync(dst))throw Error(`Missing ${name}`);if(name.startsWith('overhead')){const src=path.join(assets,n<800?'walk.mp4':'yash.mp4'),s=srcIndex[n];evidence.push({overhead_time:+((n/30)-23.9).toFixed(3),rendered_mean_abs_gray_255:mean(gray(render,n),gray(render,n+1)),source_mean_abs_gray_255:mean(gray(src,s),gray(src,s+1))});}}
const inputs=frames.flatMap(([name])=>['-i',path.join(preview,name+'.jpg')]);
const filters=frames.map((_,i)=>`[${i}:v]scale=480:270[v${i}]`).join(';')+';'+frames.map((_,i)=>`[v${i}]`).join('')+`vstack=inputs=${frames.length}[out]`;
ff([...inputs,'-filter_complex',filters,'-map','[out]','-frames:v','1','-q:v','3',path.join(preview,'phone_sheet.jpg')]);
fs.writeFileSync(path.join(__dirname,'motion_evidence.json'),JSON.stringify(evidence,null,2)+'\n');
console.log(JSON.stringify(evidence,null,2));
