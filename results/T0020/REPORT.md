---
status: done
---

# T0020 lip-sync audit

Made `sync_audit.md` and `sync_audit.json`, with all 2 s sliding-window correlation results, confident-window offsets, phrase times in video coordinates, and the opening word timings for normalpart6. `measure.js` reproduces the analysis from local footage without saving or committing audio.

Confirmed median offsets: normalpart6 -0.37050 s (6.00 ms confident-window range), sospart1 +4.27100 s (0.25 ms), sospart2 +0.06600 s (0.00 ms at 4 kHz resolution). Normalpart6's T0003 “Oh” interval starts 0.37050 s before video zero, leaving only 0.00950 s inside the picture. The clean sospart2 track extends 5.99082 s beyond its video, although all transcribed speech ends inside it.

Notes: Low-ratio windows are listed but excluded from the median and spread. Word timings come from T0003 and retain its uncertainty around the opening “Oh.” No footage or audio was copied into the result.
