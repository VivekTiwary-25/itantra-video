---
status: done
---
# F0021: cards polish

`film/cards_v3/index.html`: CSS only. Timings, strings, motion and transition are unchanged.

## Works-now card
| Element | Before | Now |
|---|---|---|
| Card width | 1660 px | 1700 px |
| `WORKS NOW` label | 38 px | 40 px |
| Four items | 46 px semibold | 56 px semibold, 50 px apart |
| Check discs | 46 px | 28 px |
| `COMING NEXT` label | 30 px | 32 px |
| Coming-next items | 36 px | 40 px, still dimmed (64% white, weight 500), outlined 30 px rings |

- The card stays centred by the grid wrapper and now spans y 104-976 (104 px above and below).
- The four items with their label fill about 480 px, roughly half the frame height.
- The longest line ends about 130 px inside the card edge.

## Closing card
`iTantra` 140 px, tagline 60 px, team lines 42 px and 40 px. Card width 1240 → 1320 px.

## Checks
- **`hyperframes.cmd check`:** passed, 0 errors, all 8 text checks WCAG AA. The 3 warnings are the intended 8.25-8.56 s crossfade overlap, as in F0012.
- **Stills:** at 1.0 / 3.0 / 7.5 / 9.0 / 12.0 / 13.9 s in `results/F0021/preview/`, each with a `_480.png` copy, plus `contact-sheet.jpg`.
- **480 px:** every line on both cards reads clearly. COMING NEXT is visibly smaller and dimmer.
