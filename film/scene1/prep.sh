#!/usr/bin/env bash
# Scene 1 prep: graded, trimmed, constant-30fps clips + cleaned voice track.
# Run from the repo root:  bash film/scene1/prep.sh
# Reads footage_root from machine.local.json. Outputs go to film/scene1/assets/ (git-ignored media).
set -euo pipefail
R=$(python -c "import json;print(json.load(open('machine.local.json'))['footage_root'])")
A=film/scene1/assets
mkdir -p "$A"

# --- colour (draft, see film/scene1/REPORT.md) ---
# part 2 is matched to part 1 using the grey brick wall as the neutral reference
MATCH2="lutrgb=r='clip(val*0.970,0,255)':g='clip(val*0.972,0,255)':b='clip(val*0.966,0,255)'"
# one natural look: gentle S-curve with highlight roll-off, warm mids / cool shadows, -10% saturation, soft vignette
LOOK="curves=master='0/0.02 0.12/0.10 0.5/0.5 0.82/0.84 0.94/0.92 1/0.955',colorbalance=rs=-0.02:bs=0.035:rm=0.025:bm=-0.02:rh=0.01:bh=-0.01,eq=saturation=0.9,vignette=a=PI/7"
ENC="-an -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart"

# part 1: video 0.80 s -> 18.80 s (first 0.8 s has a finger over the lens)
ffmpeg -v error -y -ss 0.8 -t 18.0 -i "$R/Video/vachna part1.mp4" -vf "fps=30,${LOOK}" $ENC "$A/part1.mp4"
# part 2: whole clip, then hold the last frame 2.88 s for the doorway (scene ends at 58.0 s)
ffmpeg -v error -y -i "$R/Video/vachna part2.mp4" -vf "fps=30,${MATCH2},${LOOK},tpad=stop_mode=clone:stop_duration=2.88,trim=end=40.0" $ENC "$A/part2.mp4"

# --- voice ---
# sync (cross-correlation vs camera audio, no drift): clean t plays at video t+0.571 (part 1), t+0.389 (part 2)
# scene time: part1 clean t -> t - 0.229 ; part2 clean t -> t + 18.389
CH="pan=mono|c0=0.5*c0+0.5*c1,highpass=f=100:poles=2,highpass=f=100:poles=2,afftdn=nr=30:nf=-26:tn=0,agate=threshold=0.025:ratio=2:range=0.35:attack=5:release=180:knee=4,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3000:t=q:w=1.0:g=2,deesser=i=0.3:m=0.5:f=0.5,acompressor=threshold=-20dB:ratio=2:attack=10:release=150"
ffmpeg -v error -y -i "$R/Audio/vachna part1.mp3" -i "$R/Audio/vachna part2.mp3" -filter_complex \
 "[0:a]$CH,atrim=start=0.229:end=18.2,asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st=17.7:d=0.25[a];\
[1:a]$CH,atrim=end=36.6,asetpts=PTS-STARTPTS,afade=t=out:st=36.3:d=0.3,adelay=18389|18389[b];\
[a][b]amix=inputs=2:normalize=0,apad=whole_dur=58,atrim=end=58,volume=7.1dB,alimiter=limit=0.84:attack=2:release=50:level=false[m]" \
 -map "[m]" -ar 48000 "$A/voice.wav"
echo "prep done"
