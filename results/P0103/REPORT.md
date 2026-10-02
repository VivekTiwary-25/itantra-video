---
status: done
---
# P0103 report (claude-second)

Files are in `local/private-out/P0103/` (local only, not committed).

| File | What it is | Word count |
|---|---|---|
| `diagram.py` | Two functions: `draw_stack` and `draw_measured` | `draw_stack` draws 82 words; `draw_measured` draws 28 words |
| `make_test.py` | Builds `test.pptx` and checks every shape is inside its area | — |
| `test.pptx` | 2 slides, one per function, at the task's area sizes | — |
| `notes.md` | Area sizes, word counts, the fact mapping and the takeaway lines | 431 words |

Checks:
- `make_test.py` passes: every drawn shape is inside its area.
- `test.pptx` reopens.
- Native shapes only, no pictures.

No names were missing, so no `(name?)` placeholders were needed.

No open questions.
