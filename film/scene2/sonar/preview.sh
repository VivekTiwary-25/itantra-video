#!/usr/bin/env bash
# Join the five rendered segments into one 31 s review file, with the sfx (from the renders) and, for version (a),
# the music bed. Review aid only: the lead cuts the segments in separately and does the real mix.
# Run from the repo root:  bash film/scene2/sonar/preview.sh <renders dir> <out.mp4> [a|b] [540]
#   <renders dir> holds sonar_a.mp4 relay_1.mp4 relay_2.mp4 relay_3.mp4 sonar_b.mp4 (rendered with sfx)
set -euo pipefail
D="$1"; OUT="$2"; VER="${3:-a}"; H="${4:-1080}"
MUSIC=film/scene2/sonar/music/sonar_music.wav
IN=(); for s in sonar_a relay_1 relay_2 relay_3 sonar_b; do IN+=(-i "$D/$s.mp4"); done
CAT="[0:v][0:a][1:v][1:a][2:v][2:a][3:v][3:a][4:v][4:a]concat=n=5:v=1:a=1[v][sfx]"
if [ "$VER" = "a" ]; then
  FC="$CAT;[v]scale=-2:$H:flags=lanczos[vo];[5:a]volume=0dB[m];[sfx][m]amix=inputs=2:normalize=0:duration=first[a]"
  ffmpeg -v error -y "${IN[@]}" -i "$MUSIC" -filter_complex "$FC" -map "[vo]" -map "[a]" \
    -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$OUT"
else
  FC="$CAT;[v]scale=-2:$H:flags=lanczos[vo]"
  ffmpeg -v error -y "${IN[@]}" -filter_complex "$FC" -map "[vo]" -map "[sfx]" \
    -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$OUT"
fi
echo "wrote $OUT"
