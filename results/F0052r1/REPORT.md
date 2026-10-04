---
status: done
---

# F0052r1 scene 4

Rendered the licensed teardown model in Blender for the lab lift, showroom spin, closing handoff, and two-phone packet shot. The model's own internal parts were tested with opaque glTF circuit materials, but the opening still read as sparse at phone size. The composition therefore uses the accepted F0044 image layers for the processor opening, with a short crossfade into and out of the Blender footage. The board, processor area, and battery are clearly visible while the numbers appear. The timing, labels, packet, ticks, narration hooks, and lab bridge remain driven by the existing scene 4 timeline.

Updated `film/scene4/blender_scene.py`, `encode_blender.py`, `build.py`, `scene.js`, `render.cmd`, `README.md`, and the built `index.html`. The model credit in `film/scene4/CREDITS.md` matches the local license note. No model source, footage, audio source, or private home-screen image was added to git.

Outputs: PNG sequences at `RENDERS:scene4/blender/lift/`, `RENDERS:scene4/blender/spin/`, `RENDERS:scene4/blender/close/`, and `RENDERS:scene4/blender/pair/`; plus `RENDERS:scene4/blender/phone.webm`, `RENDERS:scene4/scene4_audio.wav`, and `RENDERS:scene4/scene4.mp4`. Six 1920×1080 stills, a 480-pixel-per-shot contact sheet, and one-line judge-impact verdicts are in `results/F0052r1/preview/`.

Verification: `hyperframes.cmd check film/scene4` passed with 0 errors, 0 layout issues, 0 motion issues, and 4/4 contrast checks. The final MP4 was checked from an encoded processor frame and by `ffprobe`: 1920×1080, 30 fps, 609 frames, 20.30 s, H.264 video and AAC audio. The sampled front views show no rear camera or Apple logo.

Notes: N7–N7d still have placeholder durations and empty transcript text in `film/common/narration_v4.json`; the composition rebuilds from their real values when supplied. The audio export currently contains the existing placeholder narration treatment and ticks. The accepted F0044 Three.js composition remains available if the local Blender video is absent.
