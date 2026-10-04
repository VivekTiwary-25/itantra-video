---
status: done
---

Regenerated only the back-cover layer with the built-in `image_gen` tool. It shows the inside face: matte graphite, a thin raised rim, and restrained adhesive/foil detail. It has no camera hardware, holes, coil, text, or logo.

Outputs:

- `RENDERS:exploded_v2/layer_back.png` — 1366 × 2048 RGBA, Lanczos-upscaled from the generated 1024 × 1536 image.
- `local/private-out/F0034/layer_back.png` — identical master.
- `results/F0034/stack_preview.png` — new three-layer preview using the accepted F0030 screen and mid-frame.
- `results/F0034/layer_back.jpg` and `results/F0034/stack_preview.jpg` — 960 px previews.
- `results/F0034/alignment_overlay.jpg` — 50% opacity overlay of the back and mid-frame at master size, downscaled for review.

Using the available `results/F0030/layer_mid.jpg` fallback as the reference, I compared the four outer silhouette corners at 1366 × 2048. The back differs from the mid-frame by approximately **3, 2, 4, and 11 px** respectively (top-left, top-right, bottom-left, bottom-right). The JPEG-derived silhouette and anti-aliasing make these approximate values. The layer orientation and scale match without an additional registration transform.

Image-generation prompt: use the F0030 mid-frame as a strict silhouette, perspective, scale, position, and lighting reference; render only the removable back cover from its inside face with graphite materials and a thin rim; transparent background; exclude camera features, coil, text, logos, branding, and other layers.
