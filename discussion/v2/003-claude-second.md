# v2 review: scene 2 (`film/scene2/v2/`, T0032) — pre-review against the spec

From: claude-second (T0041). T0032 hadn't landed in git when I wrote this. These are the checks and numbers the helper should apply when building scene 2 v2, taken from the spec and the source media. I'll add a code review if T0032 lands before I finish.

**1. Yash's opening "Oh" is probably the director's "go". Recommend leaving it out.**
- `results/T0003/clean__Normalpart6.json` has "Oh," at clean 0.00-0.38. Clean-audio energy shows one burst at 0.1-0.3 s, then nothing until "it's" at 1.60 s.
- With the confirmed offset of -0.3705 s, that burst is at video -0.17 s, *before the camera started*. It's also 1.4 s before the rest of the line.
- Recommended window for his first line: clean **1.68 → 3.02** ("it's" - 0.12 to "here." 2.72 + 0.30), i.e. video 1.31-2.65.
- If Vivek hears that it really is Yash saying "Oh", use 0.00 → 3.02 instead. That's a one-number change.

**2. Rule B windows** (clean-audio seconds, from T0003 word timings):

| Line | Window |
|---|---|
| normalpart1 "Hey dude…where are you?" | **4.83 → 9.83** (words 4.95-9.53). The "go" burst at clean ≈0.6 s is outside. |
| Normalpart6 "I'm in the garden. I'll come to you." | **8.48 → 10.94** (words 8.60-10.64; speech energy actually ends ≈10.15, so there's plenty of tail) |

Place each so its first word lands where the spec says:
- Vachana: her first word at slot `ptt_down` (0.08), matching camera src = slot + 4.80 (video 4.88).
- Yash: "I'm" at `yash_app.ptt_down` + 0.1.

**3. Sync numbers to verify in `timeline.json`:**
- bench: normalpart1 full frame src 0.0-4.3, with no push-in.
- Split in over src 4.3-4.8.
- `vachana_send` camera src = slot + 4.80. The camera ends at src 10.83 (slot 6.03); hold the last frame with the 2 % push to 13.13.
- `sent` sound at slot 11.98. Freeze 3.6 s, with N1 at freeze + 0.2.
- Yash: `yash_before_notification` ends 0.3 s after "here." (video 2.35 + 0.3 = 2.65, i.e. src 0-2.65). The notification sound comes at the cut.
- In `yash_app`, the camera continues from src 2.65, then holds with the slow push while the TTS plays (`play_at` + 0.15). His line "I'm" (video 8.23) must land at `ptt_down` + 0.1, so resume the camera at `ptt_down` + 0.1 - (8.23 - resume_src), and don't play it through at real speed from 2.65.
- `sent` at `yash_app.sent_at`.
- Scene 2 **ends on `sonar_b` + a 0.5 s hold**: no fade, no N4, no `vachana_reply`.

**4. Framing** (split panel x 0-1232):
- Yash at the hedge (normalpart6) is roughly centred in the source (x ≈ 560-1260; checked on a frame at src 5 s). `object-position: 50% center` shows src 344-1576 and keeps him whole.
- Vachana on the bench (normalpart1): **I could not verify this on real frames.** My shell tools were down while I wrote this note. Choose `object-position` from the stills of src 4.8-10.8 so she and the phone sit clear of the right-hand 24 px feather.

**5. The walk:** `build.py` must re-link or re-create `assets/walk.mp4` on every run (the vivek-pc listener moves it away) and verify every `<video>` asset exists and covers its declared duration **before** rendering. Scene 3 v2's `write_page()` already does this at the end: copy that pattern. Render the picture once and mux both mixes from it.

**6. Rules:**
- Nothing red in scene 2: the scene 3 red palette must not leak in, and the notification sound is `RENDERS:sound/notify.wav` at -9 dB, `sent.wav` at -10 dB.
- Music only under the sonar section, as a separate stem.
- The same missing-slot guard as scene 3 note 002 point 1: no invented UI in the final picture.
