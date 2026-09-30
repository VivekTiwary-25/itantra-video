# scene2: hand-back to lead (claude-second)

From: claude-second

Handing scene 2 back to you.
- **Drafts:** both drafts from T0007 render (98.1 s, all five slots are placeholder cards).
- **S0003 (codex-vivek) is running.** It's looking for the missing `vachana_send` raw take (it wasn't at `RENDERS:scene2/app/vachana_send.mkv`) and re-rendering both drafts with the maps fallback card.
- **New tool:** `film/scene2/main/prep_slot.py` preps any scrcpy recording into a slot (top 110 px crop, trim, 30 fps, no grade). The commands are in `results/S0002/REPORT.md`.
- **Listener quirk:** it moves `assets/walk.mp4` out after every task, so always run `build.py` before rendering.

What's left, and the questions for Vivek, are in `results/T0008/REPORT.md`.
