---
status: done
---
# F0024: F0019 findings applied (outside s2a)

## Final segment table (`film/final/v3_segments.json`)
| Segment | Render command | Picture | Stems | Expected |
|---|---|---|---|---|
| intro | TODO: F0023 has not landed; set from its REPORT | (assumed) `RENDERS:intro_v3/intro_v3.mp4` | dx embedded (assumed) | null (any length, warns) |
| s2a | `node film/scene2/v3a/build.js --render` | `RENDERS:scene2/v3a/scene2_picture.mp4` | dx `RENDERS:scene2/v3a/scene2_dialogue_sfx.wav`; TTS from `RENDERS:scene2/v3a/audio_events.txt` (fallback 40.21-43.554) | 44.154 s |
| s2b | `film\scene2\v3b\render.cmd` | `RENDERS:scene2/v3b/scene2_v3b.mp4` | dx embedded (N2/N3 + sonar sfx) | 32.4 s |
| s3 | `python film/scene3/v3/build.py` | `RENDERS:scene3/v3/scene3_picture.mp4` | dx `RENDERS:scene3/v3/scene3_dialogue_sfx.wav`; TTS from `RENDERS:scene3/v3/audio_events.txt` (fallback 39.013-42.357) | 51.4 s |
| exploded | `python film/exploded/build.py && python film/exploded/ticks.py && hyperframes.cmd render film/exploded -q high -f 30 -o <renders_dir>/exploded/exploded.mp4` | `RENDERS:exploded/exploded.mp4` | sfx `RENDERS:exploded/ticks.wav` | 17 s |
| cards | `python film/cards_v3/cards_sfx.py && film\cards_v3\render.cmd` | `RENDERS:cards_v3/cards_v3.mp4` | sfx `RENDERS:cards_v3/cards_sfx.wav` | 14 s |

## Changes
1. **Assembler** (`film/final/assemble_v3.py`): the events-log parser now accepts s2a's `TTS` label as well as s3's `app TTS …`. It drops the `next: …` note that s3's log adds to other rows: a plain match on "TTS" would have picked up a dialogue line. Checked on both log formats.
   - `README_v3.md`: the s2a and s3 rows are updated, and it says to render s2a before s2b.
2. **s2b** (`film/scene2/v3b/build.js`): new `joinFromS2a()`.
   - It reads `film/scene2/v3a/timeline.json` `end_state` and refuses the build unless the slot is `yash_app` and the phone rect (x, y, width, height within 0.5 px) and background match s2b's own (450×1000 at 735,40, `#0a0d12`).
   - It uses `slot_time + 1/30` (today 11.69 → 11.7233) for the still and for the `yashSlot` video's `data-media-start`, which it writes into `index.html` at build time. The template is outside `writes:`, so its hard-coded 11.724 is replaced on the way to the page. If the replacement fails, the build stops.
   - The value is also stored in the page's timeline (`start_state.slot_time` and `derivation`).
3. **s3 join tint** (`film/scene3/v3/index.html.tpl:12-14`): both sides already use `.glass-card.full.sos` (F0015/F0017), but the backgrounds still differed: s3 frame 0 was about 6 code values greener and 5 less red than s2b's last frame.
   - Fix: s3's `.card-red` now uses s2b's own red radial (`#redTint` gradient) at 0.68, and `.card-footage` is dimmed to brightness .22, saturate .2. `.card-footage` is only behind the full card in `card_out`, so the reveal is unaffected.
   - Measured on full-size test pages that rebuild both join frames from the real sources (local `sonar_b` render last frame, `sospart1` frame 0, current glass kit): mean absolute difference 1.7/255. Whole-frame means: s2b (32.6, 23.8, 31.8) vs s3 (33.1, 26.3, 33.7).
4. **s3 music** (`film/scene3/v3/build.py`): `sos_music` is no longer loaded or placed. `scene3_music.wav` and `scene3_mix.wav` are no longer written. `mux()` now muxes `scene3_dialogue_sfx.wav` into `scene3_v3.mp4`.

## Checks
- **Syntax:** `node --check` on s2b's `build.js` and `py_compile` on s3's `build.py` and the assembler both pass. `joinFromS2a()` was run against the real timelines: 11.7233, geometry OK.
- **Draft assembly:** `assemble_v3.py --draft` ran end to end (all slates here; QC PASS).
- **Fixture run (non-draft, 10 s test segments under `local/tmp`):** the new s2a paths, the s2a `TTS` window (16.5-19.4 film s) and the s3 window (36.2-38.9) all reached the film cue sheet. -16.02 LUFS, -3.8 dBTP.
- **Not run:** `hyperframes.cmd check` for s2b and s3. Their builds need staged media that isn't on this laptop (s3 app slots and sonar cache; s2b sonar renders under `RENDERS:scene2/sonar`). The s3 template change is CSS only; the next normal build runs check.
