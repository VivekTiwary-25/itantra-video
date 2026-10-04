---
status: failed
---

F0022 could not be completed in this worker session. The offline Whisper and RNNoise model files are present, but `python` is unavailable to the worker shell. The Python executable recorded in `local/python.txt` is outside this session's readable sandbox, so `film/intro_v3/prep.py` cannot run. Its required word-timed transcription, voice comparison, cleaned voice, and envelope therefore remain unverified and unproduced.

I checked the local fallback: FFmpeg includes a whisper.cpp transcription filter, but it requires a whisper.cpp model. The supplied `local/models/faster-whisper-medium.en/model.bin` is a faster-whisper/CTranslate2 model, and no whisper.cpp model is present. Using the provisional transcript for captions or timed graphics would risk putting words on screen that Vachana did not say, contrary to the task.

No composition, captions, previews, sound stem, or render were made. The previous measured alignment (`camera = clean - 0.7781 s`, correlation peak `0.25430`) was not reconfirmed. The private home screen and source media were not copied into tracked outputs.
