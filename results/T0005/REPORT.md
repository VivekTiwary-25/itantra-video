---
status: failed
---

T0005 could not render narration. SAPI speech synthesis failed on the first line with `0x80045040`; a direct SAPI test also returned `Access is denied` during `Speak`. `System.Speech` could not initialize its output device, and OneCore/WinRT returned `Internal Speech Error`. No valid WAVs or durations were produced, so `narration.json` was not written.

Installed voices found:

- SAPI: Microsoft David Desktop, Microsoft Zira Desktop (both English, United States).
- OneCore registry: Microsoft David, Microsoft Mark, Microsoft Zira (all English, United States). OneCore `AllVoices` enumeration failed in this session.
- No English (India) voice was found.

Made `tts.ps1`, a local only SAPI and ffmpeg script for the four exact lines. It is ready to rerun in a Windows session where speech synthesis works; its output target is `RENDERS:scene2/narration/`.
