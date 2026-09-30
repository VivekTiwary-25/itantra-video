---
status: done
---

# T0007 — scene 2 assembly

## Made

- `film/scene2/main/build.py` builds the graded camera plates, the T0006 walk ramp, a staged copy of the five sonar compositions, the main HyperFrames page, separate audio tracks, and both final mixes. It runs with `python film/scene2/main/build.py` from the repository root or any working directory. Media assets are generated under `local/renders/scene2/` and linked into the composition's ignored `assets/` folder.
- `film/scene2/main/slots.json` holds the five replaceable app paths and durations. `index.html.tpl`, generated `index.html`, `timeline.json`, `hyperframes.json`, the local GSAP copy, and `.gitignore` are in `film/scene2/main/`.
- `results/T0007/preview/` contains ten 960-pixel JPG stills from the final no-music draft.
- Two complete drafts: `RENDERS:scene2/scene2_draft_music.mp4` and `RENDERS:scene2/scene2_draft_nomusic.mp4`. Both are 1920×1080, 30 fps, 2,944 frames, 98.133 seconds. Encoded audio measures **−16.2 LUFS integrated, −1.7 dBTP** in each. `hyperframes check` passed during the build.

## Exact timeline

Times are scene seconds. The 0.5-second dissolve from the bench to `vachana_send` starts at 7.700 and ends at 8.200, inside the first 0.5 seconds of that slot.

| Segment | Start | End |
|---|---:|---:|
| Doorway and “How the app works” | 0.000 | 3.000 |
| Bench, normalpart1 from source 0.0 | 3.000 | 7.700 |
| `vachana_send` | 7.700 | 20.700 |
| Last-frame freeze; N1 at 20.900 | 20.700 | 24.300 |
| Graded T0006 walk ramp | 24.300 | 30.300 |
| `maps` | 30.300 | 33.800 |
| Yash before notification, normalpart6 source 0–2.65 | 33.800 | 36.467 |
| `yash_receive`, notification at 36.467 | 36.467 | 45.467 |
| Yash after notification, normalpart6 source 3.6–10.667 | 45.467 | 52.533 |
| `yash_reply` | 52.533 | 57.033 |
| `sonar_a`; N2 at 57.033 | 57.033 | 64.033 |
| `relay_1` | 64.033 | 70.033 |
| `relay_2` | 70.033 | 76.033 |
| `relay_3` | 76.033 | 82.033 |
| `sonar_b`; N3 at 86.033 | 82.033 | 88.033 |
| Sonar last-frame hold and fade; N4 at 88.333 | 88.033 | 90.633 |
| `vachana_reply` | 90.633 | 97.633 |
| Final app-frame hold | 97.633 | 98.133 |

N1–N4 remain separate, fixed-start WAV tracks in `RENDERS:scene2/N1.wav` through `RENDERS:scene2/N4.wav`. Dialogue, app audio, effects, and sonar-only music are also separate render stems. Camera plates use scene 1 `GRADE_V1`; app recordings are never graded. The normalpart1 side image continues moving from source 4.7 to 10.8, then holds the last available frame. The sonar music is absent from every other section.

## Replacing an app slot

1. Put each portrait recording under `local/renders/scene2/app/`, or change that slot's `RENDERS:` path in `film/scene2/main/slots.json` to another path relative to `local/renders/`. Keep the paths relative; never add a machine path to a committed file.
2. Keep the listed `duration` to preserve this cut. Changing it moves all later segments and narration starts on the next build. For `vachana_send`, `sent_at` is seconds into the slot and places the soft send blip (currently 12.5).
3. Record `ptt_down` and `ptt_up` as seconds into `vachana_send` after aligning the screen recording. Vachana's clean spoken line occupies approximately **0.182–4.762 seconds into that slot**. These fields document the PTT hold; they do not retime the fixed dialogue or the recording. Align or trim the recording before rerunning the build.
4. Run `python film/scene2/main/build.py`. A present slot file replaces its dark `APP: <slot name>` card. Its own audio is mixed when available; the Yash notification uses the slot's audio, `RENDERS:scene2/app/notify.wav` if supplied, or a soft procedural placeholder tone.

Current missing slots are `vachana_send` (13.0 s), `maps` (3.5 s), `yash_receive` (9.0 s), `yash_reply` (4.5 s), and `vachana_reply` (7.0 s). Their marked cards are for this review draft only.

## Notes for review

- The specified cut durations total **98.133 seconds**, longer than the task's “about 80 s” estimate. I kept the lead's exact segment lengths and source cuts.
- `brief/style.md` was not present. The doorway, phone layout, font, colour, and timing follow this task and the supplied scene 1 assets.
- The normalpart6 sync analysis reports drift even though the task fixes its offset at −0.370 s. The build uses the required offset; check Yash's lip sync by ear before final use. The opening “Oh” partly precedes video source zero at this offset.
- The bench phone push reaches a close view from a small area of the camera frame, so the last part is visibly upscaled. The real portrait app recording replaces that close view at the dissolve.
- The sonar folders were staged and rendered under `local/renders/scene2/`; the supplied `film/scene2/sonar/` files were not edited.

## Files moved out of git by the listener

- `film/scene2/main/assets/walk.mp4` (29.7 MB) was too big for git. Moved to local path: `RENDERS:T0007/film/scene2/main/assets/walk.mp4` (inside renders_dir on vivek-pc)
