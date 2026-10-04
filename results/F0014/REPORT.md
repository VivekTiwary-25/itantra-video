---
status: done
---

## Made

- Updated `film/exploded/index.html`: centred phone at the start and end, left-positioned exploded stack, 40 px / 30 px glass labels, 2 px leaders, stronger sonar rings, a visible locked blue packet, travelling layer glows, and a distinct surface graphic on all six layers. The private iTantra home image remains in the ignored local build asset.
- Updated `film/exploded/ticks.py` and regenerated `RENDERS:exploded/ticks.wav` at the six label entrances.
- Nine 1920 × 1080 stills at 1, 3, 5, 7, 9, 11, 13, 15, and 16.9 s in `results/F0014/preview/`, plus `contact-sheet.jpg`, nine 480 px copies in `phone-size/`, and `contact-sheet-480.jpg`.
- Full 1920 × 1080, 30 fps, 17.0 s render: `RENDERS:exploded/F0014-full.mp4` (video only). The 960 × 540 preview with tick audio is `results/F0014/preview-540p.mp4` (17.0 s, 694,091 bytes).

## Label and tick times

| Time | Layer |
| ---: | --- |
| 2.70 s | Screen and mic |
| 4.70 s | Speech to text |
| 6.70 s | Encryption |
| 8.70 s | Bluetooth radio |
| 10.70 s | Speaker |
| 12.70 s | Base |

## Check and render time

- Final full render: 2 m 2.2 s on this machine, with 2 browser workers and hardware GPU screenshot capture. Output is 510 frames, 17.0 s, 3,369,941 bytes.
- `hyperframes.cmd check` passed. Lint and motion: 0 errors and 0 warnings; contrast: 6/6 text checks pass. Runtime reported the bundled Three.js global-build deprecation warning. Layout reported informational overlap during the intended label crossfades.
- `git diff --check` passed. No private home image or other local build asset is included in the task result.
