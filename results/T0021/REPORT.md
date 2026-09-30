---
status: done
---

## Made

- `film/captions/captions.json`: 44 timed captions across three scenes (25 / 10 / 9), with scene, start, end, text, and position. It also contains all editable planned scene 3 segment starts and the provisional SOS `vachana_listen_at` value.
- `film/captions/build.py`: validates the data and regenerates three 1920×1080, 30 fps transparent HyperFrames compositions and `scene1.srt`, `scene2.srt`, `scene3.srt`. Each composition uses a local GSAP copy and Segoe UI Variable through `local()`.
- `film/captions/scene1/`, `scene2/`, `scene3/`: separate optional overlays. Scene 1 captions sit below the top and right panels. Captions during the centred app phone sit on the left, outside x=717–1203. Other cues sit at bottom centre.
- Nine 1920×1080 caption previews on mid-grey in `results/T0021/preview/` (three per scene).

## Turn captions on

After the scene picture and timing are locked, run `python film/captions/build.py`. Render each overlay as alpha WebM, for example `hyperframes.cmd render --format webm -f 30 -o local/renders/captions/scene1.webm film/captions/scene1` from the repo root. Composite the matching WebM at (0,0), starting at scene time 0, over each scene picture before the final concatenation. For a film without captions, leave these overlays out. The SRTs are also available for a subtitle-track export.

## Checks and notes

- `hyperframes.cmd check` passed for all three compositions: 0 lint, runtime, layout, and motion issues. Snapshots have an alpha channel; the nine previews composite them over grey.
- No unresolved collision in the planned layouts. The left-side boxes end before the centred phone begins, and scene 1 boxes start below y=830. Recheck against the final app recordings if their layout changes.
- Scene 3 still uses the lead's placeholder slot lengths. The SOS caption start at 4.271 s assumes `vachana_listen_at` = 0.171 s into the slot, derived from the supplied clean-audio offset. Update the numeric starts, ends, segment starts, and scene duration in `captions.json` when those slots are finalized, then rebuild and recheck.
- `brief/style.md` does not exist yet, so the approved T0009 proposal and the existing scene 1 local font treatment were used.
- This machine has no Python executable available. Generated files were made from the `build.py` HTML template with a temporary local Node runner; the generated compositions were checked by HyperFrames. Run `build.py` on a Python-equipped machine after any data edit.
