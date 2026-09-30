# scene3: SOS sonar section delivered

From: claude-second

`sos_in` (2.0 s), `sos_sonar` (9.0 s) and `sos_dive` (1.5 s) are built. They pass `hyperframes check` and render at exact lengths. They're in `film/scene3/sonar/` for T0016.

- **Timing:** Vivek's point lights red at 8.00 s. `sos_dive` ends on sospart2 src 2.967, so `lab_a` continues at src 3.0.
- **Sound:** there's an sfx stem per segment and a separate `music/sos_music.wav` (12.5 s), 9 dB lower under N6.
- **`sos_in`:** it uses a placeholder until `RENDERS:scene3/app/vachana_sos_last.png` exists. Then run `python film/scene3/sonar/build.py plates pages` and set `APP_STILL['search_xy']` in `cues.py` to where the "Searching…" element sits.

Details, cue times and open points are in `results/T0014/REPORT.md`, with a 540p preview in `results/T0014/preview/`.
