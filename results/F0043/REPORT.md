---
status: done
---

# F0043 — Scene 3 v4

Made the neutral SOS card with N5 timed from `film/common/narration_v4.json`; it clears over moving `sospart1`. The searching screen cuts directly to a self-rendered sonar map. N5a, N5b and N6 set the lengths of the repeating red pulse, nearby phone rings, timer milestones and Vivek's Accept/Decline beat. The map then enters the existing dive and lab. App recordings now use uncropped 2400 px sources at one stable size, with the banner and reply punch-ins removed. The scene ends 0.4 s after Send without a black fade. Dialogue captions were retimed; narration captions are generated from nonempty v4 transcript fields.

The uncropped app derivatives are local: `RENDERS:scene3/v3/app/vachana_sos.mp4` and `RENDERS:scene3/v3/app/vivek_app.mp4`. The build prepares them from the local raw captures if needed. Missing placeholder narration for N5, N5a, N5b and N6 was written as silent preview WAVs under `RENDERS:narration/v4/`. A production render refuses the current `placeholder` narration status.

## Preview review

Each PNG is 1920 × 1080; each has a matching `-480.jpg`. `preview/sheet-480.jpg` shows all 16 beats with each frame 480 px wide. “Reads” assesses the main action and permitted labels at that size; fine text native to the app recording remains small because the full app screen stays visible.

| Still | Hero | Reads at 480 px? | Judge “oh”? |
| --- | --- | --- | --- |
| `frame-00-at-0s.png` | Neutral SOS card, red word accent | Yes, title and subline | Yes, clear mode change |
| `frame-01-at-4.15s.png` | Card clearing to moving Vachana | Yes, visual handoff | Yes, live reveal |
| `frame-02-at-8.5s.png` | Hands-free SOS beside Vachana | Yes, camera, phone and caption | Yes, real use |
| `frame-03-at-19.8s.png` | Vachana pulse, no contact line | Yes, pin and label | Yes, search starts locally |
| `frame-04-at-23.25s.png` | Three strongest phone dots light | Yes, red rings and label | Yes, first search step |
| `frame-05-at-25s.png` | Search expands to five phones | Yes, dots, label and timer | Yes, wider reach |
| `frame-06-at-26.7s.png` | Pulse hops outward twice | Yes, outer ring and label | Yes, visible expansion |
| `frame-07-at-28.5s.png` | Third hop and 60 s milestone | Yes, 60 s chip and label | Yes, final reach |
| `frame-08-at-29.7s.png` | Vivek pin and choice appear | Yes, pin and Accept/Decline | Yes, human decision |
| `frame-09-at-31.8s.png` | Accept lights red | Yes, highlighted choice | Yes, decisive response |
| `frame-10-at-34.5s.png` | Dive reaches the lab | Yes, Vivek in the lab | Yes, map becomes reality |
| `frame-11-at-35.3s.png` | Vivek with his phone | Yes, subject and lab | Yes, response context |
| `frame-12-at-36.9s.png` | SOS notification on steady full phone | Main notification shape yes; fine UI text small | Yes, arrival reads with prior map |
| `frame-13-at-38.9s.png` | Unhurried app acceptance | Main choice yes; fine UI text small | Yes, acceptance follows map choice |
| `frame-14-at-49.8s.png` | Vivek replying in the lab | Yes, caption and stable phone | Yes, reply lands |
| `frame-15-at-55.9s.png` | Red Send button, no black fade | Yes, send action | Yes, clean scene handoff |

## Checks and notes

- `python film/scene3/v3/build.py --page-only` passed and generated a 56.3 s timeline from the current placeholder durations. No full-length scene render was made.
- Final `hyperframes.cmd check film/scene3/v3` passed: zero lint, layout or motion errors; 5/5 contrast checks. It reports only the existing Three.js deprecation warning and intentional camera overflow notices.
- `python -m py_compile` and `git diff --check` passed. Final map beats were captured again after the label and pulse changes.
- The current s2b `end_state` has no `card_html`, so frame 0 uses the exact neutral card text from v4 S3. The s2b card needs the matching v4 update at assembly. Native app fine print is still too small to read on a 480 px whole-frame copy; the full screen cannot be enlarged further without zooming or cropping it.

## Files moved out of git by the listener

- `film/scene3/v3/assets/vachana.mp4` (22.9 MB) was too big for git. Moved to local path: `RENDERS:F0043/film/scene3/v3/assets/vachana.mp4` (inside renders_dir on utkarsh-pc)
