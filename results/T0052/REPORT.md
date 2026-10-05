---
status: done
id: T0052
worker: codex-vivek
machine: vivek-pc
---

Made all three assigned 1280x720 PNG thumbnails:

- `thumbnails/v1_vachana_relay_speak.png`: Vachana in the left third, the film's sonar campus on the right, one blue capsule with a white lock mid-hop between R2 and R3, blank phone markers, and a crossed-out signal icon. Text: "iTantra" and "Speak. Send. Be heard."
- `thumbnails/v2_vachana_relay_nonetwork.png`: the same frame, layout, map, and packet as v1. Text: "iTantra" and "No network. Still heard."
- `thumbnails/v3_vachana_sos.png`: Vachana beside the film's sonar campus, with concentric red rings from ONE phone at Vachana's map position. No relay chain, packet, or hop lines. Text: "iTantra" and "No network. Still heard."

Final person frames:

| Thumbnail | Footage | Time |
| --- | --- | --- |
| v1 | `FOOTAGE:Video/normalpart1.mp4` | 8.00 s |
| v2 | `FOOTAGE:Video/normalpart1.mp4` | 8.00 s |
| v3 | `FOOTAGE:Video/sospart1.mp4` | 9.50 s |

Scored 23 intro candidates, 18 normal-message candidates, and 18 SOS candidates with Laplacian sharpness over the central actor region. Personally inspected each clip's best-eight contact sheet. The relay frame ranked fifth (3849.89), with clearly open eyes and a natural mid-word expression; the SOS frame ranked first (2400.38). Final scoring and extraction both use FFmpeg timestamp seeks because OpenCV seeking initially selected different frames. The final normal frame is 8.00 s, superseding the preliminary choices.

All footage is SDR BT.709. Applied the exact `GRADE_V1` filter from `film/scene1/grades.sh` before compositing. Feathered real-person masks and a gentle bottom fade blend her into the dark field. No additional vignette was added.

Reused `film/scene2/sonar/shared/sonar.js`, the film's `geo.js`, and local Three.js/GSAP. The relay overview and phone coordinates come from the film's sonar scene. The capsule follows the blue rounded capsule and white-lock styling from `film/scene2/v3b/`; the SOS camera, origin `[330,598]`, ring colour, and restrained glow follow `film/scene3/v3/sos_map.js` and its scene CSS. Built small static compositions using these local scripts; the film files were not edited. No source-scene captions, labels, numbers, or UI text were imported. The only visible words are the required identity and four-word tagline.

Sources: `thumbnails/src/T0052/`.

Rebuild from the repository root:

```text
python thumbnails/src/T0052/frames.py
python thumbnails/src/T0052/build.py
```

`frames.py` recreates scoring/contact sheets; `build.py` extracts the fixed selected frames, applies the grade, prepares local dependencies, snapshots each 1280x720 composition through `hyperframes.cmd`, and verifies the outputs. Requires the existing local FFmpeg, HyperFrames, Pillow, OpenCV, and NumPy installations. Resolves footage from `machine.local.json`.

Intermediates, masks, scene compositions, and contact sheets remain under `local/thumbs/T0052/`. No extracted footage frames or source videos were added to the public results.

Verification:

- All three final images are PNGs at exactly 1280x720 and approximately 0.5 MB each, below the 20 MB limit.
- `results/T0052/preview/sheet.png` shows all three side by side at 320x180 each. Personally inspected the final sheet and full-size thumbnails; the title and both taglines remain readable.
- Pixel comparison confirms v1/v2 differ only within the tagline area.
- The locked packet is the only carried message visual; phone markers have empty screens.
- SOS contains one red pulse origin and no relay route.
- Source check passed for absolute paths, network URLs, and email addresses. Dependencies are local; no network resources were loaded.

Composition intent: keep the real speaker prominent, use quiet campus contours to explain the setting, and make the locked packet or local red pulse the single visual action.
