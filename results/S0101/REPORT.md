---
status: done
---

# S0101 — live overhead videos

Wired the overhead module to timed `walkVideo` and `yashVideo` elements in the s2a composition. The walk layer now stops at the overhead start, and the module plays its last 0.88 s while shrinking and tilting it. Yash plays from source 0–0.98 s in the overhead and continues from 0.98 s in his full shot. Removed still fallback references from the composition and stopped generating its two unused camera stills. The `Sped up 26×` label remains on the walk layer only. No clip speed or speech speed changed.

The overhead is **23.900–28.900 s**. The new total duration is **43.274 s**, 0.880 s shorter. Yash's opening caption is **29.230–30.770 s**. The TTS window is **39.330–42.674 s**. `YASH_REPLY` remains false.

The final `end_state` remains `yash_app` at slot time **11.690 s**, on `#0a0d12`, with phone rect **x=735, y=40, width=450, height=1000 px**.

`results/S0101/preview/` contains 960 px stills at overhead t=0.2, 0.6, 4.3 and 4.97 s, the first Yash full-shot frame, the last s2a frame, a 480 px phone sheet, and a 960×540 preview video (4.93 MB). `make_previews.js` reproduces the stills and measurements from the local render.

Adjacent-frame mean absolute differences, grayscale levels out of 255 at 480 px:

| Overhead time | Rendered composition | Live source |
|---|---:|---:|
| 0.20 s | 22.04 | 23.85 (walk) |
| 0.60 s | 19.34 | 8.65 (walk) |
| 4.30 s | 19.48 | 1.88 (Yash) |
| 4.97 s | 2.18 | 1.60 (Yash) |

`node film/scene2/v3a/build.js --preview` completed, including `hyperframes.cmd check`; `node film/scene2/v3a/build.js --page-only`, both Node syntax checks, and `git diff --check` passed. Preview frames and the phone sheet were inspected visually. Local render artifacts: `RENDERS:scene2/v3a/scene2_picture_540.mp4`, `RENDERS:scene2/v3a/scene2_dialogue_sfx.wav`, and `RENDERS:scene2/v3a/scene2_music.wav`.
