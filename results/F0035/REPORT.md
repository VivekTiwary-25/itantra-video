---
status: done
---

Updated `film/final/beat_stills.py` to print a beat table or extract exact frame-number stills, including each segment's first and last frame. It builds labelled 960 px and 480 px contact sheets and a side-by-side join sheet. Added usage and review instructions to `film/final/README_v3.md`.

Tested with a 12 s synthetic red/blue film and fake assembly report in `results/F0035/synthetic/`. The tool printed 8 beats, extracted 8 JPGs, and produced all three sheets plus `beats.json`. The join sheet shows the red last frame beside the blue first frame. A table-only check against all six supported timeline formats produced 68 beats and 12 join frames. `git diff --check` passed.

Notes: The real film was not rendered or inspected in this task. No source footage was used.
