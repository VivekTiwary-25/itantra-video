---
status: done
---

# T0006 — walk from Vachana to Yash

## Matches

| Landmark | Reference source timestamp | Walk timestamp | Confidence | Evidence |
|---|---:|---:|---|---|
| Vachana's bench | `FOOTAGE:Video/normalpart1.mp4` **1.00 s** | `FOOTAGE:Video/normalpart2.mp4` **26.00 s** (visible about 24.5–27.0 s) | **High** | Vachana herself is seated on the white concrete bench; the adjacent woman, flowering shrub, and boundary wall align. See `start_match.jpg` (reference left, walk right). |
| Yash's garden hedge | `FOOTAGE:Video/normalpart6.mp4` **1.00 s** | `FOOTAGE:Video/normalpart2.mp4` **201.80 s** (best arrival view about 200.0–202.15 s) | **Medium** | The same large round hedge, orange marigold border, lawn, and white building are visible from a much wider angle. The hedge is at the extreme end of the walk. See `end_match.jpg` (reference left, walk right). The camera angle prevents an unambiguous feature-match proof of the individual hedge. |

I sampled the walk every 0.5 s over 6–38 s and 145–202 s. `analysis/match.js` searches with FAST-like corners, gradient-histogram descriptors, a nearest-neighbour ratio test, and geometric consensus. The start's top geometric result was **26.0 s** (6 inliers); direct visual evidence makes that match decisive. The end search produced weak, non-unique matches among repetitive windows and foliage (a spurious top result at 197.0 s, 7 inliers). I used the visible hedge and garden layout to choose 201.8 s and kept confidence at medium.

## Speed ramp and preview

- `ramp.json` has five source pieces. Durations are 0.50 s at 1×, 0.50 s at 4×, 3.974 s at 38×, 0.425 s at 6×, and 0.60 s at 1×. Mathematical output length: 5.9987 s.
- Skipped 28–40 s (near-camera umbrellas/walkers) and 191–199 s (pedestrians crossing the garden path).
- `ramp.sh` is the reproducible ffmpeg-only implementation. Run from the repository root with `$FOOTAGE_ROOT` set. It applies the approved `GRADE_V1` from `film/scene1/grades.sh` to this camera footage.
- `preview/walk_ramp.mp4` was rendered and checked: **960×540, 30 fps, 180 frames, 6.000 s, no audio, 6,740,374 bytes** (under 8 MB).
- No stabilization was applied. The selected route remains readable in the contact-sheet review, while the major near-lens obstructions are removed by the skips; deshaking this forward walk would introduce moving edge crops without a clear benefit to this short preview.

## Files made

`ramp.json`, `ramp.sh`, `preview/walk_ramp.mp4`, `start_match.jpg`, `end_match.jpg`, and `analysis/match.js`.
