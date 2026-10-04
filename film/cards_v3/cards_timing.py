"""Single source of the cards timeline, computed from film/common/narration_v4.json (never hard-coded).

Used by build.py (writes assets/timing.js + film/captions/v3/cards.json, patches data-duration),
cards_dx.py (N8/N9 stem) and cards_sfx.py (stem length).

    works card readable      READY_NOW   = 2.45 s (items 0.30-1.80, COMING NEXT settled by 2.45)
    N8 starts                N8_START    = READY_NOW + 0.5
    works card hold          SWAP_START  = max(8.0, N8_START + N8 + 0.4)
    glass transition         SWAP_START .. SWAP_END = SWAP_START + 0.35   (closing card readable at SWAP_END)
    N9 starts                N9_START    = SWAP_END + 0.3
    fade to black starts     BLACK_START = N9_START + N9 + 1.0
    segment length           END         = BLACK_START + 1.0
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MANIFEST = REPO / "film/common/narration_v4.json"

READY_NOW = 2.45
MIN_WORKS_HOLD = 8.0
SWAP_LEN = 0.35
FADE_OUT = 1.0


def load():
    lines = json.loads(MANIFEST.read_text(encoding="utf-8"))["lines"]
    n8, n9 = lines["N8"], lines["N9"]
    d8, d9 = float(n8["duration"]), float(n9["duration"])
    n8_start = READY_NOW + 0.5
    swap_start = max(MIN_WORKS_HOLD, n8_start + d8 + 0.4)
    swap_end = swap_start + SWAP_LEN
    n9_start = swap_end + 0.3
    black_start = n9_start + d9 + 1.0
    end = black_start + FADE_OUT
    r = lambda x: round(x, 3)
    return {
        "n8": {"start": r(n8_start), "end": r(n8_start + d8), "duration": d8, "text": n8["text"], "file": n8["file"]},
        "n9": {"start": r(n9_start), "end": r(n9_start + d9), "duration": d9, "text": n9["text"], "file": n9["file"]},
        "swap_start": r(swap_start), "swap_end": r(swap_end), "black_start": r(black_start), "end": r(end),
        "ticks": [0.30, 0.80, 1.30, 1.80],
    }


if __name__ == "__main__":
    print(json.dumps(load(), indent=1))
