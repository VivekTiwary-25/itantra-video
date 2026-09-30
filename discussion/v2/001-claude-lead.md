# Film v2: Vivek's review fixes (claude-lead, 30 Sept 18:35). This is the spec for T0032-T0040.

Target: **final film by 20:00 IST**. codex-f1 and codex-f2 build (compositions, scripts, previews). claude-second reviews each result as it lands and fixes judgment issues inside compositions. codex-vivek preps slots, renders and assembles on vivek-pc. The lead only decides and does the final check.

To avoid stepping on the v1 files that codex-vivek is still using, **v2 is built in new folders**: `film/scene2/v2/` (owner codex-f1) and `film/scene3/v2/` (owner codex-f2), each started as a copy of that scene's `main/` folder from git at the time the task starts. Do not edit `main/`.

## A. Split screen (replaces "app centred with blurred sides" whenever someone uses the app on camera)
Layout, 1920x1080:
- **Left: the person's real clip**, a panel from x=0 to x=1232, full height, the camera clip scaled to cover it and positioned so the person and their phone stay inside (choose `object-position` per clip from the frames). Graded `GRADE_V1`.
- **Right: the app screen**, on a near-black field (#0a0d12, x=1232 to 1920): the portrait recording at height 1000 (keep its aspect), centred in that field, 32 px rounded corners, 1 px border rgba(255,255,255,0.14), soft shadow. Never graded.
- A soft 24 px dark feather on the camera panel's right edge instead of a hard line.
- **Entering:** from the full-frame camera shot, over 0.5 s (power2.inOut) the camera picture settles into the left panel while the phone slides in from the right and fades up. **Leaving:** the reverse, or a straight cut when the next shot is a different place.
- **Sync ("roughly in sync"):** the camera clip plays at real speed and is placed so the person's spoken line lines up with the app's listening state (numbers below). Where the app runs longer than the camera clip, hold the camera's first or last frame with a very slow 2% push so it never looks frozen; never loop and never speed up or slow down speech.
- App-only moments with nobody on camera (the map card; Vachana's phone getting Vivek's response) keep the old centred layout with blurred sides.

## B. "Go" cues: make them impossible
Vivek says "go" before each take, and it is in the clean audio. **Rule for every build:** a dialogue clip is audible ONLY during its spoken line: from 0.12 s before the line's first word to 0.30 s after its last word ends (word timings: `results/T0003/*.json`, `film/scene1/words_p*.json`; offsets confirmed in `results/T0020/sync_audit.md`), with 30 ms fades. Everything else in that clip's audio is muted. Camera audio is never used. This also guarantees a line is never cut early: the audio window is set by the words, not by where the picture cuts, so let the audio run on over the next picture if it has to.

## C. Scene 2 v2 (codex-f1, `film/scene2/v2/`)
Order and decisions:
1. `doorway` 0-3.0 s: unchanged ("How the app works").
2. `bench`: normalpart1 full frame from src 0.0 to src 4.3. **No push-in any more.** (Her line is at video 4.88-9.46. The "go" at about src 0-1 is removed by rule B.)
3. Split screen in over src 4.3-4.8, then slot `vachana_send` (13.13 s; `ptt_down` 0.08, `ptt_up` 5.24, `sent_at` 11.98). Camera src = slot time + 4.80, so her speaking matches the app's Listening state. The camera clip ends at src 10.83 (slot 6.03): hold its last frame with the slow push to the end of the slot. "Sent" sound at `sent_at`.
4. Freeze the whole split frame 3.6 s; N1 starts 0.2 s in.
5. `walk` 6.0 s: **in v1's music version this segment shows no picture.** Find out why and make it impossible: `build.py` must verify that every asset the composition references exists and is a playable video of the right length before rendering, and fail loudly if not (the listener on vivek-pc is known to move `assets/walk.mp4` away after each task; the build must re-create or re-link it every time, for BOTH mixes). Both mixes must come from the same single picture render.
6. `maps` 3.5 s: unchanged (centred; it now reads "~300 m, walking distance").
7. Yash: `yash_before_notification` full frame as now ("Oh, it's too hot here" + 0.3 s). Notification sound. Then split screen: right side is ONE continuous slot **`yash_app`** (codex-vivek preps it from `yash_take.mkv`: from `tap_notification` - 3.0 s to `tap_send` + 2.0 s, about 20.9 s; fields `notification_at`, `play_at`, `ptt_down`, `ptt_up`, `sent_at`; iTantra TTS `tts_msg.wav` laid at `play_at` + 0.15 s). Left side is normalpart6 continuing: he takes out his phone and looks at it (hold/slow-push while the message is read aloud), and his spoken line "I'm in the garden. I'll come to you." (times from T0020) starts 0.1 s after `ptt_down`. **"Sent" sound at `sent_at`** (new). Build against a placeholder of the right length until the slot file exists.
8. Sonar section unchanged, **music kept** under it: `sonar_a`, `relay_1..3`, `sonar_b` with N2 and N3.
9. **Scene 2 ends on `sonar_b`** (N3 "And that's how it gets there."), plus a 0.5 s hold. **Removed:** the fade, N4 ("His reply comes back the same way") and the whole `vachana_reply` shot.

## D. Scene 3 v2 (codex-f2, `film/scene3/v2/`)
0. **New intro card, 3.0 s**, same style as scene 2's "How the app works" card (the dark frosted matte panel over a heavily blurred picture, same type and size): **"SOS: help from anyone nearby"**. Behind it: blurred, graded sospart1. It appears by a straight cut from scene 2's last frame, the text fades in at 0.3 s, and at 2.5-3.0 s the panel shrinks away as in scene 2 to reveal sospart1.
1. `s3_open`: sospart1 full frame from src 0.0 to src 2.4, N5 starting 0.3 s in. Rule B removes any "go".
2. Split screen in over src 2.4-2.87, then slot `vachana_sos` (12.97 s, `listen_at` 1.4). Camera src = slot time + 2.87 (her line is at video 4.27-8.99). Hold the last camera frame with the slow push after src 10.64. **Her whole line must be heard: "…Help me anyone."** must finish (rule B). **SOS sound when she taps Send** (`send_at`, to be supplied by codex-vivek from the log: `send_tap` minus the slot's in-point).
3. `sos_in`, `sos_sonar` (N6), `sos_dive`: unchanged, music as a separate stem.
4. Lab: `sos_dive` ends on sospart2 src 3.0 full frame. SOS notification sound, then split screen: right side is ONE continuous slot **`vivek_app`** (codex-vivek preps it from `vivek_take.mkv`: from `tap_accept` - 2.6 s to `tap_send` + 1.6 s, about 21.4 s; fields `accept_at`, `play_at`, `ptt_down`, `ptt_up`, `sent_at`; iTantra TTS `tts_sos.wav` at `play_at` + 0.15 s). Left side is sospart2 from src 3.0: he looks at his phone, holds while Vachana's SOS is read aloud, and his line "Wait, I'm in the chemistry lab. I'll come get you, wait." (video 7.6-10.4) starts 0.1 s after `ptt_down`. "Sent" sound at `sent_at`. The Accept tap must be clearly visible and unhurried: do not cut or speed anything between the banner arriving and the tap.
5. `vachana_response`: app only, centred layout. **Trim the dead pause at the end**: finish 2.0 s after the message screen with Vivek's reply has opened, then a 0.5 s hold. That ends scene 3.

## E. Sounds
Procedural only (the generators from T0024 in `film/sound/`): message notification, "sent" blip, SOS notification, and an **SOS send** sound (controlled, short, clearly more serious than the "sent" blip; no siren, no boom). Use T0024's recommended option for each until Vivek picks. Levels: well under dialogue.

## F. Narration
Vivek is recording N1, N2, N3, N5, N6 himself (N4 is dropped). Targets: N1 3.0 s (max 3.4), N2 3.8 (max 4.2), N3 1.5 (max 1.8), N5 3.0 (max 3.4), N6 6.8 (max 7.2). His files go in `local/narration_vivek/` on vivek-pc. Every build reads narration from one place chosen by `film/common/narration.json` (`{"voice": "david"}` now, `"vivek"` when his cleaned files exist at `RENDERS:narration/vivek/N*.wav`), with fixed start times, so swapping the voice changes no timing. If a Vivek line is longer than its max, report it; do not time-stretch by more than 6%.

## G. Hand-back from codex-f1 / codex-f2
Code in git, `hyperframes.cmd check` passing, preview stills (960 px JPG) of every new layout in `results/<id>/preview/`, a `timeline.json`, and a REPORT.md that lists the exact slot fields the build expects. You do not have the app recordings: build and preview with placeholder videos of the right size (1080x2290 for status-bar-cropped slots, 1080x2400 for the ones that keep it) and length. codex-vivek renders the real thing; claude-second reviews it.
