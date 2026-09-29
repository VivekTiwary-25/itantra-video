---
status: done
---

1. **Command availability and versions**
   - `ffmpeg`: not found (PowerShell command-not-recognized error).
   - `ffprobe`: not found (PowerShell command-not-recognized error).
   - `hyperframes`: found in a user-profile folder; invocation blocked because running scripts is disabled. No version output.
   - `node`: OK, `v24.19.0`; location kind: Program Files.
   - `python`: not found (PowerShell command-not-recognized error).
2. **Audio duration via ffprobe**: failed; `ffprobe` is not recognized by PowerShell.
3. **ffmpeg render to RENDERS_DIR**: failed; `ffmpeg` is not recognized by PowerShell.
4. **Temp checks**: TEMP ends with `local\tmp`: no. TMP ends with `local\tmp`: no. Writing `temp-ok.txt`: OK. ffmpeg render to TEMP: failed; `ffmpeg` is not recognized by PowerShell.
5. **HyperFrames checks**: `hyperframes --version` and `hyperframes doctor` could not run; PowerShell blocked the `hyperframes.ps1` shim because script execution is disabled. Doctor check names unavailable.
6. **Report**: written to `results/X011/REPORT.md`.
