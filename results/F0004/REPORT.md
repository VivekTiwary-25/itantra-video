---
status: done
---

# Scene 2 v3a handoff

Built `film/scene2/v3a/` from v2, with the glass kit, cropped real message card, the six-second walk, F0006's campus overhead module when present, app takeovers, captions, and `YASH_REPLY` (default `false`). `film/captions/v3/s2a.json` has seven timed captions in the default cut. The composition uses no external URLs or invented app UI.

## Timeline (default cut)

| Segment | Film time |
| --- | ---: |
| Full “How the app works” card shrinks away | 0.000–1.600 |
| Bench, then split-in | 1.600–6.400 |
| Vachana app and phone takeover | 6.400–18.380 |
| Message card flight | 18.380–19.180 |
| Sped-up walk, overlapping flight by 0.400 s | 18.780–24.780 |
| Overhead | 24.780–29.780 |
| Yash full shot | 29.780–32.430 |
| Yash app, camera exit, TTS | 32.430–44.154 |

N1 starts at 19.080, 0.300 s into the walk. The walk uses v2's source pieces totalling 156.65 s in 6.00 s, displayed as `Sped up 26×`. The sent cue is at 18.380, notification cue at 33.880, and TTS at 40.210–43.554. The default cut ends 0.600 s after TTS. The full segment table and expected slot fields are in `film/scene2/v3a/timeline.json`.

**End state for s2b:** centred `yash_app` phone on `#0a0d12`, slot time **11.690 s on the final 30 fps frame**, x=735, y=40, width=450, height=1000 px. `YASH_REPLY=true` retains Yash's spoken reply and Send and ends at 53.297 s on the centred phone; that branch passed HyperFrames check and four review snapshots. The delivered page and caption JSON have been restored to `YASH_REPLY=false`.

## Camera motion audit

| Picture visible in film | Camera source range | Motion handling |
| --- | --- | --- |
| Blurred bench behind opening card, 0.000–1.600 | `FOOTAGE:Video/normalpart1.mp4` 0.000–1.600 | Plays under the near-opaque card. |
| Bench full frame, 1.600–5.900 | `FOOTAGE:Video/normalpart1.mp4` 0.000–4.300 | Plays at real speed. |
| Bench split-in and send, 5.900–12.430 | `FOOTAGE:Video/normalpart1.mp4` 4.300–10.830 | Plays at real speed; the panel slides out during source 10.330–10.830. |
| Walk, 18.780–24.780 | `FOOTAGE:Video/normalpart2.mp4` 25.50–28.00, 40.00–191.00, 199.00–202.15 | Existing ramp, displayed continuously for 6 s; final frame becomes the overhead texture. |
| Yash full shot, 29.780–32.430 | `FOOTAGE:Video/normalpart6.mp4` 0.000–2.650 | Plays at real speed. |
| Yash split, 32.430–36.880 | `FOOTAGE:Video/normalpart6.mp4` 2.650–7.100 | Plays at real speed; the panel slides out during source 6.600–7.100. |
| Optional reply only, 43.530–49.077 | `FOOTAGE:Video/normalpart6.mp4` 7.100–12.647 | Plays at real speed; exits during source 12.147–12.647. |

No live camera picture is held. `results/F0004/motion_check.txt` compares adjacent frames in the 540p movie; every sampled live range changed. The overhead uses extracted still textures by design, after the live walk has ended.

## Outputs and checks

- `results/F0004/preview/` has twelve 960 × 540 JPG review stills and `scene2_v3a_540.mp4` (44.167 s, H.264/AAC, 5.0 MB).
- `results/F0004/captions_check.txt` confirms seven default captions, including two for the TTS line.
- `RENDERS:scene2/v3a/scene2_dialogue_sfx.wav` and `RENDERS:scene2/v3a/scene2_music.wav` are the separate stems; the music stem is silent for the film-wide music bed. `RENDERS:scene2/v3a/scene2_picture_540.mp4` is the silent preview picture.
- `hyperframes.cmd check` passed for both default and `YASH_REPLY=true`; the default branch rendered and its movie was inspected at the requested moments and at phone size.

The configured render directory rejected new files in this sandbox, so these `RENDERS:` artifacts are staged under this repo's ignored `local/renders/` for review. The build uses `machine.local.json` by default on a render machine; this local run set `S2A_RENDER_ROOT=local/renders`.

TTS captions use the exact message visible on the recorded app screen; I did not independently listen to the TTS audio to verify every word. The intro card's frame-zero style should be compared with the separate intro composition when it lands for a seamless join.

## Files moved out of git by the listener

- `film/scene2/v3a/assets/walk.mp4` (24.0 MB) was too big for git. Moved to local path: `RENDERS:F0004/film/scene2/v3a/assets/walk.mp4` (inside renders_dir on vivek-pc)
