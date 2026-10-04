---
status: failed
---

F0005 cannot be completed on this clone because the required offline speech tools are absent. `local/models/faster-whisper-medium.en`, `local/models/rnnoise/cb.rnnn`, and `local/models/rnnoise/sh.rnnn` are missing, and `faster_whisper` is not installed in the available Python runtime. The full prep command stops at the missing ASR model before it can produce verified words. I did not infer speech or screen text from the provisional transcript.

Made `film/intro_v3/prep.py`, which reads the machine configuration, measures clean-audio/camera offset, and contains the specified offline word-timing and scene-1 voice-chain preparation for a machine with those dependencies. Its `--alignment-only` path ran successfully; Python syntax validation passed.

Measured offset: clean-audio time maps to camera time as `camera = clean - 0.7781 s`. The normalized band-limited waveform cross-correlation peak is `0.25430` (250–3000 Hz, 8 kHz analysis). The camera take is 13.268889 s, 3840×2160, about 30 fps, and BT.709 SDR. The separate clean audio is 15.296325 s. I inspected frames near camera seconds 1 and 7; Vachana is near the centre, so the final right-side layout needs an adjusted crop and a visual check.

No verified `words.json`, cleaned `voice.wav`, `envelope.json`, captions, HyperFrames composition, sound stem, beat previews, or render were produced. Her last spoken word and the available moving-camera window remain unverified. `home.png` was not copied or committed.
