---
status: done
---

Built `film/scene2/v3b/` and `film/captions/v3/s2b.json`. `node film/scene2/v3b/build.js --preview` passed `hyperframes.cmd check` and produced ten 960 px stills in `results/F0009/preview/`. `film/scene2/v3b/render.cmd` stages local assets with `machine.local.json`, rejects missing assets for a final render, and writes to `RENDERS:scene2/v3b/scene2_v3b.mp4` when the lead runs it. No final video was rendered in this task.

Timeline (segment seconds): push into Yash's phone 0–1.4; `sonar_a` 1.4–8.4; `relay_1` 8.4–14.4; `relay_2` 14.4–20.4; `relay_3` 20.4–26.4; `sonar_b` 26.4–32.4. Red tint and frost begin at 30.9; the `.glass-card.full` title `SOS: help from anyone nearby` is fully visible from 31.9 through the last frame. N2 starts at 1.4 and N3 at 30.4, matching v2's starts relative to `sonar_a` and `sonar_b` (0 and +4 s). Sonar SFX are staged; sonar music is omitted for the film-wide bed.

The start uses the task's fallback because `film/scene2/v3a/timeline.json` is absent on this machine: a 450 × 1000 Yash screen centred at (960, 540) on `#0a0d12`. The slot frame is 11.724 s into `RENDERS:scene2/app/yash_app.mp4`, calculated from `play_at` 7.63 + TTS delay 0.15 + TTS length 3.343673 + 0.6. Frame 0 is shown in `preview/00-0s.jpg`. Exact pixel comparison to s2a's eventual end frame remains for the join review.

Packet check: `film/scene2/sonar/cues.py` defines `sonar_b` hops V→R1 (0.55–1.10), R1→R2 (1.22–1.72), R2→R3 (1.84–2.42), R3→Y (2.54–3.12) relative to `sonar_b`; `overlay.js` animates the packet along those hops. I inspected the local rendered frames at 27.8 and 29.2 s, including the relay packet and final approach. Relay footage and callouts reveal no message content.

N2/N3 caption wording follows `RENDERS:narration/vivek/report.json`, including Vivek's spoken “does” in N2. The report has transcript and total duration but no word timestamps, so the N2 caption split is estimated within its 3.35 s line. The tech lines each stay up for at least 3.05 s. At 960 px they read clearly; the small second line is tiny in a 360 px downsample and should be checked in the film's intended phone playback orientation.
