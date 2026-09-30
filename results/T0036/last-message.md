T0036 is marked **failed** in [REPORT.md](/<REPO>/results/T0036/REPORT.md): this machine has no callable Python interpreter, so I could generate the synthetic inputs but could not run the end-to-end test.

I wrote [prep.py](/<REPO>/film/narration/prep.py) and the [synthetic test](/<REPO>/results/T0036/synthetic_test.ps1). No voice switch or media files were written. On vivek-pc, run the synthetic test, then run `python film/narration/prep.py` from the repo root.

TLDR: The prep tool is written; its required end-to-end verification remains open.