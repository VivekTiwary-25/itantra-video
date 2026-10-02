---
status: done
---
# P0106 report (claude-second)

Files are in `local/private-out/P0106/` (local only, not committed).

| File | What it is | Word count |
|---|---|---|
| `diagram.py` | Two functions: `draw_title_art` and `draw_references` | `draw_title_art` draws 12 words; `draw_references` draws 98 words |
| `make_test.py` | Builds `test.pptx` and checks every shape is inside its area | — |
| `test.pptx` | 2 slides, one per function, at the task's area sizes | — |
| `notes.md` | Area sizes, word counts, the fact mapping, the takeaway lines and placement notes | 386 words |

Checks:
- `make_test.py` passes: every drawn shape is inside its area.
- `test.pptx` reopens.
- Native shapes only, no pictures.
- The required title fields are not touched.
- The reference numbering is unchanged.

No open questions.
