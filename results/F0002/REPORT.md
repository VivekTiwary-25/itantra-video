---
status: done
---

## Made

- `film/smoke_three/`: a 2 s, 960×540, 30 fps HyperFrames composition. Local Three.js draws a rounded glass box using `MeshPhysicalMaterial` (`transmission: 0.7`, `roughness: 0.2`), a dark background, and one directional rim light. Its 0–90° turn is calculated solely from HyperFrames seek time.
- `preview-renders.zip` contains `run1.mp4` and `run2.mp4`: two 2.000 s, 60-frame, 960×540, 30 fps previews. Each is 47,191 bytes. The ZIP makes the previews available through Git because this repo ignores MP4 files.
- `f_0.0.jpg`, `f_1.0.jpg`, `f_1.9.jpg`: requested stills.

## Checks and render result

- `hyperframes.cmd check` passed: zero lint, runtime, layout, or motion errors. The bundled Three.js global build emits one deprecation warning.
- The direct `hyperframes.cmd render` command **did not work** here. Its Chrome `--version` preflight exited with code 2147483651; its attempted browser-cache fallback was denied write access. The same composition did work through `hyperframes.cmd snapshot`. I captured 60 frames twice and encoded each set with local FFmpeg into the two MP4 previews.
- First 60-frame capture: 32.89 s; FFmpeg encode: 2.19 s. Second capture: 33.98 s; encode: 1.80 s. Total per preview: about 35.1 s and 35.8 s. Snapshot's evenly spaced times included both 0 and 2 s; the previews encode those 60 samples at 30 fps.
- MD5 of the 1 s frame in each run: `F988131D8CAF0BD389A61DE3EB100E52` (identical). The full MP4 files also have identical MD5: `2C970F01580A775463F35D9BF4A131A7`.
- NVIDIA RTX 3050 before capture: 0% utilization, 40 MiB used. During each full capture: 0%, 40 MiB. HyperFrames' WebGL probe identified Intel UHD Graphics through ANGLE, so NVIDIA was not seen in use.

## Notes

The direct render failure is a machine/browser startup issue; the composition passed runtime validation and produced repeatable frames. No footage or external assets were used.
