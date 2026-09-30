---
status: done
---

# T0016 — Scene 3 assembly

## Made

- `film/scene3/main/build.py`, `index.html.tpl`, generated `index.html`, `timeline.json`, `slots.json`, and `prep_slot.py` form a reproducible 1920×1080, 30 fps HyperFrames composition. The app uses the centred portrait layout from scene 2. Camera plates use `GRADE_V1`; app recordings are never graded.
- `RENDERS:scene3/scene3_draft.mp4` is the 60.2-second first cut with music, 1,806 frames. It includes the three delivered SOS sonar segments. Its encoded audio measures −16.5 LUFS integrated and −1.9 dB true peak.
- `RENDERS:scene3/scene3_dialogue_sfx.wav` and `RENDERS:scene3/scene3_music.wav` are separate, full-length, time-aligned 48 kHz mono layers. Music is silent outside 18.1–30.6 s. The draft is mastered from their sum; master the two layers together again during final assembly.
- `RENDERS:scene2/scene2_dialogue_sfx.wav` and `RENDERS:scene2/scene2_music.wav` expose the existing scene 2 mix as two full-length layers. `film/scene2/main/build.py` now reproduces them. Scene 2's picture was not changed. Its music layer is silent outside its sonar section.
- Eight 960 px review stills are in `results/T0016/preview/`. `hyperframes check` passed with no errors; its layout warnings are the intentionally oversized blurred side layers.

## Timeline

| Segment | Scene start | Scene end | Source / action |
|---|---:|---:|---|
| `s3_open` | 0.0 | 4.1 | `FOOTAGE:Video/sospart1.mp4` src 0–4.1; N5 at 0.3 |
| `vachana_sos` | 4.1 | 18.1 | App slot; clean SOS line at slot + `listen_at` |
| `sos_in` | 18.1 | 20.1 | Delivered SOS transition, 2.0 s |
| `sos_sonar` | 20.1 | 29.1 | Delivered red sonar, 9.0 s; N6 at 21.1 |
| `sos_dive` | 29.1 | 30.6 | Delivered dive, 1.5 s |
| `lab_a` | 30.6 | 32.2 | `FOOTAGE:Video/sospart2.mp4` src 3.0–4.6; notification tone at 30.7 |
| `vivek_sos` | 32.2 | 44.2 | App slot |
| `lab_b` | 44.2 | 47.7 | `FOOTAGE:Video/sospart2.mp4` from src 7.3; final ~0.1 s holds the last frame because the source ends at 10.70 s |
| `vivek_reply` | 47.7 | 52.7 | App slot |
| `vachana_response` | 52.7 | 59.7 | App slot |
| `end_hold` | 59.7 | 60.2 | Last app frame |

N5 and N6 were present and mixed from `RENDERS:scene3/narration/david/N5.wav` and `N6.wav`. The clean SOS line from `FOOTAGE:Audio/sospart1.mp3` starts at scene 4.271 s (`listen_at: 0.171`); the lab line from `FOOTAGE:Audio/sospart2.mp3` starts at scene 44.505 s. Both use the scene 1 RNNoise/voice chain and approximately −16 LUFS per line.

## Sync check

I compared 300–3400 Hz speech-energy envelopes in short sliding windows against each camera track, searching ±0.6 s around the supplied offsets at 10 ms steps. For `sospart1`, the first 0–1.2 s of clean audio peaks at **+4.681 s** (correlation 0.532), while the next three windows peak at **+4.271 s** (0.894, 0.902, 0.874). The lead's +4.271 s anchor was retained; review the first phrase's mouth sync before final use. For `sospart2`, the four windows peak at **+0.075, +0.065, +0.065, +0.075 s** (correlations 0.830, 0.623, 0.786, 0.928), supporting the specified +0.065 s anchor.

## Swapping inputs

Place portrait recordings at the `RENDERS:` paths in `film/scene3/main/slots.json`, or change those paths to other locations relative to `local/renders/`. Keep the listed durations to preserve the cut. `python film/scene3/main/prep_slot.py <slot> <source> --in <seconds> --audio keep` prepares a source recording under `local/renders/` into its slot file; use `--audio drop` for silent sources. For `vachana_sos`, set `listen_at` to the point in the prepared recording where her clean line should start. Its recorded mic sound is suppressed during the clean line; other app audio remains in the dialogue layer. Then run `python film/scene3/main/build.py`.

The four app recordings were absent for this draft, so marked `APP:` cards appear in their slots. The sonar package arrived during the final build; all three real segments and their separate SFX/music stems are in the draft. The `sos_in` composition still shows its own temporary app-last-frame card until `RENDERS:scene3/app/vachana_sos_last.png` is supplied. The build picks up later replacements on rerun. The draft contains no relay chain, packet, or blue relay points.
