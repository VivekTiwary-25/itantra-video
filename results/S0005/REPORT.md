---
status: done
---

# S0005 — title card render

Rendered `RENDERS:title/title_raw.mp4` and final `RENDERS:title/title.mp4`. The final file is 20.000 s, 1920×1080, 30 fps, H.264 with a 48 kHz stereo AAC tick stem. AAC was encoded with a 256 kb/s target; the sparse stem measures about 9 kb/s in the file. Decoded ticks peak at −24.0 dBFS. No music or whooshes.

| Line | Start | Preview |
|---|---:|---|
| 1 — We built iTantra so you can reach people over long distances, even with no cell network. | 0.6 s | `preview/line-01.jpg` |
| 2 — Speak in any of 10 languages, and your message is read aloud on the other side. | 4.0 s | `preview/line-02.jpg` |
| 3 — It travels phone to phone, through the people around you, across ~400 m of campus. | 7.4 s | `preview/line-03.jpg` |
| 4 — No towers. No internet. No new hardware. Just the phones people already carry. | 10.8 s | `preview/line-04.jpg` |
| 5 — iTantra. Speak. Send. Be heard. | 14.5 s | `preview/line-05.jpg` |
| 6 — Team chmod 777 · Team ID 148903 · NIE Mysuru | 14.5 s | `preview/line-06.jpg` |

Ran `build.py`, `make_sfx.py`, and `hyperframes.cmd check`. Check passed with no lint, runtime, layout, or motion issues; contrast was 7/7. Inspected all six rendered stills against the approved wording. Segoe UI Variable is installed and named correctly; no font fallback was observed.
