---
status: done
---

Generated three photoreal teardown layers with the built-in `image_gen` tool, using the first layer as the silhouette and lighting reference for the others. The common prompt specified one unbranded graphite Android phone, a 30-degree three-quarter top view with a 20-degree turn, upper-left studio light, a subtle rim light, no text or logos, and transparent alpha. Layer-specific prompts requested the black front glass, exposed mid-frame components, and matte back cover with a generic vertical two-lens camera bar. I regenerated the back to remove an Apple-like square camera arrangement.

Full-size deliverables are in `local/private-out/F0030/` and copied to:

- `RENDERS:exploded_v2/layer_screen.png`
- `RENDERS:exploded_v2/layer_mid.png`
- `RENDERS:exploded_v2/layer_back.png`
- `RENDERS:exploded_v2/stack_preview.png`
- `RENDERS:exploded_v2/parts_check.jpg`

The result folder contains 960 px JPG previews of all four images, `parts_check.jpg` at 960 px, and `parts.json` with six pixel-coordinate callouts on `layer_mid.png`.

Notes: The generator returned 1024 × 1536 images with transparent alpha; I enlarged them with Lanczos filtering to 1366 × 2048. The phone outlines, angle, and scale match closely, though independently generated edges differ slightly and may need a small registration adjustment for animation. The part boxes are visual callouts on generated art, not a hardware engineering diagram.
