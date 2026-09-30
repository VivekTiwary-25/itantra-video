#!/usr/bin/env bash
# Replace the render's audio with the exact scene-1 mix: voice (advanced 47 ms since v3 (two RNNoise passes add ~10 ms): measured by cross-correlating the
# final file's voice against the camera's own sound, which is the lip-sync reference) and the doorway sound.
# Voice is mono at -16 LUFS; played on both channels it is lowered 3 dB so the stereo file measures -16 LUFS.
# Timings come from film/scene1/cues.json (written by build.py).
# Run from the repo root:  bash film/scene1/mux.sh <rendered.mp4> <out.mp4>
set -euo pipefail
A=film/scene1/assets
read DOOR TOTAL < <(python -c "import json;c=json.load(open('film/scene1/cues.json'))['cues'];print(c['door'],c['total'])")
SFX_MS=$(python -c "print(int(round(($DOOR-0.05)*1000)))")
ffmpeg -v error -y -i "$1" -i $A/voice.wav -i $A/doorway.wav -filter_complex \
 "[1:a]atrim=start=0.047,asetpts=PTS-STARTPTS,apad,pan=stereo|c0=c0|c1=c0,volume=-3dB[v];[2:a]adelay=${SFX_MS}|${SFX_MS},volume=-3dB[s];[v][s]amix=inputs=2:normalize=0:duration=first,atrim=end=${TOTAL}[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -movflags +faststart "$2"
