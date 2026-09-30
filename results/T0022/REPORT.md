---
status: failed
---

# T0022 quality checker

Made `film/final/qc.py`, a standard-library Python command that writes a readable pass/fail table and a JSON report. It checks streams, dimensions, codec, constant frame timing, duration sync, integrated and 10 s short-term loudness, true peak, black and flat frames, frozen holds, silence, full-scale audio samples, channel balance, and the scene 2 placeholder card by fixed colour/layout. Frozen holds are reported for review; all other planted defects fail.

Made five 4 s synthetic previews, each under 250 KB, in `results/T0022/preview/`: `good.mp4`, `black_gap.mp4`, `silence.mp4`, `too_loud.mp4`, and `placeholder.mp4`.

## Test evidence

| Preview | Planted condition | Direct FFmpeg measurement / layout check | Expected QC result |
|---|---|---|---|
| `good.mp4` | none | H.264 yuv420p 1920x1080 30 fps; AAC 48 kHz stereo; -16.03 LUFS, -15.12 dBTP | PASS |
| `black_gap.mp4` | black interval | `blackdetect`: 1.000 to 2.033 s; `freezedetect`: 1.000 to 2.033 s | FAIL: black and flat frames; freeze reported |
| `silence.mp4` | audio muted | `silencedetect`: 1.003 to 3.008 s (2.005 s) | FAIL: silence |
| `too_loud.mp4` | +12 dB gain | `loudnorm` input: -4.01 LUFS, -3.04 dBTP | FAIL: loudness |
| `placeholder.mp4` | scene 2 slot card | At 1 and 2 s, the sampled portrait panel has 99.4% background-colour pixels and 12 centred grey sampled pixels; at 0 and 3 s it has neither | FAIL: placeholder at 1 and 2 s |

The machine has no callable Python runtime (`python` and `py` are unavailable, and a local search found no accessible `python.exe`). Therefore I could not run `qc.py` on these previews, produce its JSON reports, or verify that the clean clip passes. The task's test condition remains unmet; this is why the status is `failed`.

Exact commands to complete the check on a machine with Python, from the repository root:

```text
python film/final/qc.py results/T0022/preview/good.mp4 --report results/T0022/good.json
python film/final/qc.py results/T0022/preview/black_gap.mp4 --report results/T0022/black_gap.json
python film/final/qc.py results/T0022/preview/silence.mp4 --report results/T0022/silence.json
python film/final/qc.py results/T0022/preview/too_loud.mp4 --report results/T0022/too_loud.json
python film/final/qc.py results/T0022/preview/placeholder.mp4 --report results/T0022/placeholder.json
```

The code was adjusted for this machine's FFmpeg build: `-fps_mode passthrough` is used, because `-vsync` is not supported. The picture filter chain and individual FFmpeg detectors were exercised directly.
