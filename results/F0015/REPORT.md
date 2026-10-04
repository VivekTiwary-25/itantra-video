---
status: done
---

# F0015 — Scene 3 v3 fixes

- The join card uses `.glass-card.full.sos` with the exact SOS title, including during shrink.
- Vivek's centred phone eases to 1.9× over 0.6 s for the banner and Accept, stays enlarged through the recorded acceptance, then eases out. A brief outline marks the recorded Accept button as the screen changes. His reply text gets a separate 1.6× punch before Send. App playback and scene timing are unchanged.
- Captions move to a fixed position beside the centred phone; the current glass kit supplies the 42 px tech lines and 46 px captions.
- Rebuilt `film/scene3/v3/index.html` and made 15 stills plus `results/F0015/preview/phone-review.jpg` (480 px wide per frame). The requested `07b-banner-punch.jpg` and `08-accept-tap.jpg` are included. At that size, the SOS title, three tech lines, captions, banner, Accept and reply text are legible; no tech line wraps or clips.

`hyperframes.cmd check` passed: zero errors and warnings in lint, runtime, layout and motion; contrast 2/2. The two informational camera-overflow notices are the existing intentional crop in split shots. `git diff --check` passed.

This sandbox could not launch the machine's Python executable, so `build.py --page-only` was unavailable here. `results/F0015/build_local.mjs` rebuilt the page from the existing timeline and layers, using the same local media and glass files; the Python builder remains the cross-machine production build. Preview sonar media came from the existing local cache, so a production render still needs the normal Python/SciPy path. The graded camera plate over 20 MB stays local at `RENDERS:scene3/v3/plates/vachana.mp4`.

## Files moved out of git by the listener

- `film/scene3/v3/assets/vachana.mp4` (22.9 MB) was too big for git. Moved to local path: `RENDERS:F0015/film/scene3/v3/assets/vachana.mp4` (inside renders_dir on yash-pc)
