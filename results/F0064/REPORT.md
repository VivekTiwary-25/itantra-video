---
status: done
---

# F0064 scene 4 fixes

Scene 4 now builds N7–N7d as five 2.5-second beats from the current 2.1-second narration durations plus 0.4 seconds each. The five number labels appear in order and remain fully visible for at least 2.91 seconds. The Blender phone turns continuously through the turntable beat and into the teardown; the fallback phone follows the same motion. Both use the cleaned local home screen without a status bar.

Rebuilt the transparent Blender sequence and overlay at `RENDERS:scene4/blender_f0064/` and `RENDERS:scene4/blender_f0064/phone.webm`. The scene audio at `RENDERS:scene4/scene4_audio.wav` now makes silence at the manifest duration for dropped placeholder lines; the older stand-in WAVs have stale lengths and no speech. The production composition stages the new overlay through `film/scene4/build.py`.

Seven 1920×1080 stills, a 480-pixel-per-shot contact sheet, and a judge-impact line for each still are in `results/F0064/preview/`. `hyperframes.cmd check film/scene4` passed: 0 runtime errors, 0 layout issues, 0 motion issues, 8/8 contrast checks. The overlay probes as 1920×1080, 30 fps, 13.6 seconds, VP9 with alpha. No full scene render was made, as requested.

The existing untracked `debug.log` was already present and was not changed. Temporary comparison snapshots remain under `results/F0064/preview/` because automatic approval review blocked their deletion.
