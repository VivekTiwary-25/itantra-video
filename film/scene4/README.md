# Scene 4 Blender phone and accepted fallback

`python film/scene4/build.py` stages local assets and reads N7–N7d durations and transcripts from `film/common/narration_v4.json`. Then run `film/scene4/render.cmd` to render the 30 fps segment into `RENDERS:scene4/scene4.mp4`.

The licensed teardown phone is rendered with `blender_scene.py` into transparent 1920x1080 PNG sequences under `RENDERS:scene4/blender/<shot>/`. Run Blender with `-- sequence hybrid` to render the lift, spin, close and pair shots. `python film/scene4/encode_blender.py` fills the processor interval with the last closed spin frame and makes `RENDERS:scene4/blender/phone.webm`. `render.cmd` composites the Blender footage with the accepted image-layer opening, lab bridge, unchanged labels, numbers, packet, ticks and captions. `build.py` stretches its five beats if the N7–N7d durations change. The model and private screenshot stay under `local/`; no source texture or footage is committed.

When a Blender sequence is absent, `build.py` selects the accepted F0044 generic Three.js phone and `RENDERS:exploded_v2/` image layers. The fallback source remains in this directory. Narration captions are built from nonempty `film/common/narration_v4.json` text fields into ignored `assets/captions.js`.

The bridge uses the last moving 1.33 seconds of `FOOTAGE:Video/sospart2.mp4`, source 9.333–10.667 seconds. Scene 3's last visible camera frame is at source 10.667 seconds; the clip ends at 10.701 seconds, so later footage is unavailable. Check the join against the rebuilt scene 3 cut.
