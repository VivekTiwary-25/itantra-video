---
status: done
---

Built the v3 frosted-glass kit in `film/common/glass/`: shared CSS tokens and six components, deterministic `Glass.phone`, nine inline line icons, `Glass.cross`, a 256×256 grain tile, usage README, and a four-second HyperFrames demo. Added `brief/style.md` with the shared look, text placement, colour meanings, and the no-frozen-frames rule.

Preview files: `preview/01-card.jpg`, `02-panel.jpg`, `03-circle.jpg`, `04-phone-icons.jpg`, `05-full-card.jpg` (all 1920×1080), and `preview/contact-960.jpg`. The moving demo footage starts at `FOOTAGE:Video/normalpart1.mp4` source 2.0 s and `FOOTAGE:Video/vachna part1.mp4` source 2.0 s. Demo MP4 derivatives are ignored and stay local; the phone uses an abstract blank screen solely to inspect the shell.

Checked the 960 px contact sheet at its native size, where each preview is 480 px wide. The card title and panel primary and secondary lines remain readable against the daylight shots; the tech line, caption, pins, phone shell, and two crossed icons are visible. The card and panel sit clear of the main speaker. `hyperframes.cmd check` passed with 0 lint/runtime/layout/motion warnings or errors and 18/18 text contrast checks passing.

To rebuild locally: run `python film/common/glass/make_noise.py`, `python film/common/glass/demo/build.py`, then `hyperframes.cmd check` in `film/common/glass/demo/`. Copy only `glass.css`, `glass.js`, and `noise.png` to each final composition's `assets/glass/`.
