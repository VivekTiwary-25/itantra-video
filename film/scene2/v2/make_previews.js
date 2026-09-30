/* Small review stills. Uses staged v2 plates; writes only results/T0032/preview. */
const fs=require('fs'),path=require('path'),cp=require('child_process');
const HERE=__dirname,REPO=path.resolve(HERE,'../../..'),A=path.join(HERE,'assets'),OUT=path.join(REPO,'results/T0032/preview');
fs.mkdirSync(OUT,{recursive:true});
function run(args){const p=cp.spawnSync('ffmpeg',args,{encoding:'utf8',maxBuffer:4*1024*1024});if(p.status!==0)throw Error(p.stderr||String(p.error));}
if(!process.env.WINDIR)throw Error('WINDIR is required for local Segoe UI preview text.');
const font=path.join(process.env.WINDIR,'Fonts','segoeui.ttf').replaceAll('\\','/').replace(':','\\:');
function full(name,file,sec){run(['-v','error','-y','-ss',sec,'-i',path.join(A,file),'-frames:v','1','-vf','scale=960:540','-q:v','3',path.join(OUT,name+'.jpg')]);}
function split(name,left,leftAt,app,appAt) {
  const f=`color=c=0x0a0d12:s=960x540:d=0.1[bg];[0:v]crop=1232:1080:344:0,scale=616:540[left];[1:v]scale=236:500[phone];[bg][left]overlay=0:0[x];[x][phone]overlay=670:20,drawbox=x=669:y=19:w=238:h=502:color=white@0.14:t=1,drawtext=fontfile='${font}':text='iTantra':fontcolor=white:fontsize=18:x=688:y=45[out]`;
  const inLeft=left.endsWith('.jpg')?['-loop','1','-i',path.join(A,left)]:['-ss',leftAt,'-i',path.join(A,left)];
  run(['-v','error','-y',...inLeft,'-ss',appAt,'-i',path.join(A,app),'-filter_complex',f,'-map','[out]','-frames:v','1','-q:v','3',path.join(OUT,name+'.jpg')]);
}
function maps(){const f=`color=c=0x0a0d12:s=960x540:d=0.1[bg];[0:v]scale=243:540[p];[bg][p]overlay=358:0,drawtext=fontfile='${font}':text='~300 m, walking distance':fontcolor=white:fontsize=18:x=364:y=455[out]`;
  run(['-v','error','-y','-ss','1.75','-i',path.join(A,'maps.mp4'),'-filter_complex',f,'-map','[out]','-frames:v','1','-q:v','3',path.join(OUT,'maps.jpg')]);}
full('bench_full','bench.mp4',3.0);
split('split_mid_send','bench.mp4',7.0,'vachana_send.mp4',2.2);
split('freeze','bench_end.jpg',0,'vachana_send.mp4',13.02);
full('walk','walk.mp4',3.0);maps();
full('yash_full','yash.mp4',1.8);
split('yash_split_tts','yash_mid.jpg',0,'yash_app.mp4',8.0);
split('yash_split_reply','yash.mp4',9.2,'yash_app.mp4',13.2);
full('sonar','sonar_a.mp4',4.0);
full('last_frame','sonar_b.mp4',5.8);
console.log('Wrote ten 960px review stills.');
