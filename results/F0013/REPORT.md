---
status: done
---

Updated `film/scene2/v3a/overhead/` with 40 px semibold glass pin labels, 22 px haloed dots, and a 44 px glass distance panel beside the route's middle. The map now centres the pins about 762 px apart while retaining surrounding campus buildings. The seven stills and a sheet with each frame at 480 px width are in `results/F0013/preview/`.

The dashed route now follows the shortest connected `highway` path in `film/scene2/geo/nie_north_osm.json`, revealing from Vachana to Yash. Measured straight line: **190.40 m**. Measured walking route: **307.07 m** total, including **10.37 m** of short pin-to-road connectors (OSM ways: **296.70 m**). The on-screen wording remains exactly `~300 m, walking distance`.

`hyperframes.cmd check` passed: zero lint, runtime, layout, and motion issues; all nine contrast checks passed. The 5.0 s endpoint still resolves to the prepared Yash still (frame comparison: PSNR 50.48 dB against that JPEG). No source footage is included in the result.
