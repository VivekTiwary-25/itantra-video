---
status: done
---

Measured all six clean-audio/video pairs and wrote `sync.json`, a plain-language table and verdicts in `sync.md`, and the reproducible `sync.py` script.

Five pairs show meaningful first-to-last offset differences or another alignment caveat. In particular, normalpart6, sospart1, sospart2, and vachna part1 have 196–466 ms differences, so their whole-pair offsets are anchors rather than safe full-clip replacements. Normalpart1 has a clear speech-energy peak but little waveform coherence and merits manual verification. Vachna part2 is stable within 6 ms.

The script reads the footage location from `$FOOTAGE_ROOT` or `machine.local.json`, uses installed ffmpeg/ffprobe and Python's standard library, and leaves decoded PCM only in ignored `local/tmp/T0002/`. No footage or audio source was copied into the results.
