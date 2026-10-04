# Scene 4 fallback

`python film/scene4/build.py` stages local assets and reads N7–N7d durations and transcripts from `film/common/narration_v4.json`. Then run `film/scene4/render.cmd` to render the 30 fps segment into `RENDERS:scene4/scene4.mp4`.

This fallback uses a generic Three.js phone for the closed showroom spin and the real image layers from `RENDERS:exploded_v2/` for the processor reveal. The screenshot, footage, and layer media are staged only into ignored `assets/`. `film/captions/v3/s4.json` is rebuilt from nonempty narration text fields.

The bridge uses the last moving 1.33 seconds of `FOOTAGE:Video/sospart2.mp4`, source 9.333–10.667 seconds. Scene 3's last visible camera frame is at source 10.667 seconds; the clip ends at 10.701 seconds, so later footage is unavailable. Check the join against the rebuilt scene 3 cut.
