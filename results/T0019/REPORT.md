---
status: done
---

# T0019 — bench push-in comparison

Six 1920×1080 JPG stills are in `preview/`: each candidate at scene 7.367 s and 7.667 s (source 4.367 s and 4.667 s). They use `GRADE_V1`, Lanczos enlargement, and light post-scale unsharp. The 2.2× ending previews a 0.5 s dissolve beginning at 7.4 s against the current app placeholder layout; its final still is about 53% dissolved.

Recommend **1.8×**. The current 8.5× finish stretches about 226×127 source pixels over the full frame; 1.8× retains a roughly 1067×600 crop, including her face, hand, and phone, with a much cleaner image. The 2.2× option is also clearer but cuts her face at the top and gives the placeholder transition more visual weight.

`pushin.patch` gives the exact one-line change to `film/scene2/main/index.html.tpl`; the lead can apply it and regenerate the composition with `build.py`. `generate.js` reproduces the stills from local footage. The preview's light unsharp is for comparison only; the recommended film change is the 1.8× endpoint.
