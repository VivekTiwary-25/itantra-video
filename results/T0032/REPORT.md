---
status: failed
---

# T0032 — scene 2 v2 first version

## What was made

- `film/scene2/v2/` was copied from `film/scene2/main/` and rebuilt without changing v1. It contains the split-screen composition, `build.py` entry point, Node build, three-slot `slots.json`, and `timeline.json` (89.067 s). The order ends with `sonar_b` and its 0.5 s hold; N4, the fade, and `vachana_reply` are absent.
- The camera plates use `GRADE_V1`; app slots are ungraded. The split layout uses a 1232 px camera panel, 688 px near-black app field, 1000 px portrait phone, 24 px camera-edge feather, and 0.5 s `power2.inOut` entrance. The bench is full frame without a push. Yash uses one continuous app slot while his camera picture pauses during TTS and resumes for his reply.
- Dialogue is sourced only from clean audio and windowed from 0.12 s before the first word through 0.30 s after the last, with 30 ms fades. The opening Yash window starts at the beginning of its clean file and can run over the preceding picture. Camera and screen-recording audio are excluded. The build uses `message_a` and `sent_a` from the local procedural sound designs; sent cues occur in both app slots. Music is confined to the 31 s sonar section.
- Before any picture render, the build regenerates missing assets, validates every referenced video with `ffprobe` for playability and required duration, and checks stills. Both final mixes use the same `scene2_picture.mp4` once rendered. The separate stems are `RENDERS:scene2/scene2_dialogue_sfx.wav` and `RENDERS:scene2/scene2_music.wav`.
- Ten 960 px review stills are in `results/T0032/preview/`. App screens and sonar are local visual placeholders in these stills because the real app recordings and prior sonar renders are absent here. The sonar fallback is marked locally and the normal build replaces it with the existing v1 renders or fresh HyperFrames renders.

## Slot handoff

| Slot | Path | Fields, seconds from slot start |
|---|---|---|
| `vachana_send` | `RENDERS:scene2/app/vachana_send.mp4` | `duration` 13.1333333333, `ptt_down` 0.08, `ptt_up` 5.24, `sent_at` 11.98 |
| `maps` | `RENDERS:scene2/app/maps_fallback.mp4` | `duration` 3.5 |
| `yash_app` | `RENDERS:scene2/app/yash_app.mp4` | `duration` 20.8666666667, `notification_at` 3.00, `play_at` 7.63, `ptt_down` 12.13, `ptt_up` 15.33, `sent_at` 18.87 |

For `yash_app`, the slot in-point is recording time 6.21 s. `notification_at`, `play_at`, `ptt_down`, `ptt_up`, and `sent_at` are the tap-log times minus 6.21 s. iTantra TTS is cued at `play_at + 0.15 s` from `RENDERS:tts_itantra/tts_msg.wav`.

## Build and verification

Build command on the render machine: `python film/scene2/v2/build.py` (or `node film/scene2/v2/build.js`). `node film/scene2/v2/build.js --prepare --preview` completed here, including `hyperframes.cmd check` in `film/scene2/v2/`. `node film/scene2/v2/build.js --audio-only --preview` produced the two 89.067 s local preview stems; N1–N3 are silent in them because their source files are absent on this worker.

The full picture and two MP4 mixes were **not** rendered on this machine. HyperFrames cannot launch its Chrome browser inside this worker sandbox. The local machine also lacks N1–N3 narration, the iTantra TTS file, and the real app recordings. A production build will require those local inputs. The default build fails loudly if the narration or TTS is missing.

`film/common/narration.json` is absent. The task asks to create it with `{"voice":"david"}`, but that path is outside T0032's complete `writes:` list. I did not write there. The build reads that file when present and defaults to `david` when absent; `vivek` selects `RENDERS:narration/vivek/N*.wav`, while `david` selects `RENDERS:scene2/narration/david/N*.wav`.

The copied v1 sonar pages can use their exact procedural plates and stems when those local assets exist. On this machine they do not, so the prepared review used marked static sonar visuals and a quiet procedural music fallback. These are not a substitute for the production render.

## Files moved out of git by the listener

- `film/scene2/v2/assets/walk.mp4` (24.0 MB) was too big for git. Moved to local path: `RENDERS:T0032/film/scene2/v2/assets/walk.mp4` (inside renders_dir on yash-pc)
