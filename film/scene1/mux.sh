#!/usr/bin/env bash
# Replace the render's audio with the exact scene-1 mix: voice (+25 ms to line up with picture) and the doorway sound.
# Voice is mono at -16 LUFS; played on both channels it is lowered 3 dB so the stereo file measures -16 LUFS.
# Run from the repo root:  bash film/scene1/mux.sh <rendered.mp4> <out.mp4>
set -euo pipefail
A=film/scene1/assets
ffmpeg -v error -y -i "$1" -i $A/voice.wav -i $A/doorway.wav -filter_complex \
 "[1:a]adelay=25,pan=stereo|c0=c0|c1=c0,volume=-3dB[v];[2:a]adelay=54675|54675,volume=-3dB[s];[v][s]amix=inputs=2:normalize=0:duration=first,atrim=end=58[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 256k -movflags +faststart "$2"
