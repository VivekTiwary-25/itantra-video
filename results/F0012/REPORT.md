---
status: done
---
# F0012: closing cards (works now / coming next + closing)

## Made
`film/cards_v3/` is one HyperFrames composition, `cards_v3`: 1920x1080, 30 fps, 14 s.

| File | What it does |
|---|---|
| `index.html` | The composition. A paused GSAP timeline calls one deterministic `draw(t)`; there is no randomness and no clock. It is registered as `window.__timelines.cards_v3` and also listens for `hf-seek`. |
| `build.py` | Copies `film/vendor/gsap/gsap.min.js` and the glass kit (`film/common/glass/` into `assets/glass/`, git-ignored). If the kit is absent it writes a minimal fallback `glass.css` with the same class names and tokens. `--render` renders to `RENDERS:cards_v3/cards_v3.mp4` using `renders_dir`. |
| `render.cmd` | Runs `python build.py --render`, for the lead over SSH on a render machine. |
| `cards_sfx.py` | Optional stem `RENDERS:cards_v3/cards_sfx.wav`, 14 s, mono 48 kHz, peak −20 dBFS. One tick per WORKS NOW item at 0.30 / 0.80 / 1.30 / 1.80 s, which match the item times in `index.html`. It uses the same partials and envelope as `film/exploded/ticks.py`, so it is the same tick family. Rendered locally; not in git. |
| `hyperframes.json`, `.gitignore` | Project setup; `assets/` and `snapshots/` are ignored. |

## Timeline
- **Background, whole 14 s:** a dark sonar field with six faint blue pulse rings (peak opacity 0.14) expanding slowly from a centre that drifts slowly. A faint concentric grid moves with it, under a vignette.
- **0–8 s, works-now card** (a `.glass-card`, 1660 px wide):
  - **WORKS NOW:** a 38 px letter-spaced label, then the four 3.20 items at 46 px semibold. Each has a small solid blue (`--blue`) check disc. The items appear one by one (0.30, 0.80, 1.30, 1.80 s; 0.38 s ease plus a 22 px slide).
  - **COMING NEXT:** after a thin divider, the label `COMING NEXT` (30 px, dimmed) and the two 3.21 items at 36 px, dimmed, with outlined empty circle markers. The group fades in at 2.05 s and has settled by 2.45 s.
  - From 2.45 s to 8 s only the background moves.
- **8.0–8.8 s, soft glass transition:** the works card blurs (0 → 16 px), fades and grows 2.5%, while the closing card blurs in (16 → 0 px) from 97.5% scale. There is no hard cut.
- **8–14 s, closing card:**
  - `iTantra` at 124 px bold with a faint blue glow
  - `Speak. Send. Be heard.` at 52 px
  - a short blue rule
  - `Team chmod 777 · Team ID 148903` at 38 px
  - `SIH26173 · NIE Mysuru` at 36 px, dimmed

  The card grows very slowly (1.2%), and black fades in over 13.0–14.0 s.
- **Text:** all on-screen strings are exactly those in spec section 3 (items 20, 21 and 22). No people's names.

## Checks
- **`hyperframes.cmd check`:** passed, 0 errors. Contrast: every text check passes WCAG AA. The remaining layout warnings (two `content_overlap` and some `text_occluded` info) only happen at 8.25–8.56 s, during the intended crossfade, when both cards are blurred and half transparent.
- **Stills** (`hyperframes.cmd snapshot` only, no video render): `results/F0012/preview/frame-0N-at-{1,3,7.5,9,12,13.9}s.png` at 1920 px, each with a `_480.png` copy 480 px wide, plus `contact-sheet.jpg`.
- **Reading at 480 px:**
  - 1.0 s: the first item is in and the second is arriving.
  - 3.0 s and 7.5 s: every WORKS NOW line and the COMING NEXT label and items read clearly. COMING NEXT is visibly smaller and dimmer, with empty markers.
  - 9.0 s and 12.0 s: all four closing lines read.
  - 13.9 s: nearly black, as intended.
- **Mid-transition frame (8.4 s, scratch only):** a soft blurred dissolve.

## Notes
- The glass kit's `.glass-card h1` and `.glass-card p` rules are more specific than plain class selectors. So the closing-card sizes use `#close …` selectors, and the kit itself is unchanged.
- **Joins:** the composition starts on the empty sonar field and the works card fades in over 0.3 s. It ends on black. There is no identical-frame join with the exploded view; tell me if the assembler needs one.
- `gsap.min.js` is committed next to `index.html`, as in `film/exploded/`.
