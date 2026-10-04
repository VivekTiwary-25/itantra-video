---
status: done
---

# F0061: scene 2a narration and status mask

Updated `film/scene2/v3a/` and `film/captions/v3/s2a.json`.

- N0 starts at scene time 0. The `Normal` card lasts 4.6 s, from manifest duration 4.2 s plus 0.4 s. The bench video runs continuously underneath from source 0.9667 to 5.5667 s, then continues through the split.
- N0 audio and its exact manifest text are in the audio stem and captions. N1 uses its manifest duration, with a 3.6 s beat (3.2 + 0.4 s) over the walk. If a later take exceeds the present walk/map space, the build extends the overhead map before the Yash reveal.
- A solid `#07111c` strip covers Yash's 115 px source status bar on the phone layer. The notification banner remains visible. The strip briefly yields only while the banner itself covers that top strip.
- `timeline.json` duration is 42.337 s. Its `end_state` remains `yash_app` source 19.4334 s at x=735, y=40, 450 x 1000, background `#0a0d12`, matching the s2b join geometry.

`node film/scene2/v3a/build.js --page-only` passed, including `hyperframes.cmd check`. `--audio-only` passed and wrote N0/N1 events. `git diff --check` passed. No full scene render was made. Local build media: `RENDERS:scene2/v3a/walk.mp4`, `RENDERS:scene2/v3a/scene2_dialogue_sfx.wav`.

## Previews

Full 1920 px stills are in `results/F0061/preview/`; `sheet_480.jpg` shows them at 480 px each.

| Still | Would a judge go “oh”? |
| --- | --- |
| `frame-00-at-0.5s.png` | Yes: the Normal card lands over a live bench shot as N0 begins. |
| `frame-01-at-2.1s.png` | Yes: the full N0 idea reads cleanly while the bench keeps moving. |
| `frame-02-at-4.3s.png` | The card is still present through its 0.4 s tail, then clears. |
| `frame-03-at-19.8s.png` | The walking shot and N1 caption make the distance feel concrete. |
| `frame-04-at-23.6s.png` | The overhead map establishes the route without stopping live video. |
| `frame-05-at-29.9s.png` | Yes: Yash sees the real notification, while the status strip is clean. |
| `frame-06-at-31.8s.png` | The Logs screen is whole, stable, and has no hotspot pill. |
| `frame-07-at-32.8s.png` | The listening screen stays readable with the status pill hidden. |
| `frame-08-at-42.25s.png` | The final centered phone frame is ready for s2b's push-in. |

Note: lengthening the opening bench shot keeps the source continuous but moves Vachana's separate dialogue later relative to her visible mouth. Review that split in the assembled film.

## Files moved out of git by the listener

- `film/scene2/v3a/assets/walk.mp4` (24.0 MB) was too big for git. Moved to local path: `RENDERS:F0061/film/scene2/v3a/assets/walk.mp4` (inside renders_dir on utkarsh-pc)
