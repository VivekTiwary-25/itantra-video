# Film v3 visual style

Use one quiet, dark frosted-glass system for title cards, side panels, tech lines, captions, and map labels. The source of truth is `film/common/glass/glass.css` and `glass.js`; copy the kit into each composition's `assets/glass/` at build time. Type is `SceneSans`, resolved locally to Segoe UI Variable Display / Segoe UI / sans-serif. Never fetch fonts, scripts, or images from a URL.

| Token | Value / use |
| --- | --- |
| `--glass-tint` | rgba(14,18,26,.48), dark enough for bright daylight shots |
| `--glass-blur` | 28 px, saturate(1.4) |
| `--glass-border` | 1 px rgba(255,255,255,.18) |
| `--glass-shadow` | 0 24px 60px rgba(0,0,0,.35) |
| `--text` | #f3f5f8 |
| `--text-dim` | rgba(243,245,248,.7) |
| `--blue` | #4da3ff: Normal messaging |
| `--red` | #ff4d5e: SOS and icon strike |
| `--gold` | #f5c451: Bluetooth glow, never a strike |

Cards have a 28 px radius, 64 px semibold title, and a faint top highlight. Full cards cover 1920 × 1080 with no radius and .86 dark tint. Panels have a 22 px radius with 40 px primary / 30 px secondary text. Light `.glass-circle` uses rgba(255,255,255,.55), 30 px blur, a .6 white border, and #14181f content. Grain is the local 256 × 256 `noise.png` tile at about 3% opacity.

One `.techline` at a time goes top centre at y=64: 30 px text, 12 × 26 px padding, 1300 px maximum width, one line; its optional second `<small>` line is 22 px and dim. Captions under every speech line go bottom centre, with the text baseline near y=1000: 38 px white, soft dark shadow, subtle .35 dark-glass strip, at most 1400 px wide and two lines. Keep captions clear of phone UI and tech lines. `.label-pin` uses 26 px.

Live camera video never freezes or holds a frame. When the source ends, cut or let the moving app side take over. Do not speed app screens or speech. Keep relay content hidden; SOS uses a local red search pulse, not the Normal relay chain. The film's text, claims, and exact strings come from `discussion/v3/001-claude-lead.md`.
