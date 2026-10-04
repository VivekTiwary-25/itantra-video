---
status: failed
---

# F0040 intro v4

The requested build cannot be completed with the local inputs available on this worker. No intro code, captions, audio, or preview stills were changed.

Audio cross-correlation at 4 kHz, band-limited to 250–3000 Hz, identifies `FOOTAGE:Video/20261002_072612_long_intro_2.mp4` as the camera match for `FOOTAGE:Audio/vachna_south_campus_intro_part_2_take_1.mp3`. Its normalized peak is **0.56663** at camera time = clean-audio time + **0.2525 s**. The other candidate, `FOOTAGE:Video/20261002_073404_long_intro.mp4`, peaks at **0.04142** at an offset of -1.524 s.

Required `local/intro_words/vachna_south_campus_intro_part_2_take_1.words.json` is absent. The fallback specified by the task cannot run: `local/models/faster-whisper-medium.en` is absent, and the local Hugging Face entry contains only a reference, without model files. The scene 1 voice-cleanup chain also cannot run because `local/models/rnnoise/cb.rnnn` and `local/models/rnnoise/sh.rnnn` are absent. These inputs are needed to make verified word-exact captions, the requested clean voice, and lip-synced cuts. `local/private-in/F0040/home.png` and the footage are present.

Provide the word-timing JSON and both RNNoise model files, or the local faster-whisper model and both RNNoise model files, then reassign this task as a new task ID.
