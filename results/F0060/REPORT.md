---
status: done
---

# F0060 scene 3 fixes

The scene is **47.467 s** (previous generated timeline: 56.300 s). The prepared Vivek app slot is **14.833 s**. Its five idle cuts remove 6.033 s of source; five 3-frame dissolves reduce the result by another 0.500 s. The remaining 2.300 s change comes from the current narration manifest. No camera or app recording is sped up, zoomed, or cropped.

## What changed

- A solid `#07111c` strip covers the status bar on both phone layers. The real Android SOS notification banner remains visible.
- Both expanding SOS rings stay centred on Vachana. The graphic's active Accept chip is `#34c759` with dark text; Decline and the app recording are unchanged.
- N5 holds the SOS card for 3.9 s. N5a and N5b hold the pulse loop for 2.5 s each, and N6 for 6.29 s (6.3 s at 30 fps). All four durations come from `film/common/narration_v4.json` plus 0.4 s at build time.
- The camera windows, captions, TTS, reply line and Send effect follow the shortened app slot. TTS is complete at 37.613–41.468 s; Vivek's reply begins at 41.940 s; the Send sound begins with the tap at 47.070 s. The audio stem skips N5a/N5b because the manifest marks those lines dropped.

## Vivek app cuts

Source: `RENDERS:scene3/app/vivek_take.mkv`. The prepared uncut slot starts at source 4.750 s. Intervals below are removed; each join has a 3-frame dissolve.

| Screen | Uncut slot in–out (s) | Raw source in–out (s) |
| --- | ---: | ---: |
| Notification before Accept | 1.000–2.200 | 5.750–6.950 |
| Logs list | 3.700–4.500 | 8.450–9.250 |
| SOS message before Play | 5.500–7.200 | 10.250–11.950 |
| Play-audio screen after the full TTS | 11.733–12.267 | 16.483–17.017 |
| Reply text before Send | 17.667–19.467 | 22.417–24.217 |

Accept at source slot 2.600 s, Play at 7.630 s, PTT at 12.760–16.220 s, and Send at 19.770 s are retained. Their new slot times are 1.300, 3.630, 8.127–11.587, and 13.237 s.

## Preview judgments

Every listed PNG is 1920 × 1080; `preview/sheet_480.jpg` uses 480 × 270 thumbnails.

| Still | Would a judge go “oh?” |
| --- | --- |
| `preview/frame-00-at-0.5s.png` — N5 SOS card | No; the card remains readable under the full line. |
| `preview/frame-01-at-8s.png` — Vachana phone | No; the status icons are gone and the app header is intact. |
| `preview/frame-02-at-20.7s.png` — N5a pulse | No; the search clearly begins at Vachana. |
| `preview/frame-03-at-23s.png` — N5b timer | No; both rings remain on Vachana while nearby dots light. |
| `preview/frame-04-at-28s.png` — N6 before acceptance | No; Accept and Decline are both clear. |
| `preview/frame-12-at-28.7s.png` — N6 accepted | No; the green state reads immediately, with dark legible text. |
| `preview/frame-05-at-34.5s.png` — Vivek notification | No; its banner and buttons remain while the status strip is hidden. |
| `preview/frame-06-at-35.2s.png` — Accept tap | No; the tap and notification are fully visible. |
| `preview/frame-07-at-36.4s.png` — Logs | No; the list is stable and its tap is preserved. |
| `preview/frame-08-at-36.95s.png` — SOS message | No; the SOS text is complete and readable. |
| `preview/frame-09-at-37.7s.png` — Play audio | No; the app playback is visible beside the moving camera. |
| `preview/frame-10-at-42.2s.png` — reply | No; his live camera and first reply word remain aligned. |
| `preview/frame-11-at-47.1s.png` — Send tap | No; the Send button is still visible at the cue. |
| `preview/frame-13-at-47.3s.png` — sending feedback | No; the app has advanced to its sending state. |

## Build and render notes

- `python film/scene3/v3/build.py --page-only` completed with `missing: []` and passed its `hyperframes.cmd check` gate. The 14 full-size stills and the 480 px sheet were captured from that composition. `git diff --check` passed.
- The dialogue/effects stem was rebuilt and its event list checked. No full-length video render was made, as requested.
- This worker's sandbox denies writes inside the existing `renders_dir/scene3/`; the build used its writable fallback `RENDERS:F0060/scene3/v3/`. On a machine where `scene3/` is writable, the build continues to use `RENDERS:scene3/v3/`.
- Local generated media: `RENDERS:F0060/scene3/v3/app/vivek_app.mp4`, `RENDERS:F0060/scene3/v3/scene3_dialogue_sfx.wav`, and `RENDERS:F0060/scene3/v3/audio_events.txt`.

## Files moved out of git by the listener

- `film/scene3/v3/assets/vachana.mp4` (22.9 MB) was too big for git. Moved to local path: `RENDERS:F0060/film/scene3/v3/assets/vachana.mp4` (inside renders_dir on vivek-pc)
