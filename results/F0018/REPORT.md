---
status: done
---
# F0018: film v3 assembler + mix + QC

## Made
- **`film/final/v3_segments.json`:** the six segments in film order, each with folder, `render_cmd`, picture, stems (`dx`/`sfx`), segment-time `tts_windows` and `expected_duration`, plus a `status` note saying what each build really writes today:

  | Segment | Today |
  |---|---|
  | intro (`film/intro_v3/`) | Not built yet: the folder doesn't exist. Picture, embedded audio and render command are assumed (`RENDERS:intro_v3/intro_v3.mp4`, embedded dx). |
  | s2a | Only `film/scene2/v3a/overhead/` exists, so outputs are assumed (`RENDERS:scene2/v3a/scene2_v3a.mp4`, embedded dx). The TTS window is the last 3.944-0.6 s of the segment, from v3b's `start_state` derivation. |
  | s2b | `render.cmd` writes one mp4. HyperFrames mixes N2/N3 narration and the sonar sfx into it, with no separate stems, so dx is `embedded`. 32.4 s. |
  | s3 | Picture `scene3_picture.mp4` plus `scene3_dialogue_sfx.wav` as dx (dialogue, TTS, narration and UI/sonar sfx in one file; there is no separate sfx stem). Its own `scene3_music.wav` is listed but not mixed, because the film bed replaces it. The TTS window comes from `audio_events.txt` ("app TTS" line) when it exists; otherwise the fallback is 39.013-42.357. 51.4 s. |
  | exploded | `build.py` only stages assets, so the render command is spelled out. Silent picture plus sfx `ticks.wav`. 17 s. |
  | cards | `render.cmd`, plus sfx `cards_sfx.wav`. 14 s. The closing chord is at segment 8 s. |

- **`film/final/assemble_v3.py`:** the one-command assembly described in the task. Notes on how I built it:
  - **Pictures:** concat by stream copy when every file matches, otherwise one libx264 CRF 18 encode with conform.
  - **Stems:** each segment's stems are trimmed or padded to its picture length, with a warning if a stem runs past the last frame. Speech is never stretched or cut on purpose.
  - **Music cue sheet:** built from the real segment starts. Sections under 6 s are merged for the bed, because a 2 s slate is shorter than the crossfades. Then `make_bed.py` and `duck.py` run.
  - **Bed trim:** the bed is trimmed to keep MIX.md's distance to dialogue (dialogue measured against -18 LUFS, clamped ±10 dB, `--bed-trim-db` overrides).
  - **Master:** -16 LUFS with a linear gain, plus a limiter only if the true peak needs it (TP target -1.8 for AAC margin). The encoded film is verified at -16 ±0.5 LUFS and <= -1.5 dBTP.
  - **Mux:** AAC 256 kbps, 48 kHz stereo. Frame count and A/V length are checked.
  - **Outputs:** the film, the no-music version, stems carrying the master gain, a report JSON; then QC.
  - **`--draft`:** 2 s slates (dark field with "MISSING SEGMENT: name"), a faster encode, `_draft` on every name.
  - **Other options:** `--renders-dir`, `--reuse-bed`, `--no-qc`.
- **`film/final/qc.py`:** the old behaviour is unchanged (checked on a test film). The freeze threshold is now a parameter (default 1 s, as before). The new `--v3` mode adds:
  - **freezes >= 0.5 s**, each with film time, segment and segment time. REVIEW in camera segments, INFO in exploded, cards and slates.
  - black >= 1 s FAIL, except the final fade
  - loudness and true peak, full-scale samples
  - silence > 1.5 s: FAIL, except INFO in cards and slates
  - A/V alignment and length against the assembly report
  - a contact sheet: frames at exactly 0, 5, 10 s… with time labels, plus a 960 px copy
  - status PASS / REVIEW / FAIL (exit 1 on FAIL)
- **`film/final/README_v3.md`:** the lead's commands: render each segment, assemble, QC, and what to do when something fails.

## Tests (this laptop; short ffmpeg jobs only)
- **Draft, real clone:** `python film/final/assemble_v3.py --draft`. No v3 segment is rendered on this machine, so all six segments became slates; the real `cards_sfx.wav` was used, trimmed to the slate.
  - It ran end to end in about 21 s: 12.0 s, 360 frames, `full_film_v3_draft.mp4`, -16.0 LUFS, -3.2 dBTP.
  - QC: PASS, with slate holds as INFO.
  - Files: `draft_assembly_report.json`, `draft_qc.json`, `draft_contact_960.jpg`.
- **Fixture (non-draft path, test files in `local/tmp/`, not committed):** six 10 s test-pattern segments in a separate renders folder, using a copy of the segments file with 10 s lengths. Setup:
  - speech-like embedded audio in intro, s2a and s2b
  - a separate, 0.3 s too long dx WAV plus an `audio_events.txt` TTS line in s3
  - a tick sfx in exploded; the real cards sfx
  - a deliberate 1 s frozen hold in s2a

  Results:
  - stream-copy concat, 1800 frames
  - the TTS windows reached the film cue sheet (s2a 16.056-19.4, from its negative window; s3 36.2-38.9, from the events file)
  - the closing chord was placed
  - the bed was ducked: music is about 12 dB lower under speech than in the no-dialogue section, and about 3 dB lower again inside the TTS window
  - the encoded film measured -16.01 LUFS, -3.9 dBTP
  - QC REVIEW, with exactly one row: "freeze >= 0.5 s in s2a, film 14.00-15.07 = s2a 4.00-5.07 s", the planted freeze
  - both over-long-stem warnings fired

  Files: `fixture_assembly_report.json`, `fixture_qc.json`, `fixture_contact_960.jpg`.

## For the lead
- Exact commands: `film/final/README_v3.md`. The short form is to render the segments, then run `python film/final/assemble_v3.py` on utkarsh-pc.
- Before the real run, fix the intro and s2a entries in `v3_segments.json` once those builds exist (output name, stems, lengths), and check the s2a TTS window.
- Deviation from the task text: the film-level cue sheet goes to `RENDERS:full_film_v3_work/cues_film.json`, not `film/music/cues.json`. `film/music/` is not in this task's `writes:`, and rewriting a committed file on every assembly would leave the render clone dirty. `make_bed.py` and `duck.py` take `--cues`, so the result is the same.
- The render machine needs numpy and scipy for the bed and ducking (the same need as scene 3's build). In a non-draft run a bed failure stops the assembly; in draft mode it continues without music.
