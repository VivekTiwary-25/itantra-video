---
status: done
---

# S0003 — scene 2 drafts

The raw `vachana_send` take was not found. The only recording candidate in the requested `local/` search was `local/app/t.mkv` (3.463 s, 1080×2400), too short for the 13.133 s slot. There was no `vachana_send*.mkv` or `vachana_send*.mp4` in `local/app/`, `local/renders/scene2/app/`, or elsewhere under `local/`. The other MKV/MP4 files under `local/` are earlier drafts, test patterns, prepared plates, and the maps/sonar renders. `local/app/vachana_send.scrcpy.log` records an ADB startup failure, so no take was prepared. The placeholder remains. PTT and Send alignment cannot be checked visually; the timing in `slots.json` still maps the logged PTT down, PTT up, and Send events to slot 0.08, 5.29, and 12.12 s respectively.

Ran `python film/scene2/main/build.py` with the current `slots.json` and maps fallback. Outputs:

- `RENDERS:scene2/scene2_draft_music.mp4`
- `RENDERS:scene2/scene2_draft_nomusic.mp4`

Both drafts are 1920×1080, 30 fps, 2949 frames. Encoded audio measured −16.2 LUFS and −1.7 dBTP on each. `hyperframes.cmd check` passed: zero errors, one existing duplicate-media warning, and three intentional overflow notes.

Five 960×540 JPGs from the new no-music draft are in `results/S0003/preview/`: `vachana_send_0p3.jpg`, `vachana_send_2p5.jpg`, `vachana_send_12p3.jpg`, `maps_2p5.jpg`, and `sonar_b_5p5.jpg`. The first three show the placeholder; the maps and sonar stills show the expected graphics.

## Files moved out of git by the listener

- `film/scene2/main/assets/walk.mp4` (29.7 MB) was too big for git. Moved to local path: `RENDERS:S0003/film/scene2/main/assets/walk.mp4` (inside renders_dir on vivek-pc)
