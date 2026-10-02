---
status: done
---
# P0104r1 report (claude-second)

This redoes P0104. The first attempt left nothing to continue from: its worker's shell never started. The inputs are in `local/private-in/P0104/`, and the files are in `local/private-out/P0104/` (local only, not committed).

| File | What it is | Word count |
|---|---|---|
| `diagram.py` | Two functions: `draw_risks` and `draw_feasibility` | `draw_risks` draws 103 words; `draw_feasibility` draws 39 words |
| `make_test.py` | Builds `test.pptx` and checks every shape is inside its area | — |
| `test.pptx` | 2 slides, one per function, at the task's area sizes | — |
| `notes.md` | Area sizes, word counts, which candidates were kept or dropped, the fact mapping and the takeaway lines | 423 words |

Checks:
- `make_test.py` passes: every drawn shape is inside its area.
- `test.pptx` reopens.
- Native shapes only, no pictures.
- No cell is over 12 words.

No open questions.
