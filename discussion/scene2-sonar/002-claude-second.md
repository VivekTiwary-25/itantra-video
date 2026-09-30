# scene2-sonar: progress 1

From: claude-second

`sonar_a` and `relay_1` are ready to cut in. `relay_2`, `relay_3` and `sonar_b` are pushed too, as v1. All five pass `hyperframes check` with 0 errors (the only warning is Three.js r160's own "global build is deprecated" console note).

- **Build:** `python film/scene2/sonar/build.py` (makes graded plates, sfx stems, music, and copies the scripts in), then `cd film/scene2/sonar/<segment>` and `hyperframes.cmd render -q high -f 30 -o <out>.mp4`. On this PC the renders take 85 s (sonar_a) and 50 s (relay_1).
- **Lengths:** exact, 210 / 180 / 180 / 180 / 180 frames.
- **Stills:** in `results/T0004/preview/`.
- **Thrisha:** she *is* the walker in normalpart3. She enters at about 4.5 s. Her phone is clipped in her front jeans pocket, so relay_3 freezes at 6.5 s of the source.
- **V position:** OSM puts the main gate at about (350,515) in the image frame, not (345,605). I put V on the internal road at (330,598), about 30 px from your suggested point.
- **Red:** the kept-colour area is tight on the phone, so Utkarsh's red shirt and Thrisha's pink shirt stay grey.

Next I'm polishing these (timing and sound). The full report goes in `results/T0004/REPORT.md`.
