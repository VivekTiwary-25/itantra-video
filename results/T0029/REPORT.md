---
status: done
---

# Scene 2 final pass

## Made

- Changed the bench push-in endpoint to 1.8×. Its 0.5 s dissolve into the app runs from scene 7.700 to 8.200.
- Applied the confirmed normalpart6 clean-audio offset of -0.37050 s. The camera in-point remains source 0; the opening “Oh” begins 0.37050 s before Yash appears, over the end of the maps segment, so the word is retained.
- Prepared four real app slots with `prep_slot.py` and no grade:
  - `vachana_send`: source 1.55–14.683 s; status bar cropped; recording audio dropped. The PTT down/up and Send taps are at slot 0.08/5.24/11.98 s.
  - `yash_receive`: `yash_take` source 5.60–17.833 s; status bar kept; recording audio dropped. The notification appears near source 7.8 s, and `RENDERS:tts_itantra/tts_msg.wav` starts at source 13.55 s, 0.15 s after `tap_play`, normalized to dialogue level.
  - `yash_reply`: `yash_take` source 21.08–26.58 s; status bar cropped; recording audio dropped. The “Sent to Vachana” confirmation is visible before the cut, and the cut precedes the unrelated banner.
  - `vachana_reply`: source 7–14 s; status bar cropped; recording audio dropped. Ordinary phone use, the reply notification, Logs, and the opened message are visible.
- Used T0024 option 1, `message_a.wav`, at the Yash notification around scene 38.800 s.
- Rebuilt the composition and both stereo mixes. `build.py` ran `hyperframes.cmd check` successfully. Both drafts are 1920×1080, 30 fps, 3,075 frames, 102.500 s. The separate audio layers were also rendered.

Outputs: `RENDERS:scene2/scene2_draft_music.mp4`, `RENDERS:scene2/scene2_draft_nomusic.mp4`, `RENDERS:scene2/scene2_dialogue_sfx.wav`, `RENDERS:scene2/scene2_music.wav`. Prepared slots are under `RENDERS:scene2/app/`.

## Timeline

| Segment | Start | End |
|---|---:|---:|
| Doorway | 0.000 | 3.000 |
| Bench | 3.000 | 7.700 |
| `vachana_send` | 7.700 | 20.833 |
| Send freeze; N1 at 21.033 | 20.833 | 24.433 |
| Walk | 24.433 | 30.433 |
| `maps` fallback | 30.433 | 33.933 |
| Yash before notification | 33.933 | 36.600 |
| `yash_receive` | 36.600 | 48.833 |
| Yash after notification | 48.833 | 55.900 |
| `yash_reply` | 55.900 | 61.400 |
| `sonar_a`; N2 at 61.400 | 61.400 | 68.400 |
| `relay_1` | 68.400 | 74.400 |
| `relay_2` | 74.400 | 80.400 |
| `relay_3` | 80.400 | 86.400 |
| `sonar_b`; N3 at 90.400 | 86.400 | 92.400 |
| Sonar fade; N4 at 92.700 | 92.400 | 95.000 |
| `vachana_reply` | 95.000 | 102.000 |
| Final hold | 102.000 | 102.500 |

`vachana_send`, `yash_receive`, `yash_reply`, and `vachana_reply` use real recordings. `maps.mkv` was unavailable; `maps` retains the existing `RENDERS:scene2/app/maps_fallback.mp4` placeholder visual. No text placeholder card remains.

## QC

`film/final/qc.py` ran on both final drafts. Full results: `results/T0029/qc_music.json` and `results/T0029/qc_nomusic.json`. Both returned **FAIL** for audio silence longer than 1.5 s and 10 s short-term level outliers. The longest silent stretch is scene 94.642–102.507 s across the return leg; other app actions also have long silent stretches. The music version's final 100–110 s window is the outlier; the no-music version also flags 70–80 s. These audio gaps need an editorial sound pass. The scene keeps music confined to the two sonar sections.

Both drafts passed QC checks for format, dimensions, 30 fps constant timing, stereo AAC, matched stream durations, no long black frames, no detected text placeholder card, no clipping, and channel balance. Integrated loudness is -16.24 LUFS with music and -16.03 LUFS without; true peaks are -4.75 and -4.77 dBTP. Visual spot checks confirmed the Yash notification, TTS screen, sent confirmation, and Vachana return flow. `hyperframes.cmd check` reported only its existing duplicate-media warning and intentional side-layer overflow notes.

## Files moved out of git by the listener

- `film/scene2/main/assets/walk.mp4` (29.7 MB) was too big for git. Moved to local path: `RENDERS:T0029/film/scene2/main/assets/walk.mp4` (inside renders_dir on vivek-pc)
