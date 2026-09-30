---
status: done
---

# S0004 — closing title card, option A

Built `film/title/` as a 1920×1080, 30 fps, 20.0 s HyperFrames composition. Its text follows the approved six lines exactly. `build.py` contains the single `DISTANCE = "~400 m"` setting and writes `index.html` from `index.html.tpl`. `make_sfx.py` writes a deterministic, very quiet 48 kHz stereo tick stem to `assets/title_sfx.wav`; the composition includes it as a timed audio element. GSAP is copied from `film/vendor/gsap/` and loaded locally.

| Line | Start |
|---|---:|
| 1 — We built iTantra… | 0.6 s |
| 2 — Speak in any of 10 languages… | 4.0 s |
| 3 — It travels phone to phone… | 7.4 s |
| 4 — No towers… | 10.8 s |
| 5 — iTantra. Speak. Send. Be heard. | 14.5 s |
| 6 — Team chmod 777 · Team ID 148903 · NIE Mysuru | 14.5 s |

Lines 1–4 clear away before the next line, so the long statements have the whole centre of the frame. The identity and team line fade in together; that final state holds for more than 4 seconds. One 960×540 JPG per line is in `results/S0004/preview/`. `line-06-640.jpg` verifies the small team line remains readable at 640×360.

`hyperframes.cmd check` passed: 0 lint errors or warnings, 0 runtime errors, 0 layout issues, 0 motion issues, and 7/7 contrast checks. Six HyperFrames snapshots were visually inspected. The locally generated audio stem peaks at −39.5 dBFS.

Python is unavailable on this worker, so `index.html` and the ignored WAV were generated locally from the same parameters without running the Python scripts. Run `python film/title/build.py` and `python film/title/make_sfx.py` on the render machine before the final render.

`preview/title_preview.mp4` is a 960×540, 20.0 s, 30 fps **still based timing preview** with the tick stem, under 1 MB. A direct HyperFrames MP4 render was attempted, but the sandbox prevented Chrome from starting. The stills and successful check verify the actual HyperFrames composition; the MP4 preview does not show its in-between fade and rise animation.
