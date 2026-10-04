---
status: done
---

# F0053 intro polish

Enlarged the hero within the unchanged right panel in `film/intro_v3/`. The single phone is 671 px tall (85% of the panel); in the badge ring it is 553 px (70%); both phones in the message and speech beats are 593 px (75%). The speech overlay uses 30 px text. The four network badges are 120 px with 30 px labels and outlined red strikes; the Bluetooth badge is wider so its full 30 px label fits. The packet and gold Bluetooth glyph are about twice their prior size. The second phone's speaker waves remain visible inside the panel. The accepted timing, captions, camera cut, panel position, and downward ending remain unchanged.

Review stills: `preview/frame-00-at-3s.png` through `preview/frame-11-at-33.5s.png` are the same twelve moments as F0046 at 1920 x 1080. `preview/contact-sheet-480.jpg` shows each at 480 px wide.

| Still | Would a judge go “oh”? |
| --- | --- |
| 00, 3 s | Yes: the opening introduces Vachana and the problem plainly. |
| 01, 7.5 s | Yes: the larger single phone immediately anchors her question. |
| 02, 11.5 s | Yes: the first four crossed network badges read around the phone. |
| 03, 14.5 s | Yes: the uncrossed gold Bluetooth badge is the clear exception. |
| 04, 17 s | Yes: her voice becomes a waveform on the larger phone. |
| 05, 19.8 s | Yes: the 30 px speech text is legible on the phone. |
| 06, 22.8 s | Yes: the larger sealed packet and separate gold Bluetooth glyph show travel. |
| 07, 24.4 s | Yes: the packet reaches the second phone without obscuring either phone. |
| 08, 27.8 s | Yes: sound waves visibly leave the second phone. |
| 09, 31.8 s | Yes: the full glass title is direct and readable. |
| 10, 32.8 s | Yes: the downward title movement reveals the next moving scene. |
| 11, 33.5 s | A clean handoff: the bench is moving and the intro graphics are gone. |

Validation: `hyperframes.cmd snapshot` captured all twelve stills. The final `hyperframes.cmd check` passed with 0 lint, runtime, layout, and motion issues; all 8 contrast checks passed. `git diff --check` passed. No full-length render was made.

## Files moved out of git by the listener

- `film/intro_v3/assets/explain.mp4` (29.4 MB) was too big for git. Moved to local path: `RENDERS:F0053/film/intro_v3/assets/explain.mp4` (inside renders_dir on vivek-pc)
