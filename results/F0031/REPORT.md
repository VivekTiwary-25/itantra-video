---
status: done
---
# F0031: exploded view v2, step 2 (teardown animation on placeholder layers)

## Made: `film/exploded_v2/`
HyperFrames, 1920x1080, 30 fps, 16 s.
- **Layers:** three still layers in 2.5D (CSS `translate3d`, 1400 px perspective). Slow push 1.00 → 1.10 (power1 in-out) over the whole segment. No Three.js.
- **Background:** dark studio with a soft top light, plus faint sonar rings around the phone.
- **Files:** `index.html`, `timeline.json` (beats, label times and text, all layout numbers), `build.py` (stages assets + `data.js`), `make_placeholders.py`, `ticks.py`, `render.cmd`, `README.md`.

**PLACEHOLDERS:** F0030 had not delivered when I started, so the layers and part map are placeholders I generated. `make_placeholders.py` draws grey sheared shapes into `RENDERS:exploded_v2/layer_*.png` and writes a fake `parts_placeholder.json`.

**The real files drop in with no code change:** same file names in `RENDERS:exploded_v2/`, and `results/F0030/parts.json` takes priority automatically (several JSON shapes accepted, see README). Layout tuning is in `timeline.json` only. A small "placeholder layers" tag shows in the corner until real parts are used.

**Beats:**

| Time | What happens |
|---|---|
| 0-1.5 s | Assembled phone. |
| 1.5-3.5 s | Layers float apart: screen up-right and toward camera, back cover down-left and away, mid-frame stays; independent drift. |
| 3.5-13 s | Four labels × 2.375 s, exact spec items 24-27, as `.glass-panel` (titles 52 px, details 34 px). Leader lines go to the parts' real pixel positions in `layer_mid.png`, recomputed every frame, with white-blue glow. Bluetooth chip + antenna get the GOLD glow with two leaders. One light sweep crosses the metal frame (3.5-4.8 s), masked to the mid layer. |
| 13-15 s | Layers close up, and the phone glides to frame centre. |
| 14.9-16 s | `No new hardware.` (spec 28), 56 px, centred below the phone. |

- **Ticks:** `ticks.py` (same tick family as `film/exploded/ticks.py`) writes `RENDERS:exploded_v2/ticks.wav` at the label starts 3.5 / 5.875 / 8.25 / 10.625 s (rendered locally).
- **Check:** `hyperframes.cmd check` passes (0 errors, 0 warnings, contrast OK).

**Design change from the brief:** the layers separate diagonally, not straight up. These are three-quarter top-view stills, and a straight vertical stack would put the screen layer over the board's top half (processor, Bluetooth chip) during the labels. The diagonal keeps every lit part clear. The offsets are in `timeline.json`.

## Stills (`results/F0031/preview/`, 1920 px JPG + `sheet_480.jpg`)
With placeholders I judged motion design and layout, not photorealism.

| Still | Hero | Reads at 480 px? | Would a judge go "oh"? |
|---|---|---|---|
| 0.7 s | Assembled phone in three-quarter view on the dark studio. | Yes (no text). | Not yet: it's the calm opener; real render needed. |
| 2.5 s | Layers mid-separation, even gaps. | Yes. | Likely with real images: this is the reveal moment. |
| 4.2 s | Microphone label + glow at the bottom edge. | Title yes, detail yes. | Moderate: the glow is small on the placeholder mic. |
| 6.8 s | Processor glow + label; detail wraps to 3 lines + 1. | Yes, the detail is just readable. | Yes with a real SoC under the glow. |
| 9.2 s | Gold glow on the Bluetooth chip and antenna, two gold leaders. | Yes. | Yes: the gold ties back to the intro. |
| 11.6 s | Loudspeaker glow + label. | Yes. | Moderate. |
| 14 s | Layers closing back together, moving to centre. | Yes. | Yes as motion (snap-back). |
| 15.7 s | Closed phone centred, `No new hardware.` | Yes, clearly. | Clean end line. |

The one thing to check once F0030 lands: the real `parts.json` positions, and `layer_px` / offsets, so the screen layer never covers a lit part and nothing leaves the frame at the 1.10 push.
