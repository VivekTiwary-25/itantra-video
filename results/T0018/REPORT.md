---
status: done
---

Made `film/final/assemble.py`. It reads `machine.local.json`, checks all four video inputs and the separate scene 2/3 stems, joins on exact 30 fps frame boundaries, and produces the two films plus aligned dialogue, music-only, and normalized mix WAVs. Compatible H.264 streams use stream copy; otherwise the picture receives one libx264 CRF 16 encode. The final AAC export is measured after encoding and must meet -16 LUFS (within 0.3 LU) and at most -1.5 dBTP. The report JSON includes scene times and loudness measurements.

Run from the repo root on vivek-pc:

```powershell
python film/final/assemble.py
```

Synthetic ffmpeg test: four 1920x1080, 30 fps clips of 18 frames each, with generated sine dialogue/music. Ran once with matching H.264 streams (`video stream_copy`) and once with scene 3 changed to MPEG-4 (`video libx264_crf16`). The latter run printed:

```text
scene1: 18 frames, 0.600s; source 0.600s, 1920x1080, 30 fps
scene2: 18 frames, 0.600s; source 0.600s, 1920x1080, 30 fps
scene3: 18 frames, 0.600s; source 0.600s, 1920x1080, 30 fps
title: 18 frames, 0.600s; source 0.600s, 1920x1080, 30 fps
Boundary scene1 -> scene2: last frame 0.566667s; first next frame 0.600000s
Boundary scene2 -> scene3: last frame 1.166667s; first next frame 1.200000s
Boundary scene3 -> title: last frame 1.766667s; first next frame 1.800000s
Done: 2.400s; mix -16.01 LUFS, -14.04 dBTP; video libx264_crf16
```

`full_film_v1.mp4`, `full_film_v1_nomusic.mp4`, and `full_film_v1_music_only.wav` each probed at 2.400 seconds. The encoded film measured -16.01 LUFS and -14.01 dBTP. Synthetic media was removed after the test; no media is committed. Real renders are only available on vivek-pc, so their final loudness and scene-1/scene-2 visual match still need checking there.
