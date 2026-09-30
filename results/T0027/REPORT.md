---
status: done
---
# T0027: dispatcher, 15:50-17:50 IST (claude-second)

## Finished and reviewed

| Task | Worker | Verdict | Notes |
|---|---|---|---|
| T0016 scene 3 assembly | codex-vivek | accepted | 60.2 s. All 3 SOS sonar segments are in; dialogue/sfx and music are separate layers; sync agrees with T0020. |
| T0018 `assemble.py` | codex-f2 | accepted | Frame-exact joins and a loudness gate. |
| T0019 push-in | codex-f1 | accepted | 1.8x, applied in T0029. |
| T0020 lip-sync audit | codex-f2 | accepted | normalpart6 -0.3705 s, sospart1 +4.271 s, sospart2 +0.066 s. No further sync task needed. |
| T0021 captions | codex-f1 | accepted | Optional layer. |
| T0022 `qc.py` | codex-f1 | accepted **with my fixes** | The worker couldn't run Python. I ran the tests and fixed a black-frame parser bug (ffmpeg 9 prints start and end on one line, so every black run looked open-ended) and a false alarm on the dark sonar sections. Fades under 1 s are now INFO. All 5 planted defects are caught, and the clean clip passes. |
| T0023 title B + poster | codex-f1 | accepted | Vivek picks A or B. |
| T0024 sound options | codex-f2 | accepted | Vivek picks by ear. T0029 used `message_a`. |
| T0025 rule audit | codex-f2 | accepted | Its relay_2 "Utkarsh is Yash" must-fix is a **false alarm**: normalpart4 and normalpart6 show clearly different men (checked side by side). |
| T0026 style guide | codex-f2 | accepted | Can become `brief/style.md`. |
| T0017 title A | codex-f1 | redo → S0004 | Failed on a codex network error before starting. |
| T0028 title render | codex-vivek | redo → S0005 | No `film/title/` existed yet. |
| S0003 | codex-vivek | accepted | Leftover from T0008. |
| S0004 title A | codex-f2 | accepted | `film/title/`: six lines verified word for word. Its Python scripts run. |
| S0005 title render | codex-vivek | accepted | `RENDERS:title/title.mp4`, 20.0 s, ticks at -24 dBFS, no font fallback. |
| S0006 scene 3 + title re-audit | codex-f2 | accepted | 3 must-fix: placeholders (known), SOS music baked into `scene3_draft.mp4`, narration not on its own stem. The last two are queued as S0007. |
| T0029 scene 2 final pass | codex-vivek | accepted | **Four real app slots are in.** Push-in 1.8x, Yash's lip sync fixed, `message_a` notification, 102.5 s, -16.2 LUFS. The maps slot is still the drawn fallback. |
| S0008 caption refresh | codex-f1 | accepted | Matches T0029's timeline (spot-checked). |

## Running at hand-back
- **T0030 (codex-vivek): the full first cut**, `RENDERS:full_film_v1.mp4` + `_nomusic` + `_music_only.wav`, running since about 17:20. All its inputs exist: scene 1 v3 (the lead's), scene 2 from T0029, scene 3 from T0016, and the title from S0005. **The lead should review it when it lands.** Check that the qc table isn't failing on anything other than the known dead-air silences and the scene 3 placeholders.

## Queued
- **S0007 (codex-vivek, waits for T0030 to be accepted):** separate narration stems for scenes 2 and 3, the scene 3 draft without baked music, and `assemble.py` taking a narration layer. This fixes the S0006 must-fixes without delaying the first cut.
- codex-f1 and codex-f2 have nothing queued. The remaining work needs vivek-pc (media, Python, the phone) or the lead's recordings, so I didn't queue filler.

## Blocked, and on what
- **Scene 3 app slots** (`vachana_sos`, `vivek_sos`, `vivek_reply`, `vachana_response`) and the `sos_in` searching still (`RENDERS:scene3/app/vachana_sos_last.png`): these wait for Vivek's OK on the SOS wording and then the recordings. Until then the full cut shows marked `APP:` cards in scene 3.
  - Once the recordings are in: prep with `film/scene3/main/prep_slot.py`, set `listen_at`, run `python film/scene3/sonar/build.py plates pages` (and set `APP_STILL['search_xy']`), rebuild scene 3, then re-run T0030's assembly.
  - Also check that the Accept tap is visible and unhurried.
- **Real Google Maps recording:** `maps.mkv` doesn't exist. The drawn fallback card is used.
- **Sound option WAVs** for everything else (sent/tick/SOS): they need `python film/sound/make_options.py` run on vivek-pc once Vivek has chosen.

## For Vivek to decide
1. **Title card A or B.** A is rendered and in the cut (`results/S0004/preview/`); B is in `results/T0023/preview/`. Also the poster (`results/T0023/poster.png`).
2. **Dead air in the scene 2 app slots:** 94.6-102.5 s is silent (the return leg, `vachana_reply`), with shorter gaps in other slots. Options:
   - accept the calm silence
   - a very low room tone
   - play `tts_reply.wav` when Vachana opens Yash's reply, if the app reads it aloud
   - I'd pick the last one if the app does that.
3. **Captions on or off.** The overlays are ready and timed to the current cut (`film/captions/`, T0021/S0008).
4. **Maps:** is the drawn card acceptable, or should a real Google Maps recording replace it? The title's "~400 m" must match whatever the map shows.
5. **Sounds:** pick from the 15 options in `results/T0024/preview/all_options.mp3`. `message_a` is already used for Yash's notification.
6. **Scene 3:** Vivek's point on the sonar map is illustrative (the courtyard block south of Vachana). Move it if the real chemistry lab is elsewhere (`film/scene3/sonar/cues.py`).
7. **Scene 1 text:** does the scene 1 problem-statement panel need the exact official SIH wording (T0025 should-fix)?
8. **Length:** scene 2 is now 102.5 s and scene 3 is 60.2 s. The whole film will be about 4:40 plus the title, depending on scene 1 v3.

## Notes for the lead
- On every listener task on vivek-pc, `film/scene2/main/assets/walk.mp4` gets moved out. `build.py` re-links it, so always rebuild before rendering scene 2.
- The listener runs S-prefixed tasks **before** T-prefixed ones on the same worker. I used `depends_on` so S0005 and S0007 couldn't jump ahead of the cut.
