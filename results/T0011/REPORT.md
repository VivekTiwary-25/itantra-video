---
status: done
---

Built `mapcard/`, a 1920×1080, 3.5-second HyperFrames composition using a local GSAP copy. It draws the NIE North campus boundary and roads from the supplied OSM data, with campus building outlines from the supplementary trace. Vachana and Yash use the specified coordinates. Their straight-line haversine distance is 190.4 m, rounded to **about 190 m**. The thin connecting line draws on before the distance label appears.

`hyperframes.cmd check` passed with 0 lint, runtime, layout, and motion issues; all 28 text contrast checks passed. Stills are `preview/frame-00-at-1.3s.png` and `preview/frame-01-at-3s.png`. Both were visually inspected.

The CSS requests Segoe UI Variable with `local()` and falls back to Segoe UI. Snapshot generation reported that Segoe UI Variable was unavailable on this machine; no font file is bundled. The composition loads no external assets.
