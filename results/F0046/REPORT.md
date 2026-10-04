---
status: done
---

# F0046 intro v4

Built the 33.6 s intro in `film/intro_v3/` from `cuts_v4.json`, `words_v4.json`, `envelope_v4.json`, `RENDERS:intro_v4/voice.wav`, and the existing captions. The opening name/team/problem panel remains as before. The one camera cut is at 6.842 s and coincides with the change to a fixed right-hand glass panel. That panel moves through the badge ring, voice waveform and text, message flight, and second phone speaking. The title drops from above, holds for 1.2 s, then continues down over the moving bench shot. `render.cmd` retains `call hyperframes.cmd` and `"%~dp0."`.

`film/intro_v3/timeline.json` records the last intro frame of `FOOTAGE:Video/normalpart1.mp4` at source **0.966667 s**; scene 2 can begin at source 1.0 s. The intro uses live moving footage throughout. Generated camera assets and the private home image remain ignored local build inputs. No full-length render was made.

## Review stills

All full-size frames are 1920 × 1080 in `results/F0046/preview/`. `contact-sheet-480.jpg` places each frame at 480 px wide.

| Still | Hero; reads at 480 px?; judge reaction |
| --- | --- |
| `frame-00-at-3s.png` | Vachana and the unchanged name/team/problem panel; yes; strong direct opening. |
| `frame-01-at-7.5s.png` | The bridge question and centred real phone; yes, caption reads; clean visual reset. |
| `frame-02-at-11.5s.png` | Four network badges building around the phone; yes, labels and strikes read; the idea is immediate. |
| `frame-03-at-14.5s.png` | Complete five-badge ring with gold Bluetooth; yes, exception reads; clear focal point. |
| `frame-04-at-17s.png` | Her voice waveform inside the phone; yes, silhouette and caption read; tangible speech beat. |
| `frame-05-at-19.8s.png` | Waveform resolved into phone text; yes, caption reads and text transformation is clear; focused beat. |
| `frame-06-at-22.8s.png` | Locked packet crossing the gold Bluetooth link; yes, two phones and packet read; clear travel. |
| `frame-07-at-24.4s.png` | Packet arriving at the second phone; yes, trajectory reads; good handoff. |
| `frame-08-at-27.8s.png` | Second phone emitting speaker waves; yes, waves and caption read; the return to speech lands. |
| `frame-09-at-31.8s.png` | Full frosted `How the app works` title; yes; quiet and readable. |
| `frame-10-at-32.8s.png` | Title continuing down to reveal the moving bench; yes; transition direction reads. |
| `frame-11-at-33.5s.png` | Clean moving bench shot with no leftover intro graphics; yes; scene 2 is ready to continue. |

## Checks

- `hyperframes.cmd check .`: passed; 0 lint/runtime/layout/motion issues, 8/8 contrast checks passed.
- `git diff --check`: passed.
- All 12 preview PNGs are under 20 MB; the 480 px sheet is under 1 MB.

## Files moved out of git by the listener

- `film/intro_v3/assets/explain.mp4` (29.4 MB) was too big for git. Moved to local path: `RENDERS:F0046/film/intro_v3/assets/explain.mp4` (inside renders_dir on vivek-pc)
