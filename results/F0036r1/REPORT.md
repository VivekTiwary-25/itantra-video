---
status: done
---

# F0036r1 - exploded v2 polish

The F0036 attempt committed its composition changes before the worker hit a usage limit. I verified and retained those changes in `film/exploded_v2/index.html` and `README.md`: the 60 px end line has its baseline near y=960; the microphone has a soft ring about 3 times the part size plus a short pulse when its label appears; and the subtle sonar rings have a stronger 2 px stroke and 0.18 peak opacity. The text and beat timings are unchanged.

Rebuilt the staged assets from the real layers in `RENDERS:exploded_v2/` and `results/F0030/parts.json` on this machine. Generated eight 1920 x 1080 beat stills at 0.7, 2.5, 4.2, 6.8, 9.2, 11.6, 14, and 15.7 s in `results/F0036r1/preview/`, plus `contact-sheet-480.jpg` with each frame 480 px wide. Visual review confirms the microphone glow, visible but restrained sonar, and closing line placement.

`hyperframes.cmd check film/exploded_v2` passed: 0 errors, 0 warnings, 0 layout issues, and 8/8 text contrast checks. HyperFrames logged automatic SceneSans font injection and large-image inlining notices; the check and snapshots completed successfully.
