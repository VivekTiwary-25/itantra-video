---
status: done
---

# F0062r1 intro fixes

Continued the F0062 intro. The camera overlap is a 0.35 s cross-dissolve from 6.667 to 7.017 s, inside Vachana's pause; the dialogue and captions keep their original timing. The opening name/team/PS card and the fixed phone panel are the same glass element, which resizes and cross-fades its contents. Both phone mockups now cover the Android status strip with solid app background colour `#07111c`. The build uses the lead's cleaned private screenshot when present and a local private fallback when it is absent.

The production composition is in `film/intro_v3/`. Twelve 1920 × 1080 stills and `preview/contact-sheet-480.jpg` (each tile 480 px wide) are here. No full-length render was made.

| Still | Would a judge go “oh”? |
| --- | --- |
| `preview/frame-00-at-3s.png` | Yes: the opening identifies Vachana, her team, and the problem statement clearly. |
| `preview/frame-01-at-6.48s.png` | Yes: the name card remains readable as the transition begins. |
| `preview/frame-02-at-6.6s.png` | Yes: the panel starts growing without a visual swap. |
| `preview/frame-03-at-6.72s.png` | Yes: the camera dissolve falls in the pause while the card stays anchored. |
| `preview/frame-04-at-6.842s.png` | Yes: the camera overlap and the in-place panel morph are both visible. |
| `preview/frame-05-at-7s.png` | Yes: the old camera view clears as the phone takes over the same panel. |
| `preview/frame-06-at-7.25s.png` | Yes: the name content fades while the phone grows, with no second panel. |
| `preview/frame-07-at-7.5s.png` | Yes: the phone is fully established and its Android status icons are hidden. |
| `preview/frame-08-at-9s.png` | Yes: the first network badge reads beside the clean phone screen. |
| `preview/frame-09-at-17s.png` | Yes: the waveform and clean phone screen support the speech-to-text explanation. |
| `preview/frame-10-at-22.8s.png` | Yes: both clean phone screens and the gold Bluetooth symbol make the transfer legible. |
| `preview/frame-11-at-27.8s.png` | Yes: the second phone's sound waves complete the explanation. |

Validation: `hyperframes.cmd snapshot` captured all 12 stills. `hyperframes.cmd check film/intro_v3` passed with 0 lint, runtime, layout, and motion warnings; 8/8 contrast checks passed. It reported one informational 2.25 px overflow on the existing opening panel. `git diff --check` passed. This machine has no callable Python executable, so the updated `build.py` was not rerun here; the checked `index.html` has the matching composition change, and the current ignored voice asset was refreshed from `RENDERS:intro_v4/voice.wav` before the final check.

## Files moved out of git by the listener

- `film/intro_v3/assets/explain.mp4` (30.0 MB) was too big for git. Moved to local path: `RENDERS:F0062r1/film/intro_v3/assets/explain.mp4` (inside renders_dir on yash-pc)
