---
status: done
---

# F0032r1 - exploded view v2 with real layers

Staged the accepted real screen and mid-frame layers from F0030 and the revised inside-face back cover from F0034. The composition uses the source images at their portrait aspect ratio. I tuned the layer width and front-glass separation so the named components stay exposed and the glass stays within frame. The microphone, processor, Bluetooth chip, antenna, and loudspeaker leaders use `results/F0030/parts.json` and were checked against the rendered stills.

Changed the part highlights to local, soft glows; only the Bluetooth chip and antenna use gold. Corrected the masked light sweep's travel across the metal board. Placed the closing line below the reassembled phone.

Outputs: `film/exploded_v2/index.html`, `timeline.json`, and `README.md`; eight 1920 x 1080 frames, `preview/contact-sheet-480.jpg` (480 px per frame), and `preview/VERDICTS.md` with a one-line verdict for each beat. The source layers remain at `RENDERS:exploded_v2/layer_screen.png`, `RENDERS:exploded_v2/layer_mid.png`, and `RENDERS:exploded_v2/layer_back.png` and are staged by `build.py` on the render machine.

Verification: `hyperframes.cmd check film/exploded_v2` passed with 0 errors, 0 warnings, 0 layout issues, and 8/8 text contrast checks. The previews use the actual F0030/F0034 layers; no placeholders.
