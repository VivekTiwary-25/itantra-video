#!/bin/sh
set -eu

# Run from the repository root with FOOTAGE_ROOT pointing at the footage folder.
# Optional first argument overrides the output path.
: "${FOOTAGE_ROOT:?Set FOOTAGE_ROOT to the folder containing Video/}"
. film/scene1/grades.sh
out="${1:-results/T0006/preview/walk_ramp.mp4}"
mkdir -p "$(dirname "$out")"

ffmpeg -hide_banner -y -i "$FOOTAGE_ROOT/Video/normalpart2.mp4" \
  -filter_complex "\
[0:v]trim=start=25.50:end=26.00,setpts=PTS-STARTPTS,fps=30,scale=960:540,setsar=1[v0];\
[0:v]trim=start=26.00:end=28.00,setpts=(PTS-STARTPTS)/4,fps=30,scale=960:540,setsar=1[v1];\
[0:v]trim=start=40.00:end=191.00,setpts=(PTS-STARTPTS)/38,fps=30,scale=960:540,setsar=1[v2];\
[0:v]trim=start=199.00:end=201.55,setpts=(PTS-STARTPTS)/6,fps=30,scale=960:540,setsar=1[v3];\
[0:v]trim=start=201.55:end=202.15,setpts=PTS-STARTPTS,fps=30,scale=960:540,setsar=1[v4];\
[v0][v1][v2][v3][v4]concat=n=5:v=1:a=0,${GRADE_V1},format=yuv420p[v]" \
  -map "[v]" -an -c:v libx264 -preset medium -crf 23 -movflags +faststart "$out"
