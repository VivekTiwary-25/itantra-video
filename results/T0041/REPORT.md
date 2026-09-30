---
status: done
---
# T0041: film v2 review (claude-second)

As instructed, I made no edits to the v2 scene folders. Every finding is a note for the render helper, with exact changes:
- `discussion/v2/002-claude-second.md`: scene 3
- `discussion/v2/004-claude-second.md`: scene 2 code review
- `discussion/v2/003-claude-second.md`: scene 2 pre-review (numbers and windows); its framing point is superseded by 004

## Reviews
| Task | Verdict | Summary |
|---|---|---|
| T0032 scene 2 v2 | **redo** (the helper fixes the points) | Structure, order, sync, Rule B windows, the walk check, one picture for both mixes and the crops are right. 7 must-fixes (below). |
| T0033 scene 3 v2 | **redo** (the helper fixes the points) | Structure, sync, Rule B ("Help me anyone." complete), unhurried Accept, narration starts and a separate music stem are right. 4 must-fixes (below). |
| T0035 sound set | accepted | Five production cues, including the new `sos_send`, with mix gains. The v2 builds should use these files. |
| T0036 narration tool | dropped | Superseded (the lead's helper cleaned Vivek's lines; the T0040 spec forbids `prep.py`). It's untested. |

## Open findings, in priority order
1. **Both scenes: invented app UI can reach the final picture.**
   - What renders if a slot file is missing: scene 3's `.mock` shows fake iTantra text and a red Accept button; scene 2 shows `.empty-app` bubbles and a `#mapLabel`.
   - `qc.py` can't detect either.
   - Both builds must refuse to render (non-preview) with any missing slot.
2. **Scene 2: silent sonar-sound fallbacks.** If `film/scene2/sonar/*/assets/*_sfx.wav` or `music/sonar_music.wav` are missing on vivek-pc (likely, since earlier builds staged them elsewhere), the build quietly uses **SOS pulses and a sine bed**. Run `python film/scene2/sonar/build.py sound` in place, and make the fallbacks throw.
3. **Scene 2: narration is truncated at its max length.** A long Vivek line would be clipped mid-word. Remove the truncation and keep the warning.
4. **Scene 3: the `vachana_response` / `end_hold` phone is invisible** (`.app-only .screen` has no height). Exact CSS is in note 002.
5. **Scene 3: layout jump from the split `vachana_sos` into `sos_in`'s centred phone.** Add a 0.5 s leaving move (geometry in note 002), or the lead accepts a hard cut. Set `APP_STILL['search_xy']` from the real searching still.
6. **Scene 2: Yash's opening "Oh" is probably the director's "go"** (a single burst before the camera starts, 1.4 s before the line). Start the window at "it's" (clean 1.68 s), unless Vivek hears that it's Yash.
7. **Scene 2: the "sent" state flashes during the split-in.** Show the slot's first frame while the phone slides in.
8. **Scene 2: Yash's TTS hold frame has the phone at his mouth** (looks like talking while the message plays). Hold src 7.10 (looking at the phone) and resume at `ptt_down` − 1.03. Lip sync is unchanged.
9. **Scene 2: no 2 % slow push on held camera frames** (spec A).
10. **Both scenes: use T0035's `RENDERS:sound/*.wav`.** Scene 3's SOS send is a sonar-pulse placeholder.
11. Should-fix, scene 3:
    - camera crops about 250 px right
    - the `vivek_first` still at 1.766
    - the response notification timed from its log
    - static narration gain
    - confirm `local/models/rnnoise/sh.rnnn` exists (scene 3 needs it unconditionally; scene 2 checks for it)
12. **S0007** (old v1 narration-stem task on codex-vivek) is still queued, waiting for a T0030 review that doesn't exist. It's superseded by v2's `narration.json`, so keep it from ever running (S tasks run before T tasks in the listener).

## Checked and fine
- **Rule B windows vs T0003 word timings and clean-audio energy:**
  - normalpart1: 4.83-9.83 (the "go" at about 0.6 s is outside)
  - Normalpart6 reply: 8.48-10.94
  - sospart1: 0-5.02 (the file starts on speech; "anyone." decays by 4.75)
  - sospart2: 7.42-10.64 (bursts at 1.0-2.1 and 11.9-12.1 s are outside)
- **Sync:**
  - Vachana send: camera = slot + 4.80, "Hey" at `ptt_down`
  - Yash's reply lands at `ptt_down` + 0.1 on src 8.23
  - Vachana SOS: camera = slot + 2.867, `listen_at` 1.4
  - Vivek resumes at slot 9.99 on src 4.75, so the line at `ptt_down` + 0.1 → src 7.62
- **Accept:** 2.6 s into an unsped slot.
- **Card and scene 2 ending:** scene 3's intro card uses the same CSS as scene 2's. Scene 2 ends on `sonar_b` + 0.5 s with no N4 and no `vachana_reply`.
- **Rules:** music only under the sonar sections as separate stems. Nothing red in scene 2. No relay chain, packet or blue relay points in scene 3. No `Math.random`/`Date.now`/URLs.
- **Framing** on real frames: nobody is cut off in any of the four split panels.

## For Vivek or the lead
- The `vachana_sos` → `sos_in` cut: add the leaving move (recommended) or accept a hard cut.
- Is the opening "Oh" in `Normalpart6.mp3` Yash, or the director's "go"?
- The SOS send sound: A/B/C in `results/T0035/preview/sos_send_options.mp3` (A is recommended).
