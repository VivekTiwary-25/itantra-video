# Run from the repository root. All working files remain in local/thumbs/T0051.
$ErrorActionPreference = 'Stop'
$work = 'local/thumbs/T0051'
$sonar = "$work/sonar"
New-Item -ItemType Directory -Force $sonar, 'thumbnails', 'results/T0051/preview' | Out-Null
Copy-Item 'film/scene2/sonar/sonar_a/index.html', 'film/scene2/sonar/sonar_a/geo.js', 'film/scene2/sonar/sonar_a/hyperframes.json' $sonar
Copy-Item 'film/scene2/sonar/shared/sonar.js', 'film/scene2/sonar/shared/overlay.js', 'film/scene2/sonar/shared/sonar.css' $sonar
Copy-Item 'film/vendor/three/three.min.js', 'film/vendor/gsap/gsap.min.js' $sonar
Add-Content "$sonar/index.html" '<style>#ov,#black{display:none!important}</style>'
hyperframes.cmd snapshot $sonar --at 6.4 --no-end --describe false
$plate = "$sonar/snapshots/frame-00-at-6.4s.png"
$source = Get-Content 'thumbnails/src/T0051/index.html' -Raw
$names = @{ 4='v4_phone_rings'; 5='v5_sealed_in_transit'; 6='v6_no_signal_to_heard' }
foreach ($mode in 4,5,6) {
  $dir = "$work/v$mode"
  New-Item -ItemType Directory -Force $dir | Out-Null
  $source.Replace('data-mode="4"', "data-mode=`"$mode`"") | Set-Content "$dir/index.html" -Encoding utf8
  Copy-Item $plate "$dir/plate.png"
  Copy-Item 'film/scene2/sonar/sonar_a/hyperframes.json' "$dir/hyperframes.json"
  hyperframes.cmd snapshot $dir --at 0 --no-end --describe false
  Copy-Item "$dir/snapshots/frame-00-at-0s.png" "thumbnails/$($names[$mode]).png"
}
ffmpeg -y -i 'thumbnails/v4_phone_rings.png' -i 'thumbnails/v5_sealed_in_transit.png' -i 'thumbnails/v6_no_signal_to_heard.png' -filter_complex '[0:v]scale=320:180[a];[1:v]scale=320:180[b];[2:v]scale=320:180[c];[a][b][c]hstack=inputs=3' -frames:v 1 -update 1 'results/T0051/preview/sheet.png'
