---
status: done
---

# Scene 3 v2 hand-back

Made `film/scene3/v2/` as a copy of v1 with a new 61.933 s cut, the 3.0 s SOS intro card, camera/app split screens, a continuous `vivek_app` slot, word-window dialogue gating, procedural cues, separate sonar music, and the trimmed response ending. `build.py` creates one composite picture render plus `RENDERS:scene3/v2/scene3_dialogue_sfx.wav` and `RENDERS:scene3/v2/scene3_music.wav`. It checks every referenced video and image before the composite render. Camera plates use `GRADE_V1`; app recordings remain ungraded. The original three sonar compositions are staged and rendered without editing them.

Build on the render machine: `python film/scene3/v2/build.py`. Its output picture is `RENDERS:scene3/v2/scene3_picture.mp4`. Missing app recordings become 1080x2290 portrait placeholders. The build reads `film/common/narration.json` when present (`david` or `vivek`) and otherwise selects David. David N5/N6 are read from `RENDERS:scene3/narration/david/`; Vivek N5/N6 from `RENDERS:narration/vivek/`.

## Slots expected by `slots.json`

| Slot | Fields, seconds from prepared slot start |
|---|---|
| `vachana_sos` | `duration: 12.966667`, `listen_at: 1.4`, `send_at: 11.23` |
| `vivek_app` | `duration: 21.366667`, `accept_at: 2.6`, `play_at: 7.63`, `ptt_down: 12.76`, `ptt_up: 16.22`, `sent_at: 19.77` |
| `vachana_response` | `duration: 6.966667`, `opened_at: 4.96` |

The `vivek_app` in-point is 4.75 s into `vivek_take.mkv`; its Accept tap stays 2.60 s into the unsped slot. The response duration includes 2.0 s after the opened message plus a separate 0.5 s end hold. `timeline.json` gives all starts and ends.

## Verification and preview

`hyperframes.cmd check` passed locally: zero lint/runtime/motion errors, zero warnings, and 8/8 text contrast checks. `hyperframes.cmd lint` also passed after updating the v2 composition ID. Nine 960 px stills are in `results/T0033/preview/`: intro, opening, mid-SOS split, original SOS sonar, lab Accept, Play, reply, response opened, and last frame. Local app panels are temporary UI placeholders; the sonar still was captured from the unchanged `film/scene3/sonar/sos_sonar` composition.

Python is unavailable on this worker, so the production `build.py` and audio stems were not executed here. App recordings, David narration, and TTS are also absent on this machine. The local preview was generated with `preview_build.mjs` and ignored media under `film/scene3/v2/assets/`. `film/common/narration.json` did not exist and was outside T0033's `writes:` paths, so it was not created; the build defaults to David until the shared config is added by its owner.
