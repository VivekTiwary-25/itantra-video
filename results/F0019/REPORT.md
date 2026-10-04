---
status: done
---
# F0019: fresh-eyes review of the film v3 parts

The note is `discussion/v3/002-claude-second.md`. It covers s2a (+ overhead), s2b, s3, exploded, cards and captions. intro_v3 has only `prep.py`: F0005 failed, so there is no composition.

## Must-fix before render
1. **App media in git:** `film/scene2/v3b/assets/yash_slot.jpg` (plus that folder's kit copy) and `film/scene3/v3/snaps_accept*/` are real app-recording frames. Remove them from the index and add the ignore rules (exact commands are in the note). The root rule `film/*/assets/` does not reach `film/scene2/v3b/assets/`.
2. **s2a assembly inputs:** `film/final/v3_segments.json` points s2a at an assumed file. The real outputs are `scene2_picture.mp4` + `scene2_dialogue_sfx.wav`, 44.154 s, and the events log label is `TTS`. Update the json and the label match in `assemble_v3.py:196`. This is outside this task's `writes:`; I can do it as a short follow-up.
3. **No intro yet:** F0005 is blocked by missing ASR models on its clone. Re-queue it on a machine with `local/models/`. Its last frame must copy s2a's frame-0 card exactly.

## Should-fix (detailed in the note)
- s2b → s3 card background tint differs slightly (raise `.card-red` alpha in s3).
- s2a defines its own caption and full-card styles instead of the kit's.
- s2b hard-codes s2a's end slot time.
- s3 still mixes `sos_music` into its own scene file.
- The "Yash" pin label is not in spec section 3 (suggest adding it).
- The overhead holds camera stills for about 0.8 s and 1 s (lead's design; a strict fix is described).

## Fine
- **On-screen text:** matches section 3 exactly.
- **Captions:** match what is spoken and sit in their windows, with no collisions in the stills.
- **Hard rules:** no breaches found.
- **Music:** none inside s2a, s2b, exploded or cards.
