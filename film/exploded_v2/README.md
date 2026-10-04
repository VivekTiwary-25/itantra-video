# Exploded view v2 (photoreal teardown, 16 s)

HyperFrames, 1920x1080, 30 fps. Three still layers (screen / metal mid-frame with board / back cover) in 2.5D: CSS `translate3d` under a 1400 px perspective plus a slow 1.00 → 1.10 push. No Three.js.

## Files
| File | What it is |
|---|---|
| `index.html` | The composition, a pure function of t. All numbers come from `timeline.json` (via `assets/data.js`). |
| `timeline.json` | Beat times, label times and text (spec items 24-28), layout. `layer_px` sets image width; height follows the source aspect ratio. `center`, per-layer `tight` / `exploded` offsets `[x, y, z]`, `label_x`/`label_w`, and `end_center_x` control placement. |
| `build.py` | Stages `assets/`: the layers, `data.js` (timeline + parts), the glass kit, GSAP. `--placeholders` makes placeholder layers first if the real ones are missing. |
| `make_placeholders.py` | Grey placeholder layers + `parts_placeholder.json` (never overwrites real layers unless `--force`). |
| `ticks.py` | One glass tick per label, at the label start times → `RENDERS:exploded_v2/ticks.wav`. |
| `render.cmd` | build → ticks → render to `RENDERS:exploded_v2/exploded_v2.mp4` (render machines only). |

## Beats (timeline.json)
- **0-1.5 s:** assembled phone, push starts.
- **1.5-3.5 s:** layers float apart. The screen goes up-right and toward camera, the back down-left and away, and the mid-frame stays put; each layer drifts slightly on its own.
- **3.5-13 s:** four labels, 2.375 s each: Microphone, Processor, Bluetooth chip and antenna (GOLD glow, two leaders), Loudspeaker. Each has a leader line and glow on the part from `parts.json`. A light sweep crosses the metal frame at 3.5-4.8 s.
- **13-15 s:** the layers close up, and the phone glides to frame centre (`end_center_x`).
- **14.9-16 s:** `No new hardware.` (56 px), centred below the phone.

## Swapping in the real images (F0030)
1. Put `layer_screen.png`, `layer_mid.png`, `layer_back.png` in `RENDERS:exploded_v2/`, replacing the placeholders: same names, same 1366 x 2048 portrait canvas for all three, transparent background.
2. `results/F0030/parts.json` is picked up automatically, and the placeholder parts are then ignored. Coordinates are pixels in `layer_mid.png`. Required parts: `microphone`, `processor`, `bluetooth_chip`, `antenna`, `loudspeaker` (`battery` is optional). Accepted shapes:
   - `{"parts": {name: {...}}}` or `{name: {...}}`
   - per part: `center`/`centre` `[x, y]` and/or `bbox`/`box` (`[x, y, w, h]` or `[x0, y0, x1, y1]`), or `x,y,w,h` / `cx,cy`
3. Run `python film/exploded_v2/build.py` and `hyperframes.cmd snapshot film/exploded_v2 --at 2.5,4.2,6.8,9.2,11.6,15.7`. The small "placeholder layers" tag in the top-right corner disappears once real parts are used.
4. If the real phone sits differently in its canvas, change `layer_px` and the `exploded` offsets in `timeline.json` so that:
   - the lit parts on the mid-frame stay uncovered by the screen layer
   - nothing leaves the frame at the 1.10 push
   - labels (from `label_x`) do not cover the stack
