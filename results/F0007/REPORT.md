---
status: done
---

## Made

- `film/exploded/`: 1920 × 1080, 30 fps, 17 s HyperFrames composition. Local Three.js draws six transmissive rounded glass layers, the phone and locked packet. The private home image is copied by `build.py` to ignored `assets/home.png`; a neutral dark screen is used when it is absent. All animation is derived from seek time.
- `film/exploded/ticks.py`: six short glass ticks at 4.10, 5.85, 7.60, 9.35, 11.10, and 12.85 s. Local stem: `RENDERS:exploded/ticks.wav` (17 s, 48 kHz mono, peak −18.0 dBFS).
- `results/F0007/preview/frame-00.jpg` through `frame-08.jpg`: 1920 × 1080 stills at 1.0, 3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0, and 16.9 s, respectively. `contact-sheet.jpg` shows all nine. `phone-size/` contains each frame at 480 × 270, and `contact-sheet-480.jpg` shows that check.

## Check

`hyperframes.cmd check` passed across all nine times: zero lint, layout, or motion issues. The bundled Three.js global build produced its deprecation warning. The browser's hardware WebGL probe selected Intel UHD Graphics through ANGLE; a dedicated NVIDIA GPU was not reported.

Final nine-frame snapshot batch: 56.63 s total, including browser startup and contact-sheet creation. Observed PNG save intervals (seconds) were:

| Still time | 1.0 | 3.0 | 5.0 | 7.0 | 9.0 | 11.0 | 13.0 | 15.0 | 16.9 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Interval | 11.27* | 1.46 | 2.69 | 1.64 | 2.10 | 2.51 | 1.95 | 1.46 | 1.67 |

*The first interval includes browser startup. Later intervals are the time between completed frame files; they exclude final contact-sheet processing. The 480 px check shows the active titles and layer structure; the smaller tool lines are fine print at that size.

Python was unavailable on this machine's shell. The local WAV was made with the same synthesis formula as `ticks.py` through Node, then checked as 17.000 s and −18.0 dBFS. `build.py` and `ticks.py` remain ready for a render machine with Python.
