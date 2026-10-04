---
status: done
---

# F0044 scene 4

Built the specified fallback. Blender and the downloaded phone model were unavailable when work began, so `film/scene4/` uses a generic Three.js phone for the showroom turntable and the existing `RENDERS:exploded_v2/` image layers for the processor opening. The phone has no logo, and its back is never presented to the camera. `film/scene4/CREDITS.md` records that no downloaded model credit applies.

Made a moving lab push-in from `FOOTAGE:Video/sospart2.mp4`, graded with the same camera grade as scene 3; processor numbers with a shrinking size bar and soft ticks; a second turntable phone, gold Bluetooth packet and speaker waves; and the final `No new hardware.` line. The on-screen strings follow spec 005. `film/scene4/render.cmd` rebuilds the assets, narration-driven timing and captions, renders the composition, and muxes audio.

Outputs: `RENDERS:scene4/scene4.mp4` and `RENDERS:scene4/scene4_audio.wav`. Ten 1920×1080 stills and `results/F0044/preview/contact-sheet-480.jpg` cover the bridge, spin, opening, number beats, packet and end line. The full result is 20.30 s, 1920×1080, 30 fps, 609 frames, H.264/AAC.

Verification: `hyperframes.cmd check film/scene4` passed with no errors or layout issues and 4/4 contrast checks. Stills were reviewed at full size and in the 480 px sheet. `ffprobe` verified both video and audio streams and the exact frame count. No output inside the committed paths exceeds 20 MB.

Notes: N7–N7d are still placeholders in `film/common/narration_v4.json`; this render contains silence for those lines, and `film/captions/v3/s4.json` is empty until the real transcripts arrive. Re-running `render.cmd` picks up their actual durations, WAVs and text. The optional TTS clip was omitted so the N7c narration and its future caption remain clear. Scene 3's last camera frame is at source 10.667 s and its lab clip ends at 10.701 s; the bridge therefore uses the last moving section at source 9.333–10.667 s, as the fallback permits. Check the join once scene 3 v4 is rebuilt.
