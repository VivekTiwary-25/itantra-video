---
status: done
---

# F0029 intro v3 visual pass

Reworked `film/intro_v3/` around one large right-stage hero per beat. Vachana stays around x=560 on live, slowly drifting footage. The panel, voice-driven waveform, word-timed baseline, curved message bubble, layered Android phone, notification, and fully contained glass circle now use larger type and deeper glass. Gold is applied to the Bluetooth icon and glow; the other authored graphics are neutral. The phone screen comes from the private F0029 home image, which is not in Git.

The camera needed a tighter crop than the requested 1.10 scale to keep its right edge covered after shifting Vachana to x=560. The right side has a soft dark gradient. No source frame is held.

The 13.8 s duration, beat timing, `film/captions/v3/intro.json`, prepared voice, sfx, and final full-card markup and position are unchanged. `build.py` now reads `local/private-in/F0029/home.png`; `render.cmd` remains the delivery render entry point.

## Review stills

Nine 1920×1080 stills and a sheet with each frame 480 px wide are in `results/F0029/preview/` under the same names as F0023.

| Still | Hero; 480 px read; judge reaction |
| --- | --- |
| `01-panel.jpg` | Vachana name and team panel; all three lines read; yes, the panel has weight beside her. |
| `02-waveform.jpg` | White, voice-shaped waveform; reads immediately; yes, it fills its glass stage. |
| `03-typing.jpg` | Words rising from the bright baseline; the current words read; yes, the words have a clear focal point. |
| `04-card-flight.jpg` | Locked message bubble; its text reads on pause; yes, it has a distinct path into the phone. |
| `05-phone-banner.jpg` | Android phone and dropped notification; notification reads, app controls are secondary; yes, the device has depth. |
| `06-two-crossed.jpg` | Full glass circle, phone, and first two strikes; the network idea reads; yes, nothing clips the frame. |
| `07-four-crossed.jpg` | Four neutral strikes against the gold Bluetooth icon; the distinction reads; yes, the hierarchy is clear. |
| `08-circle-growth.jpg` | Expanding glass-to-card transition; its shape and caption read; yes, the growth carries the scene to the join. |
| `09-full-card.jpg` | `How the app works` full card; title reads; yes, it is clean and identical in layout to the join. |

## Outputs and checks

- `results/F0029/preview/intro_v3-540p.mp4`: 960×540, 13.800 s, H.264/AAC, 4.42 MB.
- `RENDERS:F0029/intro_v3-preview-1080.mp4`: local 1920×1080 render used to make the preview.
- `RENDERS:F0029/final-snapshots/`: local full-resolution PNG captures.
- `hyperframes.cmd check .`: passed; 0 lint/runtime/layout/motion issues; 13/13 contrast checks passed.
- `git diff --check`: passed. Caption and timeline files have no diff.

The brief packet-flight beat is short by the approved timing; its text is easiest to inspect in the full-resolution still. The home screenshot is required again as `local/private-in/F0029/home.png` on any other render machine.

## Files moved out of git by the listener

- `film/intro_v3/assets/camera.mp4` (25.2 MB) was too big for git. Moved to local path: `RENDERS:F0029/film/intro_v3/assets/camera.mp4` (inside renders_dir on vivek-pc)
