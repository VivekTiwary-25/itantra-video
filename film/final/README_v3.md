# Film v3: render, assemble, QC (for the lead, on a render machine)

Run everything from the repository root of the render machine's clone (utkarsh-pc first, then yash-pc, then vivek-pc; never yojitth-pc). Paths come from that clone's `machine.local.json` (`renders_dir`, `footage_root`). `film/final/v3_segments.json` lists what each segment produces and how long it must be. Update it when a segment's output or length changes; `expected_duration: null` accepts any length with a warning.

## 1. Render the segments (film order)
| # | Segment | Command | Picture | Audio taken from |
|---|---|---|---|---|
| 1 | intro | `python film/intro_v3/build.py --render` (not built yet: confirm the real command and output, then fix the json) | `RENDERS:intro_v3/intro_v3.mp4` | its embedded track |
| 2 | s2a | `node film/scene2/v3a/build.js --render` | `RENDERS:scene2/v3a/scene2_picture.mp4` (44.154 s) | `RENDERS:scene2/v3a/scene2_dialogue_sfx.wav`; TTS window from its `audio_events.txt` |
| 3 | s2b | `film\scene2\v3b\render.cmd` | `RENDERS:scene2/v3b/scene2_v3b.mp4` (32.4 s) | embedded (narration + sonar sfx) |
| 4 | s3 | `python film/scene3/v3/build.py` | `RENDERS:scene3/v3/scene3_picture.mp4` (51.4 s) | `RENDERS:scene3/v3/scene3_dialogue_sfx.wav` (no scene music since F0024) |
| 5 | exploded | `python film/exploded/build.py && python film/exploded/ticks.py && hyperframes.cmd render film/exploded -q high -f 30 -o <renders_dir>\exploded\exploded.mp4` | `RENDERS:exploded/exploded.mp4` (17 s) | sfx `RENDERS:exploded/ticks.wav` |
| 6 | cards | `python film/cards_v3/cards_sfx.py && film\cards_v3\render.cmd` | `RENDERS:cards_v3/cards_v3.mp4` (14 s) | sfx `RENDERS:cards_v3/cards_sfx.wav` |

Pictures must be 1920x1080 at 30 fps.

## 2. Assemble (also runs QC)
```
python film/final/assemble_v3.py
```

**What it does:**
- Checks every file and length. A missing file stops the run, with the list.
- Concatenates the pictures: stream copy if they all match, otherwise one libx264 CRF 18 encode.
- Lays out the dx and sfx stems on the film timeline.
- Writes the film-level music cue sheet to `RENDERS:full_film_v3_work/cues_film.json`, using the real segment starts and the TTS windows in film time. s3's windows come from `audio_events.txt` when it exists.
- Runs `film/music/make_bed.py` (about 1.5 min) and `film/music/duck.py`.
- Trims the bed so it keeps MIX.md's distance to the dialogue. Bed levels assume dialogue at -18 LUFS; the trim is clamped to ±10 dB, and `--bed-trim-db N` overrides it.
- Masters to -16 LUFS integrated, true peak <= -1.5 dBTP, and muxes AAC 256 kbps.

**Outputs:**
- `RENDERS:full_film_v3.mp4` (with music)
- `RENDERS:full_film_v3_nomusic.mp4`
- `RENDERS:full_film_v3_stems/{dx,sfx,music}.wav`. These carry the master gain, so dx + sfx + music add up to the mix before any limiting.
- `RENDERS:full_film_v3_report.json`: segment starts and lengths, music cue sheet, bed trim, loudness of every stage, warnings.
- `RENDERS:full_film_v3_qc.json` and `RENDERS:full_film_v3_contact.jpg` (plus `_960.jpg`).

**Options:**
- `--draft`: 2 s slates for missing segments, a faster encode, and every output name gets `_draft`, so a draft never replaces a real film. Use it to check the pipeline before every segment exists.
- `--reuse-bed`: skips re-rendering the bed when only the picture changed and the cue sheet did not.
- `--no-qc`: skips QC.

The committed `film/music/cues.json` is only read, for section loudness targets, key and duck settings.

## 3. QC (on its own, e.g. after a manual fix)
```
python film/final/qc.py --v3 <renders_dir>\full_film_v3.mp4 --segments-report <renders_dir>\full_film_v3_report.json --report <renders_dir>\full_film_v3_qc.json --contact <renders_dir>\full_film_v3_contact.jpg
```

**What it checks:**
- format, A/V alignment, length against the assembly report
- **every freeze >= 0.5 s**, with the segment and segment time. REVIEW in camera segments, because the film rule is that live camera never freezes, so check each one. INFO in exploded, cards and slates.
- black frames >= 1 s (the final fade to black is allowed)
- loudness -16 ±1 LUFS, true peak <= -1.5 dBTP, full-scale samples
- silence > 1.5 s: FAIL, except INFO in cards and slates
- a contact sheet with one frame every 5 s, labelled with the film time

Exit code 1 on FAIL. A REVIEW status still exits 0, so read the freeze rows. `python film/final/qc.py VIDEO` (no `--v3`) keeps the old v2 checks.

## If something fails
| Message | Fix |
|---|---|
| "missing inputs" | Render that segment, or fix its path in `v3_segments.json`. |
| "picture is N s, expected M s" | The segment changed length. Re-check its joins, then update `expected_duration`. |
| "stem is longer than the picture" | The tail after the last frame is dropped. Listen that it holds no speech (speech is never cut or stretched on purpose). |
| Encoded film misses -16 LUFS / -1.5 dBTP | Look at `loudness` in the report. A very dynamic mix uses the limiter path (`master_method`). |

## 4. Beat stills (after every assembly, before a render is accepted)
```
python film/final/beat_stills.py                                   # default: RENDERS:full_film_v3_draft.mp4 + its _report.json
python film/final/beat_stills.py --film RENDERS:full_film_v3.mp4    # the final
python film/final/beat_stills.py --beats-only                      # print the beat table only
python film/final/beat_stills.py --film RENDERS:full_film_v3.mp4 --report RENDERS:full_film_v3_report.json --out RENDERS:review/final_check
```
- **Inputs:** segment starts come from the assembly report. Beats come from each segment's own `timeline.json` (folder from `v3_segments.json`):
  - `segments` lists (s2a, s2b, s3) give the middle of each segment
  - `tech_lines` / `techlines` and `labels` (exploded_v2) give their middles
  - the intro's word cues give a moment 0.4 s after each cue
  - cards uses built-in beats
  - every segment also gets its first and last frame, for the joins
- **Slates:** draft slates get first/last frames only.
- **Output:** `RENDERS:review/<film name>/` (`--out` to change), printed at the end:
  - `frames/` (full-size JPGs)
  - `beats_full.jpg` (960 px tiles)
  - `beats_phone.jpg` (480 px tiles, how a judge on a phone sees it)
  - `joins.jpg` (each segment's last frame next to the next segment's first frame)
  - `beats.json`
- **Review:** look at every tile at both sizes. In `joins.jpg`, check that each cut flows as intended; the tool places the exact last and first frames side by side.
- Frame extraction decodes the film once and selects the requested frame numbers, so the join images are frame-accurate. A missing timeline or a report/film frame-count mismatch stops the run.
- Needs ffmpeg and Pillow. Takes about 20 s for a 2:35 film.
