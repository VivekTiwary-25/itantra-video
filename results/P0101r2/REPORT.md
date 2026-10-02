---
status: done
---
# P0101r2 report (claude-second)

This redoes P0101 and P0101r1, which left no output to continue from. The inputs were read from `local/private-in/P0101/`, and the files are in `local/private-out/P0101r2/` (local only, not committed).

| File | What it is | Word count |
|---|---|---|
| `diagram.py` | One function: `draw_journey` | `draw_journey` draws 54 words |
| `make_test.py` | Builds `test.pptx` and checks every shape is inside its area | — |
| `test.pptx` | 1 slide at the task's area size | — |
| `notes.md` | Area size, word count, the step-by-step fact mapping and the takeaway line | 384 words |

Checks:
- `make_test.py` passes: every drawn shape is inside its area.
- `test.pptx` reopens.
- Native shapes only, no pictures.

Open question: the step icons are Segoe UI Symbol glyphs. They need one look in real PowerPoint, which may swap in colour emoji on some machines.
