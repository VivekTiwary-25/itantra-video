---
status: done
---

# T0012: Scene 3 SOS pulse look test

Made a standalone, seekable 1920 × 1080 composition in `results/T0012/pulse/`. It reuses the Scene 2 sonar campus renderer, traced geometry and settled camera. The campus remains in its revealed blue state. One soft red ring expands from Vachana, and Vivek's nearby marker lights when it arrives. There is no route, relay marker, packet or message content.

Stills in `results/T0012/preview/`:

- `start.png` — 0.15 s, before the red ring begins.
- `mid.png` — 1.00 s, ring expanding.
- `arrival.png` — 1.85 s, ring reaches Vivek and his marker is lit.

Timing: 3.2 s test duration. The ring begins at 0.20 s and travels at 70 campus map pixels/s. The illustrative responder point is 111.5 map pixels from Vachana, giving contact at approximately 1.79 s. The point brightens over the last 0.12 s before contact. The start, speed and contact time can be changed in `index.html`.

Colour: existing campus cold tones `#B4D6F4`, `#F2F9FF` and `#7AA2C6`; ring core `#E65A63`, soft glow `#D62F40`, broad wake `#A52936`; sender `#EAF4FF`. No source footage or audio was used.

Notes: The responder location is a look-test position, not a verified real-world actor position. It should be confirmed during the Scene 3 edit. `brief/style.md` was not present, so this test takes its campus look from the existing Scene 2 composition. `hyperframes.cmd check results/T0012/pulse` passed with one warning from the locally supplied Three.js global build. All three PNGs were rendered and inspected at 1080p; each is under 8 MB.
