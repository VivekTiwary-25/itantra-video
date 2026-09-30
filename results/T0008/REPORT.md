---
status: done
---
# T0008: acting lead for scene 2, 12:10-14:00 IST (claude-second)

## Finished
- **Both scene 2 drafts render on vivek-pc** (T0007, codex-vivek, reviewed and accepted):
  - `RENDERS:scene2/scene2_draft_music.mp4` and `RENDERS:scene2/scene2_draft_nomusic.mp4`
  - 1920x1080, 30 fps, 98.133 s, -16.2 LUFS, -1.7 dBTP; `hyperframes check` passes
  - The whole cut list is built: the doorway, "How the app works", the bench push-in, the slot layout with blurred sides, the freeze + N1, the walk ramp, the maps slot, Yash in 8a-8d, the sonar section with N2/N3, the fade + N4, and `vachana_reply`.
  - All five app slots are `APP: <slot>` placeholder cards (review-only).
- **Sonar section (T0004)**: final, and used as delivered inside T0007.
- **Slot prep tool** (S0002): `film/scene2/main/prep_slot.py` turns a raw scrcpy recording into a slot file. It crops the top 110 px (the hotspot pill), trims, converts to CFR 30 fps H.264, and keeps or drops the audio. There's no grade. `build.py` now fits any portrait aspect to full height.
- **Maps fallback** (T0011 → S0001): a neutral drawn map, "about 190 m" straight-line, in landscape and portrait (1080x2400). The portrait version is rendered on vivek-pc as `RENDERS:scene2/app/maps_fallback.mp4`, and `slots.json` `maps` points at it.
- **`vachana_send` alignment worked out from the tap log** (S0002): `--in 1.55`. PTT down lands 0.10 s before her spoken line and PTT up 0.53 s after it. Send is at slot 12.12 s, `sent_at` 12.27, and the slot is 13.133 s long.
- **Reviews written:**

  | Task | Verdict |
  |---|---|
  | T0007 | accepted |
  | T0009 (captions) | accepted |
  | T0010 (scene 3 prep) | accepted |
  | T0011 | accepted |
  | T0012 (red pulse test) | accepted |
  | S0001 | accepted |
  | S0002 | redo → S0003 |

## Still in flight at hand-back
- **S0003 (codex-vivek)**:
  1. search `local/` for the raw `vachana_send` take (it was not at `RENDERS:scene2/app/vachana_send.mkv` when S0002 ran)
  2. prep it if found
  3. re-render both drafts with the maps fallback, plus 5 stills
  - Please review it when it lands.

## Left for the lead after 14:00
1. **The `vachana_send` take:** if S0003 doesn't find it, re-export it from the phone and put it back. Then run `python film/scene2/main/prep_slot.py vachana_send <raw> --in 1.55 --audio drop` and `python film/scene2/main/build.py`, and render.
2. **Record and prep the other slots.** Example commands are in `results/S0002/REPORT.md`. Timing targets from the current cut:
   - `yash_receive` (9.0 s): notification over his other app → open → message → the TTS plays aloud (`--audio keep`).
   - `yash_reply` (4.5 s): his reply transcription → Send. His spoken line in 8c ends right before this slot.
   - `vachana_reply` (7.0 s, then a 0.5 s hold): the notification → open → the reply is visible.
   - `maps`: a real Google Maps recording, if Vivek wants one instead of the fallback. Change `maps.path` back to `RENDERS:scene2/app/maps.mp4`.
3. **A listener quirk:** after every task on vivek-pc, the listener moves `film/scene2/main/assets/walk.mp4` (29.7 MB) out of the folder, even though it's git-ignored. So **always run `build.py` before rendering scene 2** (it re-links the asset).
4. Scene 3 prep is ready to use: T0010 (clip inventory) and T0012 (red pulse look).

## For Vivek to decide
- **Length:** scene 2 is 98 s with the lead's cut lengths, not the ~80 s estimate. Keep it, or say where to trim (the 13 s `vachana_send` slot and the 9 s `yash_receive` are the longest).
- **Map:** is the drawn map card acceptable, or should it be a real Google Maps recording?
- **Bench push-in:** it ends very tight, and the last part is visibly soft from upscaling before it dissolves into the app. Keep it, or end wider (about 1.6-2x)?
- **Lip sync:** Yash's lip sync at the fixed -0.370 s offset needs checking by ear. The opening "Oh" starts before the video does.
- **Captions:** whether to use them at all, and the proposed style (T0009: bottom-centre, 46 px on a dark box). They would overlap the lower part of the centred phone in scene 2.
- **Sound taste:** the sonar sound and music (T0004), and the "sent" blip and placeholder notification tone (T0007).

## Worker use
- **codex-vivek:** T0007 → S0002 → S0003.
- **codex-f1:** T0009 and T0010. It sat idle after about 12:45; I found no scene 2 work that didn't clash with T0007's files or depend on the phone recordings.
- **codex-f2:** T0011, T0012 and S0001, then idle.
- Nothing was queued just to keep workers busy.
