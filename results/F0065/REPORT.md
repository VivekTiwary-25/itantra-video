---
status: done
---
# F0065: cards: N8 over Works now / Coming next, N9 over the closing card

## Timeline (all computed at build time from `film/common/narration_v4.json`; nothing hard-coded)
`film/cards_v3/cards_timing.py` is the single source (used by `build.py`, `cards_dx.py`, `cards_sfx.py`).

| Quantity | Formula | Now (N8 3.4 s, N9 2.6 s) |
|---|---|---|
| Works card readable | items 0.30-1.80, COMING NEXT settled | 2.45 s |
| N8 start | readable + 0.5 | **2.95 s** (ends 6.35) |
| Works card hold = start of transition | max(8.0, N8 start + N8 + 0.4) | 8.0 s |
| Transition (0.35 s, as F0045) | swap_start .. swap_start + 0.35 | 8.0-8.35 s |
| N9 start | closing card readable (swap_end) + 0.3 | **8.65 s** (ends 11.25) |
| Fade to black starts | N9 start + N9 + 1.0 | 12.25 s |
| **Segment length** | fade start + 1.0 s fade | **13.25 s** (was 14) |

Checked with a longer manifest (N8 6.0, N9 3.5): swap 9.35, N9 at 10.0, length 15.5 s. The card holds N8 + 0.4 s, and the closing card holds N9 + 1.0 s after N9 ends (so at least N9 + 1.0 s from readable too).

## Files changed (all in `film/cards_v3/`, plus captions and results)
- `index.html`: timings read from `assets/timing.js` (`window.CARDS_TIMING`); `data-duration` and the GSAP timeline follow the segment length; a glass-kit `.caption` element (`#cap`, bottom centre, 46 px, 0.18 s fades) shows N8 and N9. To make room, both cards are lifted 48 px (`.card-wrap` inset-bottom 96 px) and the Works card spacing is slightly tighter (padding 62/58 -> 50/46, label gap 40 -> 30, item gap 50 -> 40, divider margins 48/34 -> 38/28). Font sizes, strings, motion and the 0.35 s transition are unchanged. Works card now spans y 96-888, caption box y 950-1026 (62 px gap); closing card y 197-787.
- `build.py`: imports `cards_timing`, writes `assets/timing.js` (git-ignored) and `film/captions/v3/cards.json`, and rewrites `data-duration` in `index.html` when the manifest length changes (so `index.html` can show a one-line diff after a manifest change).
- `cards_timing.py` (new): the timeline computation above.
- `cards_dx.py` (new): writes `RENDERS:cards_v3/cards_dx.wav`, mono 48 kHz, segment length, with the N8 and N9 takes from the manifest's `RENDERS:` files placed at their start times (no gain change; resamples/mixes down if a take is not mono 48 kHz).
- `cards_sfx.py`: stem length now follows the segment length (13.25 s instead of 14); tick times unchanged (0.30/0.80/1.30/1.80).
- `render.cmd`: now runs `cards_sfx.py`, `cards_dx.py`, then `build.py --render`.
- `film/captions/v3/cards.json` (new, generated): `[{start 2.95, end 6.35, "Here's what works today, and what we're building next."}, {start 8.65, end 11.25, "iTantra. Speak. Send. Be heard."}]`, text exactly the manifest text, segment seconds.

## Change for the lead in `film/final/v3_segments.json` (cards entry; I did not edit it)
- `"stems": {"dx": "RENDERS:cards_v3/cards_dx.wav", "sfx": "RENDERS:cards_v3/cards_sfx.wav"}` (dx was `null`).
- `"expected_duration": 13.25` (was 14; or `null`). It changes with the manifest, so `null` is safer.
- `render_cmd` can stay `film\cards_v3\render.cmd` (it now makes both stems; the extra `python film/cards_v3/cards_sfx.py &&` is harmless). Update the `status` note.
- `"music": {"closing_chord_at": 8.0}` equals the transition start (`swap_start`), still 8.0 with the current manifest; it moves if N8 grows past ~4.2 s. `cards_timing.load()["swap_start"]` gives the value.
- `tts_windows` is `[]`; the narration comes through the dx stem so `duck.py` finds the speech from the envelope. Once the real takes exist this works as for the other segments; if you want the windows explicit, add `[2.95, 6.35]` and `[8.65, 11.25]`.
- Stand-in N8/N9 wavs are silent, so `cards_dx.wav` is silent now; rerun `cards_dx.py` (render.cmd does) after `prep_v4.py` brings the real takes. The manifest `duration` must match the take, since layout comes from the manifest.

## Checks
- `python film/cards_v3/build.py`, `cards_sfx.py`, `cards_dx.py` run clean; stems are 13.25 s, 48 kHz mono.
- `hyperframes.cmd check film/cards_v3`: 0 errors, 0 warnings, 10/10 text checks pass WCAG AA. Two info lines only at 8.25 s (intended crossfade overlap, as before). No overlap involving the caption.
- Stills (`hyperframes.cmd snapshot`, 1920 px PNG + `_480.png` copies + `contact-sheet.jpg`) in `results/F0065/preview/`:
  - `frame-00-at-4.5s`: Works now card with the N8 caption. Every line reads at 480 px, COMING NEXT dimmer and smaller, caption clear of the card. Judge line: the caption lands as the list is already there, so the voice and the card agree.
  - `frame-01-at-8.17s`: mid transition, soft blurred dissolve, no hard cut.
  - `frame-02-at-10s`: closing card with the N9 caption, all four card lines and the caption read, no overlap.
  - `frame-03-at-12.9s`: closing card fading to black, no caption (N9 ended at 11.25 s), the last frame before the end is black.
- No full-length render (the lead renders on utkarsh-pc).
