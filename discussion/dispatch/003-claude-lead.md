# Lead → dispatcher (17:20): distance is now "~300 m"

Vivek gave the real walking distance: about 270-300 m. **Use "~300 m" on the title card and the map card** (map label: "walking distance"). This replaces the "~200 m" in note 002.
- Map card: the lead's helper is re-rendering `RENDERS:scene2/app/maps_fallback.mp4` from `film/scene2/mapcard/` now; scene 2 must be re-rendered after it lands.
- Title: `DISTANCE = "~300 m"` in `film/title/build.py`, then re-render `RENDERS:title/title.mp4`.
- T0030 started before this decision, so T0031 (queued right behind it for codex-vivek) applies "~300 m" to the title and scene 2, checks the scene 3 slots use the re-recorded SOS clips, and reassembles. Please do not queue the same work twice; if you have an S-task doing any of it, say so in `discussion/dispatch/`.
- Vivek reset the usage limits: go full speed. codex-f1 and codex-f2 are idle right now: give them the real work that is left (scene 3 sonar pieces, reviews of landed results, anything T0025's audit marked must-fix).
