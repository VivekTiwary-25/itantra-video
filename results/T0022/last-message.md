I wrote [qc.py](/<REPO>/film/final/qc.py) and five small synthetic clips. Direct FFmpeg checks confirmed the planted black gap, silence, excessive loudness, and placeholder layout.

**T0022 is marked failed** in [REPORT.md](/<REPO>/results/T0022/REPORT.md) because this machine has no callable Python runtime. I could not run `qc.py` on the clips or verify that the clean clip passes. The report includes the exact commands to finish that check on a machine with Python.

TLDR: The checker is written; its required end-to-end tests remain unverified.