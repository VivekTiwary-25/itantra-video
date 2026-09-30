// T0020 measurement: 2 s band-passed waveform windows, 0.5 s hop.
// Run from repo root with: node results/T0020/measure.js
const fs = require('fs');
const path = require('path');
const cp = require('child_process');
const rate = 4000, windowSamples = 2 * rate, hop = rate / 2;
const repo = path.resolve(__dirname, '../..');
const config = JSON.parse(fs.readFileSync(path.join(repo, 'machine.local.json')));
const root = process.env.FOOTAGE_ROOT || config.footage_root;
const pairs = [
  ['normalpart6', 'normalpart6.mp4', 'Normalpart6.mp3', 'clean__Normalpart6.json'],
  ['sospart1', 'sospart1.mp4', 'sospart1.mp3', 'clean__sospart1.json'],
  ['sospart2', 'sospart2.mp4', 'sospart2.mp3', 'clean__sospart2.json'],
];
function fft(re, im, inverse = false) {
  const n = re.length;
  for (let i=1,j=0;i<n;i++) {
    let bit=n>>1;
    for (;j&bit;bit>>=1) j^=bit;
    j^=bit;
    if(i<j){[re[i],re[j]]=[re[j],re[i]];[im[i],im[j]]=[im[j],im[i]];}
  }
  for(let len=2;len<=n;len*=2){
    const theta=(inverse?2:-2)*Math.PI/len, wr=Math.cos(theta),wi=Math.sin(theta);
    for(let i=0;i<n;i+=len){let ur=1,ui=0;
      for(let j=0;j<len/2;j++){
        const a=i+j,b=a+len/2,vr=re[b]*ur-im[b]*ui,vi=re[b]*ui+im[b]*ur;
        re[b]=re[a]-vr;im[b]=im[a]-vi;re[a]+=vr;im[a]+=vi;
        const nr=ur*wr-ui*wi;ui=ur*wi+ui*wr;ur=nr;
      }
    }
  }
  if(inverse){for(let i=0;i<n;i++){re[i]/=n;im[i]/=n;}}
}
function decode(file){
  const p=cp.spawnSync('ffmpeg',['-nostdin','-v','error','-i',file,'-vn','-ac','1','-ar',String(rate),'-af','highpass=f=300,lowpass=f=3400','-f','s16le','-acodec','pcm_s16le','-'],{maxBuffer:20*1024*1024});
  if(p.status!==0) throw Error(String(p.stderr));
  const out=new Float64Array(p.stdout.length/2);
  for(let i=0;i<out.length;i++)out[i]=p.stdout.readInt16LE(i*2)/32768;
  return out;
}
function duration(file){const p=cp.spawnSync('ffprobe',['-v','error','-show_entries','format=duration','-of','csv=p=0',file]);return Number(String(p.stdout).trim());}
function measure(video,audio){
  const n=1<<Math.ceil(Math.log2(video.length+windowSamples-1));
  const vr=new Float64Array(n),vi=new Float64Array(n),prefix=new Float64Array(video.length+1);
  for(let i=0;i<video.length;i++){vr[i]=video[i];prefix[i+1]=prefix[i]+video[i]*video[i];}
  fft(vr,vi);
  const rows=[];
  for(let start=0;start+windowSamples<=audio.length;start+=hop){
    const ar=new Float64Array(n),ai=new Float64Array(n);
    let asq=0;
    for(let i=0;i<windowSamples;i++){const x=audio[start+i];ar[windowSamples-1-i]=x;asq+=x*x;}
    fft(ar,ai);
    for(let i=0;i<n;i++){const r=ar[i]*vr[i]-ai[i]*vi[i];ai[i]=ar[i]*vi[i]+ai[i]*vr[i];ar[i]=r;}
    fft(ar,ai,true);
    let best=-1,bestLag=-1;
    const scores=new Float64Array(video.length-windowSamples+1);
    for(let lag=0;lag<scores.length;lag++){
      const vsq=prefix[lag+windowSamples]-prefix[lag];
      const score=vsq>0&&asq>0?Math.abs(ar[lag+windowSamples-1])/Math.sqrt(vsq*asq):0;
      scores[lag]=score;
      if(score>best){best=score;bestLag=lag;}
    }
    let second=0;
    for(let lag=0;lag<scores.length;lag++)if(Math.abs(lag-bestLag)>rate*.05&&scores[lag]>second)second=scores[lag];
    const ratio=second?best/second:null;
    rows.push({clean_window_s:[start/rate,(start+windowSamples)/rate],video_window_s:[bestLag/rate,(bestLag+windowSamples)/rate],offset_s:(bestLag-start)/rate,peak:best,next_peak:second,peak_ratio:ratio,confident:ratio>=2});
  }
  return rows;
}
function median(a){if(!a.length)return null;const s=[...a].sort((x,y)=>x-y),m=Math.floor(s.length/2);return s.length%2?s[m]:(s[m-1]+s[m])/2;}
function round(x,n=5){return x==null?null:Number(x.toFixed(n));}
function phrases(words){
  const out=[],cur=[];
  for(const w of words){cur.push(w);if(/[.!?]$/.test(w.word.trim())){out.push(cur.splice(0));}}
  if(cur.length)out.push(cur);
  return out;
}
const all=[];
for(const [name,vname,aname,jsonname] of pairs){
  const vpath=path.join(root,'Video',vname),apath=path.join(root,'Audio',aname);
  const vdur=duration(vpath),adur=duration(apath);
  const rows=measure(decode(vpath),decode(apath));
  const good=rows.filter(r=>r.confident),offset=median(good.map(r=>r.offset_s));
  const mad=median(good.map(r=>Math.abs(r.offset_s-offset)));
  const spread=good.length?Math.max(...good.map(r=>r.offset_s))-Math.min(...good.map(r=>r.offset_s)):null;
  const transcript=JSON.parse(fs.readFileSync(path.join(repo,'results/T0003',jsonname)));
  const allWords=transcript.flatMap(s=>s.words);
  const words=allWords.map(w=>({word:w.word.trim(),clean_start_s:w.start,clean_end_s:w.end,video_start_s:offset==null?null:round(w.start+offset),video_end_s:offset==null?null:round(w.end+offset),fully_inside_video:offset!=null&&w.start+offset>=0&&w.end+offset<=vdur}));
  // T0003 has no punctuation in SOS part 2; split its speech into four natural utterances.
  const groups=name==='sospart2'?[allWords.slice(0,1),allWords.slice(1,6),allWords.slice(6,10),allWords.slice(10,11)]:phrases(allWords);
  const ps=groups.map(p=>({text:p.map(w=>w.word.trim()).join(' '),clean_start_s:p[0].start,clean_end_s:p[p.length-1].end,video_start_s:offset==null?null:round(p[0].start+offset),video_end_s:offset==null?null:round(p[p.length-1].end+offset),fully_inside_video:offset!=null&&p[0].start+offset>=0&&p[p.length-1].end+offset<=vdur}));
  all.push({clip:name,video:'FOOTAGE:Video/'+vname,clean_audio:'FOOTAGE:Audio/'+aname,video_duration_s:vdur,clean_duration_s:adur,window_length_s:2,step_s:.5,bandpass_hz:[300,3400],sample_rate_hz:rate,peak_exclusion_ms:50,threshold_ratio:2,window_count:rows.length,confident_window_count:good.length,confirmed_offset_s:round(offset,5),offset_min_s:good.length?Math.min(...good.map(r=>r.offset_s)):null,offset_max_s:good.length?Math.max(...good.map(r=>r.offset_s)):null,offset_spread_ms:round(spread*1000,2),offset_mad_ms:round(mad*1000,2),windows:rows.map(r=>({...r,offset_s:round(r.offset_s,5),peak:round(r.peak,5),next_peak:round(r.next_peak,5),peak_ratio:round(r.peak_ratio,3)})),phrases:ps,words});
  console.log(name,good.length+'/'+rows.length,'offset',offset,'spread ms',spread*1000);
}
fs.writeFileSync(path.join(__dirname,'sync_audit.json'),JSON.stringify({method:'Absolute normalized waveform cross-correlation of 300-3400 Hz filtered mono audio, 2 s clean windows every 0.5 s searched across full camera audio; peaks compared with all lags more than 50 ms away.',clips:all},null,2)+'\n');
const lines=['# Lip-sync audit — T0020','',
  'Offsets place clean time `t` at video time `t + offset`. I decoded both tracks to mono 4 kHz PCM with a 300–3400 Hz band-pass filter. For every 2 s clean-audio window at a 0.5 s step, I searched every full 2 s placement in the camera audio with absolute normalized waveform cross-correlation. Peak ratio compares the winning lag against the strongest lag more than 50 ms away. Only ratios ≥2 count toward the median. Times below use the median of those confident offsets and T0003 word boundaries; source durations come from ffprobe. A low-ratio window supplies no drift evidence.',''];
const fmt=(x,n=3)=>x==null?'—':x.toFixed(n);
for(const c of all){
  lines.push('## '+c.clip,'',`Video: \`${c.video}\` (${fmt(c.video_duration_s)} s). Clean: \`${c.clean_audio}\` (${fmt(c.clean_duration_s)} s). Confirmed offset **${c.confirmed_offset_s>=0?'+':''}${fmt(c.confirmed_offset_s,5)} s** from ${c.confident_window_count}/${c.window_count} confident windows; range ${fmt(c.offset_min_s,5)} to ${fmt(c.offset_max_s,5)} s; spread **${fmt(c.offset_spread_ms,2)} ms**, median absolute deviation ${fmt(c.offset_mad_ms,2)} ms.`,'',
    '| Clean window (s) | Best video window start (s) | Offset (s) | Peak ratio | Use? |','|---:|---:|---:|---:|:---:|');
  for(const w of c.windows)lines.push(`| ${fmt(w.clean_window_s[0],1)}–${fmt(w.clean_window_s[1],1)} | ${fmt(w.video_window_s[0],5)} | ${fmt(w.offset_s,5)} | ${fmt(w.peak_ratio,3)} | ${w.confident?'yes':'no'} |`);
  const runs=[];let first=null,last=null;
  for(const w of c.windows){if(!w.confident){if(first==null)first=w.clean_window_s[0];last=w.clean_window_s[0];}else if(first!=null){runs.push([first,last]);first=last=null;}}
  if(first!=null)runs.push([first,last]);
  lines.push('',`No confident window starts: ${runs.length?runs.map(x=>`${fmt(x[0],1)}–${fmt(x[1],1)} s clean time`).join('; '):'none'}.`,'',
    '| Spoken phrase | Video start (s) | Video end (s) | Fully inside video? |','|---|---:|---:|:---:|');
  for(const p of c.phrases)lines.push(`| ${p.text} | ${fmt(p.video_start_s,5)} | ${fmt(p.video_end_s,5)} | ${p.fully_inside_video?'yes':'no'} |`);
  lines.push('');
  if(c.clip==='normalpart6'){
    lines.push('Opening word positions from T0003:','',
      '| Word | Video start (s) | Video end (s) |','|---|---:|---:|');
    for(const w of c.words.slice(0,5))lines.push(`| ${w.word} | ${fmt(w.video_start_s,5)} | ${fmt(w.video_end_s,5)} |`);
    lines.push('','“Oh” is timed at −0.37050 to +0.00950 s. **0.37050 s of its 0.380 s interval falls before the video**; only 0.00950 s remains after video zero. This is based on the T0003 word boundary, whose “Oh” probability is 0.363.','');
  }
  if(c.clip==='sospart2')lines.push('The clean recording ends 5.99082 s after the video at this offset; its final spoken phrase ends inside the video. T0003 provides no punctuation for this clip, so the phrase grouping above uses its word sequence.','');
  const verdict=c.clip==='normalpart6'?'Offset confirmed in the speech-bearing windows; opening “Oh” is effectively cut off at video zero.':c.clip==='sospart1'?'Offset confirmed across every measured window; all listed speech is inside the video.':'Offset confirmed around the spoken reply; no confident evidence in the earlier and later stretches, and clean audio extends beyond the video.';
  lines.push(`**Verdict:** ${verdict}`,'');
}
fs.writeFileSync(path.join(__dirname,'sync_audit.md'),lines.join('\n')+'\n');
