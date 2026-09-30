---
status: failed
---

# Narration prep

Made `film/narration/prep.py` and `results/T0036/synthetic_test.ps1`. The prep command reads N1, N2, N3, N5 and N6 takes from `local/narration_vivek/`; detects clipped takes; uses scene 1's `CHAIN` with a loud warning and both RNNoise steps removed when its models are absent; trims edge silence; applies at most `atempo=1.06`; normalizes to -18 LUFS; and writes WAVs plus `report.json` under `RENDERS:narration/vivek/`. It changes `film/common/narration.json` only after all five usable outputs are made. The test script uses a separate output path and cannot change that switch.

Exact production command on vivek-pc, from the repo root:

```text
python film/narration/prep.py
```

The synthetic test generated six inputs with FFmpeg: five speech-like lines plus a clipped alternate N1 take, including long edge silence and an N6 over the maximum. It then stopped because `python` is unavailable on this worker machine. The generated media was removed by the test script. Thus the Python program has **not** passed an end-to-end run, so this task cannot be marked done. On a machine with Python, run `results/T0036/synthetic_test.ps1` to execute the fixture assertions before the production command.

No narration files were present here, no voice switch was written, and no media was committed.
