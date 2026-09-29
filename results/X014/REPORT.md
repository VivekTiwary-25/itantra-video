---
status: done
---

# X014 report

Created a 1920×1080, three-second HyperFrames composition in `project/` using the local `gsap.min.js`. The centered `iTantra` title fades in over a `#0a0a0a` background. No URL is used in `index.html`.

Commands run (with `HYPERFRAMES_NO_TELEMETRY=1` and `HYPERFRAMES_SKIP_SKILLS=1` set for every HyperFrames command):

1. `hyperframes.cmd init project --non-interactive --skip-transcribe` from `results/X014/`.
2. `hyperframes.cmd check` from `results/X014/project/` — passed with 0 errors, 0 warnings, 0 layout issues, and 4/4 contrast checks passing.
3. `hyperframes.cmd snapshot --at 0.2,1.5 --no-end -o snaps` from `results/X014/project/` — produced both requested stills.

Copied the stills to `preview/snapshot-0.2s.png` and `preview/snapshot-1.5s.png`, then removed `project/snaps/`. Visual inspection confirms the 0.2 s frame is empty and dark; the 1.5 s frame clearly shows the near-white title. No MP4 was rendered.

Note: Snapshot generation printed fontconfig cache warnings, but completed successfully and both images are valid.
