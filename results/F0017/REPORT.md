---
status: done
---

Updated `film/scene2/v3b/` to use `.glass-card.full.sos` for the final `SOS: help from anyone nearby` card. The red tint and frost still build into the full card by 31.9 s.

The dark 1.4 s hand-off came from the opening frames of `sonar_a.mp4`, which reveal the sonar from black. The build now stages a still from that existing render behind the opening and blends into the moving source. The still is generated locally and ignored by Git. `preview/02-1p4s.jpg` shows sonar across the full frame.

Rebuilt against the current glass kit. `node film/scene2/v3b/build.js --preview` passed `hyperframes.cmd check` with no placeholder assets and produced ten stills in `preview/` plus `preview/phone-review.jpg` at 480 px width. The tech lines are fully visible in the stills; captions clear the sonar pins. No final video was rendered.

Join note: scene 3's existing frame 0 currently uses `.glass-card.full` without `.sos`. Its folder is outside this task's `writes:`, so the lead should align scene 3 before final assembly.
