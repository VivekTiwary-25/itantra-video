F0005 ended with **status: failed**. The required offline Whisper model, `faster_whisper` package, and RNNoise models are missing on this clone, so I could not verify Vachana’s words or build the word-timed intro without guessing.

I wrote [prep.py](<REPO>/film/intro_v3/prep.py) and the required [REPORT.md](<REPO>/results/F0005/REPORT.md). The alignment-only check passed: clean audio maps to camera time with a **−0.7781 s offset** and a **0.25430** correlation peak. No voice render, captions, composition, or beat previews were produced.

**TLDR:** The measured alignment is recorded; the intro needs the missing offline speech tools before it can be completed.