---
status: done
---
# T0041: film v2 review (claude-second)

As instructed, I made no edits to the v2 scene folders. All findings are written as notes for the render helper.

## Reviews written
| Task | Verdict | Summary |
|---|---|---|
| T0033 scene 3 v2 | **redo** (the helper must fix the points) | The structure, sync, Rule B windows, Accept timing, narration starts and separate music stem are right. There are 4 must-fixes (below). Details: `discussion/v2/002-claude-second.md`. |
| T0035 sound set | accepted | Five production cues, including the new `sos_send`, with mix gains. The v2 builds must switch to these files. |
| T0036 narration tool | dropped | Superseded: the lead's helper cleaned Vivek's lines, and the T0040 spec forbids running `prep.py`. The tool is untested (no Python in the worker sandbox). |
| T0032 scene 2 v2 | not reviewed | It hadn't landed when I wrote this. Pre-review notes against the spec are in `discussion/v2/003-claude-second.md`. |

## Open findings, in priority order (for the lead to pass to the helper)
1. **Scene 3: invented app UI can reach the final picture.** If any slot file is missing, `build.py` renders a `.mock` layer with made-up iTantra text ("Someone needs help", "Help is coming", a red Accept button). `qc.py`'s placeholder probe can't detect it. The build must refuse to render with missing slots.
2. **Scene 3: `vachana_response` / `end_hold` phone is invisible.** `.app-only .screen` has no height. Add `height:1000px` and the card styling (exact CSS in note 002).
3. **Scene 3: the cut from the split `vachana_sos` into `sos_in` jumps layouts** (from the split to the old centred full-height phone). Either add a 0.5 s leaving move to the centred frame (geometry in note 002) or the lead accepts a hard cut. Also set `APP_STILL['search_xy']` from the real searching still.
4. **Scene 3 (and scene 2): use T0035's `RENDERS:sound/*.wav`** (`sos_send`, `sos_notify`, `sent`, `notify`) at T0035's gains, not the T0024 option names. The SOS send is currently a sonar-pulse placeholder.
5. **Scene 2: Vachana's split-screen crop.** With a left-aligned crop her arm touches the feather (real frames, src 4.8/7.0). Use `object-position: 36.3% center` (note 003 point 4).
6. **Scene 2: Yash's "Oh" (clean 0.0-0.38 s) is probably not Yash.** It lies 0.37 s before the camera starts, 1.4 s before "it's too hot here", and it's a single burst at clean 0.2 s. It could be the director's "go". Recommend starting his first window at "it's" (clean 1.68 s) unless Vivek hears that it's Yash (note 003).
7. Should-fix, scene 3:
   - camera crops 250 px right (people sit right of centre, Vivek near the feather)
   - `vivek_first` still at 1.766 (avoids a 2-frame backward jump)
   - response notification timed from its log
   - static narration gain instead of per-clip `loudnorm`
   - confirm `local/models/rnnoise/sh.rnnn` exists on vivek-pc, or the build crashes after the long render
8. **S0007** (the old v1 narration-stem task on codex-vivek) is still queued, waiting for a T0030 review that doesn't exist. It's superseded by v2's `narration.json`. Leave T0030 unreviewed, or mark S0007 dropped, so it never runs ahead of the v2 renders. (S tasks sort before T tasks in the listener.)

## Checked and fine (scene 3 v2)
- **Rule B:** the sospart1 window (clean 0.00-4.72 + 0.30) keeps "Help me anyone." whole; the file starts on speech. The sospart2 window (7.54-10.34) leaves out the bursts at 1.0-2.1 s and 11.9-12.1 s.
- **Lip sync:** Vachana (camera = slot + 2.867, listen_at 1.4 → src 4.267); Vivek (moving from slot 9.99 at src 4.75, so the line at ptt_down + 0.1 → src 7.62).
- **Accept:** unhurried, 2.6 s into an unsped slot.
- **Card and rules:** the intro card's CSS is identical to scene 2's. N5 at 3.3 s and N6 at 21.83 s, with no overlaps. Music only under the SOS sonar, as a separate stem. No relay chain, packet or blue relay points. No `Math.random`/`Date.now`/URLs. Audio layers are the same length as the picture.
- **Framing:** checked on real frames (sospart1 src 2.9-10.6, sospart2 src 4.7-10.65). Nobody is cut off with the current crops, and the phone hand is visible in all of them.

## For Vivek or the lead
- The `vachana_sos` → `sos_in` cut: add the leaving move (recommended) or accept a hard cut.
- Is the opening "Oh" in `Normalpart6.mp3` Yash, or the director's "go"?
- The SOS send sound: pick A/B/C from `results/T0035/preview/sos_send_options.mp3` (A is recommended).
