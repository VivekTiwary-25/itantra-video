---
status: done
---

1. Commands: `ffmpeg` found, version `ffmpeg version 9.0.2-full_build-www.gyan.dev Copyright (c) 2007-2026 the FFmpeg developers` (other); `ffprobe` found, same version line (other); `hyperframes.cmd` found, version `0.8.92` (user-profile folder); `node` found, version `v24.19.0` (Program Files); `python` not found.
2. `ffprobe` duration on the first Audio file: `11.743825` seconds.
3. FFmpeg lavfi output in RENDERS_DIR: OK.
4. TEMP and TMP are set and both end with `local\tmp`: yes. Small write into TEMP: OK. FFmpeg lavfi output in TEMP: OK.
5. `hyperframes.cmd --version`: `0.8.92`. Doctor checks: ✓ Version; ✓ Node.js; ✓ CPU; ✓ Memory; ✓ Disk; ✓ Frames cache; ✓ Archive extractor; ✓ Settings lock; ✓ Environment; ✗ whisper-cpp; ✗ TTS (Kokoro); ✗ BGM (MusicGen); ✓ onnxruntime-node; ✓ @google/genai; ✓ FFmpeg; ✓ FFprobe; ✗ Chrome; ✓ Docker; ✗ Docker running.
6. Diagnostic completed. The doctor command emitted a config access warning; report contains no local paths or user names.
