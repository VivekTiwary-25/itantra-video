---
status: done
---

Made `scene1.srt` with 25 short captions timed from the clean-audio word timestamps through the scene 1 segment cuts. Corrected `chmod 777`, `iTantra`, and `STT aided`. The SRT ends with the final spoken word before the doorway.

Made `scene2_lines.json` with Vachana's line, Yash's two lines, and the four narration lines specified in T0007. It contains text and speaker labels, with no speculative timing.

Proposed the bottom-center caption treatment in `style.md`. Its two-line block clears the scene 1 top and right panels.

Checks: 25 SRT cues have increasing, non-overlapping times; every text line is at most 42 characters; the scene 2 JSON parses and contains seven lines.

Note: `brief/style.md` does not exist yet. The proposal uses the colors and local Segoe family already present in the scene 1 composition. Scene 1 part 1 has a short internal cut during “TTS”, and part 2 has cuts during “convert” and “sent”; captions are split at those cut boundaries.
