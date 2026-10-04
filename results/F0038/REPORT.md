---
status: done
---

## Made
- Matched s2a's opening card to the intro's glass-kit full card: 64 px `h1`, matching font, tint, and centred position. The bench plate fades in behind the card after frame 0.
- Faded s3's red background layer from 0.68 at frame 0 to 0.04 by 0.8 s, while leaving the opening card and timing intact.
- Darkened s3's last 0.3 s to `#05070a` and faded the exploded view up from near-black over its first 0.4 s. Segment durations are unchanged.
- Made the requested 960 px stills in `preview/`, including `intro_s2a_side_by_side.png` (two 960 px frames).

## Checks and notes
- Intro last frame (13.767 s) versus s2a frame 0: RGB mean absolute difference **0.000/255** at 960×540. `compare.js` reproduces the measurement.
- s3 last frame versus exploded frame 0: RGB mean absolute difference **0.088/255** at 960×540.
- HyperFrames checks passed for s2a, s3, and exploded view. After the final s2a frame-0 background adjustment, its check took unusually long and was stopped; its final frame-0 snapshot was captured and compared as above. s3 and exploded checks passed on the final code.
- The scene 3 graded camera plate was staged locally in its ignored `assets/` folder for preview. No footage or large media is committed.

## Files moved out of git by the listener

- `film/scene2/v3a/assets/walk.mp4` (24.0 MB) was too big for git. Moved to local path: `RENDERS:F0038/film/scene2/v3a/assets/walk.mp4` (inside renders_dir on yash-pc)
- `film/scene3/v3/assets/vachana.mp4` (22.9 MB) was too big for git. Moved to local path: `RENDERS:F0038/film/scene3/v3/assets/vachana.mp4` (inside renders_dir on yash-pc)
