---
status: done
---

Built `mapcard_landscape/` from the accepted v1 with the dashed OSM college boundary removed. The roads and traced campus buildings/features remain. Built `mapcard_portrait/` at 1080×2400, 3.5 seconds, 30 fps, framed around Vachana, Yash, and the campus cluster. It uses the same neutral map and animation, with 48 px marker labels and the distance label appearing after the line draws.

`hyperframes.cmd check` passed for both compositions: 0 lint, runtime, layout, or motion issues; 28/28 contrast checks passed in each. The 3.0 s stills were inspected and saved as `preview/landscape-3s.jpg` (960×540) and `preview/portrait-3s.jpg` (540×1200).

From `results/S0001/mapcard_portrait/`, render with:

```powershell
hyperframes.cmd render -q looks -f 30 -o ../../../local/renders/scene2/app/maps_fallback.mp4
```

No MP4 was produced here. HyperFrames' render preflight could not start the installed Chrome binary for its version check. The browser did work for both composition checks and snapshots. Segoe UI Variable is requested through `local()`; the stills on this machine used the Segoe UI fallback. No font file or external asset is bundled.
