---
status: done
---

# F0023 intro v3

Built `film/intro_v3/` as a 13.8 s, 1920x1080, 30 fps HyperFrames composition. `render.cmd` builds from `machine.local.json`, runs `hyperframes.cmd check`, and renders `RENDERS:intro_v3/intro_v3.mp4`. The private home screenshot, camera derivative and prepared audio are copied only into ignored `assets/`; source footage and audio are not in Git. The camera is SDR BT.709, graded with `GRADE_V1`, framed at 1.15x with Vachana in the left half, and removed at 13.16 s before its 13.269 s source end. No camera frame is held.

Made `film/captions/v3/intro.json`, `film/intro_v3/timeline.json`, nine 1920 px JPG beat stills and `results/F0023/preview/phone-size-sheet.jpg` (each tile 480 px wide). The full card uses `<div class="glass-card full"><h1>How the app works</h1></div>` and holds from 13.16 to 13.80 s. The quiet stem is `RENDERS:intro_v3/sfx.wav`; no music was added. The cleaned, Rule B voice supplied by the lead is `RENDERS:intro_v3/voice.wav` (12.780 s), starting in the composition at 0.4619 s. The draft 1080p motion render is `RENDERS:intro_v3/intro_v3-preview-1080.mp4`; the 540p audio/video preview is `results/F0023/preview/intro_v3-540p.mp4` (3.19 MB).

## Timing and audio

- Measured alignment from the supplied prep: camera time = clean audio time − 0.7781 s; correlation peak 0.254. Speech begins at camera 0.582 s and ends at 12.942 s. The prepared voice uses 30 ms fades and runs to camera 13.242 s, under the full card.
- Prepared voice spectrum (fractional energy below 300 Hz / 300–3000 Hz / above 3000 Hz; centroid): raw 0.1642 / 0.8248 / 0.0111; 632.6 Hz. Clean 0.1150 / 0.8578 / 0.0272; 756.5 Hz. Scene 1 clean reference 0.0641 / 0.8639 / 0.0720; 1262.6 Hz. The prepared check found no low-mid deficit (`+2.57 dB` relative ratio), so no extra shelf was applied.
- Beat starts in composition seconds: panel 0.582; waveform 6.682 (voice-driven on “speaker” at 7.822); typed words 8.902; compact card 10.322; phone 10.472 and banner about 10.59; circle 10.792; icon crosses 10.842, 10.962, 11.262, 11.442; circle expansion 11.962; full card 13.160; end 13.800.
- Caption text is the supplied final take, including `chmod 777`, `iTantra`, `SIH26173`, and “speaker speaks.” The message line follows the six spoken words from “message” through the second “phone.”

## Word timing from prepared `words.json`

Times below are clean-audio seconds; `p` is the supplied ASR probability. These were supplied by the lead, and this task did not run ASR or `prep.py`.

| Word | Start | End | p |
|---|---:|---:|---:|
| I'm | 1.36 | 2.00 | .423 |
| Vachana | 2.00 | 2.32 | .875 |
| from | 2.32 | 2.58 | .936 |
| team | 2.58 | 2.82 | .699 |
| chmod | 2.82 | 3.32 | .353 |
| 777 | 3.32 | 3.86 | .738 |
| for | 3.86 | 4.44 | .855 |
| ISRO's | 4.44 | 4.92 | .855 |
| problem | 4.92 | 5.12 | .874 |
| statement, | 5.12 | 5.56 | .986 |
| SIH26173. | 5.70 | 7.02 | .748 |
| We | 7.46 | 7.50 | .853 |
| built | 7.50 | 7.70 | .762 |
| iTantra, | 7.70 | 8.32 | .407 |
| speaker | 8.60 | 8.88 | .817 |
| speaks, | 8.88 | 9.36 | .990 |
| message | 9.68 | 9.92 | .970 |
| travels | 9.92 | 10.30 | .995 |
| from | 10.30 | 10.58 | .986 |
| phone | 10.58 | 10.82 | .999 |
| to | 10.82 | 10.98 | .988 |
| phone, | 10.98 | 11.30 | .998 |
| no | 11.62 | 11.74 | .994 |
| network | 11.74 | 12.04 | .983 |
| needed. | 12.04 | 12.36 | .998 |
| Let's | 12.74 | 12.94 | .992 |
| see | 12.94 | 13.08 | .999 |
| how | 13.08 | 13.22 | .999 |
| it | 13.22 | 13.38 | .999 |
| works. | 13.38 | 13.72 | .999 |

## Check

`hyperframes.cmd check` passed: 0 lint/runtime/layout/motion errors or warnings; 14/14 text contrast checks passed. Six informational occlusion notices at 12.5 s are the intended expanding full card covering the circle. I reviewed the 1920 px beat stills and 480 px sheet. The 540p preview has video and audio streams and runs 13.802 s. Final delivery render remains for the lead's `render.cmd` run.

## Files moved out of git by the listener

- `film/intro_v3/assets/camera.mp4` (25.2 MB) was too big for git. Moved to local path: `RENDERS:F0023/film/intro_v3/assets/camera.mp4` (inside renders_dir on vivek-pc)
