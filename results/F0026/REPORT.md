---
status: done
---
# F0026: overhead module, strict no-hold

## Made (module only; s2a's build.js untouched)
- **`overhead.js`:** new optional `walkVideo` / `yashVideo` (composition-owned, HyperFrames-timed `<video>` elements). When given, the module adopts the element into its stage and applies the existing transforms, opacity and clip to it instead of to an `<img>`:
  - the walk keeps playing while it shrinks and tilts into the ground (t 0-0.88)
  - Yash plays from source 0.0 under the dissolve and push (t 4.02-5.0), so the last module frame is his live frame at source ~0.95 s

  The still path is kept as the fallback when a video option is absent. API, text and timings are otherwise unchanged. `mount` now needs a video or a still for each.
- **`preview.html`:** two local clips, `walk-tail.mp4` (last 1.2 s of `FOOTAGE:Video/normalpart2.mp4`, playing 0-1.2) and `yash-head.mp4` (`FOOTAGE:Video/normalpart6.mp4` from 0, `data-start` 4.02, duration 0.98), passed as `walkVideo` / `yashVideo`. `const live` switches back to the stills. The clips sit in the ignored `assets/`, made with the ffmpeg lines in the README; `build.py` was outside `writes:`.
- **`README.md`:** the options, and exactly what F0027 must change in s2a:
  - a moving walk video during overhead t 0-0.88
  - a Yash `<video>` at `overhead.start + 4.02` (today film 28.80), media-start 0, 0.98 s
  - `yashFullVideo` media-start 0 → 0.98, `yEarly` 2.65 → 3.63, and the other Yash source windows +0.98
  - his speech `yAt` and the "It's too hot here." caption moved 0.98 s earlier on the film timeline (caption `+1.31/+2.85` → `+0.33/+1.87`)
  - no speed changes

## Test (snapshot stills only)
- `hyperframes.cmd check` passed with the live clips.
- Stills at 0.2, 0.6, 4.3 and 4.97 s are in `results/F0026/preview/`, saved as 960 px JPGs to keep camera frames small in git.
- **Motion evidence.** Mean absolute difference, grey levels out of 255, at 480 px:

  | Time | Live vs old still path, same time | Source clip, adjacent frames at that moment |
  |---|---|---|
  | 0.2 s | 32.1 | 15.3 (walk) |
  | 0.6 s | 2.0 (walk is small and fading) | 13.4 (walk) |
  | 4.3 s | 3.0 (Yash at low opacity under the dissolve) | 2.2 (Yash, source 0.28) |
  | 4.97 s | 32.6 (Yash mid-gesture, hand to forehead, vs his source-0 pose in the still) | 2.0 (Yash, source 0.9) |

- Adjacent frames of the rendered module also differ (16.3 at 0.2 s, 11.8 at 4.97 s), but that number mixes the module's own scale and tilt animation with the footage motion. The two columns above separate the two.
