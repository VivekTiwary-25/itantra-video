---
status: done
id: T0053
worker: codex-vivek
machine: vivek-pc
---

Overwrote the three assigned 1280x720 PNGs with the requested T0052 review fixes:

- `thumbnails/v1_vachana_relay_speak.png`: Vachana speaking with her phone directly below her mouth, real campus background on the left, and the existing locked blue capsule mid-hop between two relay phones on the sonar map. Text: "iTantra" and "Speak. Send. Be heard."
- `thumbnails/v2_vachana_relay_nonetwork.png`: the same frame and composition as v1. Text: "iTantra" and "No network. Still heard."
- `thumbnails/v3_vachana_sos.png`: Vachana focused on her phone with a serious, unsmiling expression; the existing red rings expand from one phone on the sonar map. No relay chain, hop lines, or packet. Text: "iTantra" and "No network. Still heard."

Final frames:

| Thumbnails | Footage | Time |
| --- | --- | --- |
| v1, v2 | `FOOTAGE:Video/20261002_081346_short_intro.mp4` | 7.50 s |
| v3 | `FOOTAGE:Video/sospart1.mp4` | 4.25 s |

Reviewed the complete clips at quarter-second intervals: 43 normalpart1 frames, 53 short-intro frames, 42 sospart1 frames, and 42 sospart2 frames. Scored all 180 frames using the existing Laplacian sharpness method, and personally inspected chronological sheets plus each clip's best-eight sheet. The intro selection is its highest-scoring frame (2797.04), with eyes open, mouth open mid-word, and the phone raised immediately below her mouth. The normalpart1 candidates keep the phone lower and include the rejected looking-away pose. The SOS selection scores 2083.83; expression takes priority over the sharper smiling ending frames. Sospart2 shows a different actor, so it was not used.

What changed:

- Removed silhouette extraction, GrabCut, alpha mattes, and the person mask entirely. Both people now come from rectangular RGB crops of full graded footage frames, retaining their real background. Each left photo is 600x720 and fades into black over 260 px, with a slight 12% darkening before the fade. No outlines or new vignette were added.
- Applied the exact existing `GRADE_V1` before cropping. Both selected footage files are SDR BT.709.
- Reserved the top-right for text: the photo ends at x=600, text starts at x=604/611, and all map geometry and markers are clipped below y=330. The tagline ends above that area with a clear dark gap. Repositioned the existing map without changing its camera, phone coordinates, capsule styling, or SOS origin.
- Moved the same crossed-out signal icon to the calm top-right corner so it remains visible against the retained footage background. Its size, opacity, and line styling remain unchanged. Kept the existing SceneSans font, near-white text, 154 px title and 60 px tagline, blue capsule, and red pulse styling.

Updated sources remain in `thumbnails/src/T0052/`, as requested. Rebuild from the repository root:

```text
python thumbnails/src/T0052/frames.py
python thumbnails/src/T0052/build.py
```

The first command recreates candidate scores and review sheets; the second extracts the fixed selected frames, applies the grade, stages local film scripts, snapshots all three compositions with `hyperframes.cmd`, and verifies the PNGs. All dependencies are already local; no network resources are loaded. Footage paths resolve through `machine.local.json`.

Intermediates are under `local/thumbs/T0053/`. The preview is `results/T0053/preview/sheet.png`, showing all three side by side at 320x180. The inherited output section names T0052 result/scratch paths, but this redo's explicit writes list authorizes T0053; the old result and scratch files were left untouched.

Verification passed: all three final PNGs are exactly 1280x720 and under 1 MB; the footage crops are RGB with no alpha channel; v1/v2 differ only in the tagline; the strip between text and map is entirely black. Personally inspected the final small preview and full-size relay/SOS images. Titles and taglines remain readable, and no geometry touches the text. Source checks passed for network URLs, absolute paths, and email addresses. `git diff --check` passed. No film files or other repositories were edited, and no source footage was placed in public output paths.

Composition intent: preserve the existing sonar visuals while making the real speaking pose and focused SOS expression clear, with a soft full-background blend and calm space around the text.

TLDR: All three thumbnails rebuilt; speaking/SOS frames, full-background blending, and text clearance fixed and checked.
