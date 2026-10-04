---
status: done
---

# F0066: Scene 3 SOS banner hold

Removed the first idle cut before Vivek's Accept tap. A trial shortening it to 1.000–1.600 s left only about 1.5 s from the visible banner arrival to the tap, so removing it was needed to meet the 2.0 s minimum. The other four idle cuts and their three-frame dissolves are unchanged.

The banner is visible by scene time 34.233 s and settled by 34.333 s. The visible Accept tap is at about 36.900 s, leaving at least **2.567 s** from the settled banner to the tap. The new scene length is **48.767 s** (previously 47.467 s).

`film/scene3/v3/build.py` now generates the retimed app slot, camera windows, timeline and composition. `film/captions/v3/s3.json` shifts the TTS and reply captions. The rebuilt dialogue/effects stem has TTS at 38.913 s, Vivek's reply at 43.240 s, and the Send sound at 48.370 s. Generated media and audio events are at `RENDERS:F0060/scene3/v3/` (the build's existing writable fallback on this machine).

Previews in `results/F0066/preview/`: `banner-arrival.png`, `before-accept.png`, `accept-tap.png`, `after-accept.png`, and `sheet_480.jpg` (four 480 × 270 thumbnails). The app recording is not sped up.

Verification: `python film/scene3/v3/build.py --page-only` completed with `missing: []`; independent `hyperframes.cmd check` passed; `git diff --check` passed. The check reported only existing non-fatal Three.js and intentional camera overflow warnings.

## Files moved out of git by the listener

- `film/scene3/v3/assets/vachana.mp4` (22.9 MB) was too big for git. Moved to local path: `RENDERS:F0066/film/scene3/v3/assets/vachana.mp4` (inside renders_dir on vivek-pc)
