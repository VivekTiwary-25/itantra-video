---
status: done
---
# F0051: scene 3 v4 small fixes

Changed: `film/scene3/v3/sos_map.js`, `index.html.tpl`, `build.py` (+ regenerated `index.html`). No timing changes: `build.py --page-only` still gives 56.3 s with the same N5a/N5b/N6 beats, and `hyperframes.cmd check` passes (inside the build).

1. **Timer chip (N5b).** It is now a stylised clock that agrees with the labels:
   - **0 → 3 s** while `3 strongest phones` lights, then a quick count lands **exactly** on `10 s` when `5 phones at 10 s` appears.
   - It holds 10, counts quickly to `25 s` exactly as `2 hops at 25 s` appears, holds, then counts quickly to `60 s` as `3 hops at 60 s` appears, and holds 60.
   - The display rounds down, so it never shows a milestone before its label.
   - During each quick count the old label fades out, so a running time (e.g. 23 s, 56 s) is never beside a label it contradicts.
   - Screen time per stage stays tied to N5b's duration (same stage fractions .34 / .60 / .84 as F0043).
2. **N6 chip.** `Accept` / `Decline` moved below-right of Vivek's pin (pin + 30 px across, + 56 px down). The `Vivek` label and the chip now both read in full.
3. **Frame-0 SOS card.**
   - `build.py` now inserts s2b's exact `end_state.card_html` from `film/scene2/v3b/timeline.json` (F0042) for both the frame-0 card and the clearing cover, falling back to the same literal if the key is missing.
   - The old scene-3-only card CSS (38 px subline, own tint) is replaced by s2b's card CSS: full-frame wrapper, kit `.glass-card.full` with flex column centring, kit title size 64 px (like the `Normal` card in s2a), kit subline 36 px.
   - Frame 0 vs F0042's s2b SOS-card still: mean absolute difference 2.2/255, also 2.2/255 in the title area. The residue is the moving picture under the frosted card (sonar vs footage), not the card.

## Stills (`results/F0051/preview/`, 1920 px JPG + `sheet_480.jpg`)
| t (s) | What it checks | Clock / label |
|---|---|---|
| 0.000 | frame-0 SOS card = s2b join card | `SOS` 64 px, subline 36 px |
| 23.493 | 3 strongest phones lighting | 1 s, label `3 strongest phones` |
| 24.453 | quick count starts | 4 s, old label fading out |
| 24.677 | just before the milestone | 9 s, no label |
| 24.741 | milestone | **10 s** + `5 phones at 10 s` |
| 25.413 | hold | 10 s + `5 phones at 10 s` |
| 26.341 | quick count | 23 s, no label |
| 26.405 | milestone | **25 s** + `2 hops at 25 s` |
| 27.013 | hold | 25 s + `2 hops at 25 s` |
| 27.877 | quick count | 56 s, no label |
| 27.941 | milestone | **60 s** + `3 hops at 60 s` |
| 28.421 | hold | 60 s + `3 hops at 60 s` |
| 31.573 | N6: Vivek pin + Accept (lit) / Decline below-right | both read |

Everything reads at 480 px. The milestone frames are the "oh" beats: the clock visibly jumps and lands with each label.

## Files moved out of git by the listener

- `film/scene3/v3/assets/vachana.mp4` (22.9 MB) was too big for git. Moved to local path: `RENDERS:F0051/film/scene3/v3/assets/vachana.mp4` (inside renders_dir on yojitth-pc)
