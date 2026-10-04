---
status: done
---
# F0050: scene 2a v4 (spec 005 S2 + G2)

`film/scene2/v3a/`: `build.js`, `index.html.tpl` (+ regenerated `index.html`, `timeline.json`), `overhead/overhead.js` (+ README note), and `film/captions/v3/s2a.json`. F0041 had left no changes in git, so I started from S0101/F0038.

## What changed
1. **Start / intro join:** `card_out` is removed. Frame 0 is `FOOTAGE:Video/normalpart1.mp4` at the intro's hand-off source time, full frame and moving. That time is read from `film/intro_v3/timeline.json` `end_state.normalpart1_src`; the key is absent today, so the default 1.0 s applies.
   - The whole bench/split timeline now runs on that source clock: bench 0-3.3, split 3.3, app at 3.8.
   - **Mode card:** a centred `.glass-card` with the SOS card's tint and type (64 px `Normal`, 38 px `a private message to someone you trust`) fades in at 0.3 s, is readable about 0.6-2.9 s and clears by 3.3 s, over the moving bench.
2. **No zoom/crop on app recordings (G2):**
   - F0020's banner/Logs `punch()` is deleted. Both phones show the recording whole in a box of its own aspect ratio.
   - The flying message card is now a `.glass-panel` with the real message text, instead of a crop of the app screen (`message_crop.jpg` is no longer made).
3. **Overhead:**
   - **Walk:** the rise is now a tracking pull-back. The camera centre glides from Vachana's pin to the map centre (toward Yash) while zooming 2.65 → 1, and the walk clip stays at frame centre with a slight down-right drift. So it travels FROM Vachana TOWARD Yash (down-right).
   - **Zoom:** one smooth direct zoom onto Yash. A single smoothstep drives an exponential scale 1 → 5.2 and the pin's straight glide to frame centre. The old formula threw the pin off-screen and back mid-zoom, which was the "shake".
   - **Reveal:** Yash's live clip fades in by opacity only; the 1.16 → 1 secondary push and circle wipe are gone.
4. **Yash re-synced, `YASH_REPLY` true by default** (his reply line, video, audio and the second sent ting are kept; nothing returns to Vachana):
   - **App recording:** played at 1x in six pieces `[1.25-2.40][2.90-3.95][4.95-5.60][7.20-11.30][11.85-16.80][18.30-19.467]`. Every cut lies inside a stretch with no on-screen change (banner hold, Logs, message screen, after playback, compose). The build checks all 10 cuts against ffmpeg `freezedetect`.
   - **Event times** (segment s): banner 0.20, play tap 3.28, message plays 3.43-6.77, reply PTT 7.23-10.43, Send 12.47.
   - **Camera, two windows, nothing repeated or held:**
     - Window A continues the full shot (source 2.65 → about 4.15, looking at his phone as the banner lands).
     - App takeover from 1.5 to 3.4 s.
     - Window B (source = dt + 0.90) shows him listening (source 4.33-7.67) exactly while the app plays the message. It then stays lip-synced to his reply (camera = clean audio - 0.37 s) and slides out at 11.2-11.7 s, before the clip ends (12.647).
   - **Full shot:** source 0.98-2.65, so "It's too hot here." ends exactly at the split.
5. **N1:** read from `film/common/narration_v4.json`: start = walk + 0.3, duration 3.2 s (placeholder). If `RENDERS:narration/v4/N1.wav` is missing, the audio stem logs placeholder silence; preview and page-only only, while a production render refuses unless `ALLOW_PLACEHOLDER_NARRATION=1`. The caption uses that file's `text`; it is empty for now, so the v3 line stands in until the real take is transcribed.
6. **`timeline.json`:**
   - duration **41.037 s** (was 43.274)
   - `end_state` = `yash_app` slot_time **19.4334** (last frame of the last piece), rect 735/40/450/1000, `#0a0d12`. s2b's push-in continues the recording from 19.467 (sent tick → Logs) and its build checks the rect.
   - The yash_app EDL, event times and camera windows are recorded in the yash_app segment.
   - `audio_events.txt` labels are now `dialogue …` / `narration N1` / `sfx …` / `TTS`, which the assembler reads for ducking.

`node build.js --page-only` passed, including `hyperframes.cmd check`; `results/F0050/build_check.txt` has the numbers. No video was rendered.

**For the lead:** `film/final/v3_segments.json` (outside this task's writes) still says s2a `expected_duration` 43.274. Set it to **41.037**. Its TTS fallback is now 31.397-34.737 s (yash_app starts at 27.967), but the assembler reads the real window from `audio_events.txt` anyway.

## Stills (`results/F0050/preview/`, 1920 px JPG + `sheet_480.jpg`)
| t (s) | Hero | Reads at 480 px? | Judge "oh"? |
|---|---|---|---|
| 0.0 | Vachana on the bench, moving, continuing the intro's shot | yes | n/a (join frame) |
| 1.5 | `Normal` mode card over the moving bench | title yes; subline readable, small | clean mode framing, yes |
| 3.6 | split: Vachana + her app (Listening) | yes | ok |
| 9.0 | split: app transcribing her line | yes | ok |
| 16.1 | message flies off as a glass card with her real text; phone shows "Sent to Yash" | yes | yes, the message visibly leaves |
| 18.5 | sped-up walk, `Sped up 26×`, N1 caption | yes | ok |
| 21.5 | walk clip tilting into the ground, map rising | yes | yes, the rise |
| 22.0 | walk shrinking down-right toward Yash, buildings appearing | yes | yes |
| 23.6 | overhead with both pins and `~300 m, walking distance` | yes | yes, the clear "how far" moment |
| 25.0 | start of the single zoom onto Yash's pin (no shake) | yes | yes |
| 26.25 | end of the zoom: Yash's live frame | yes | smooth landing |
| 26.9 | Yash full shot, "It's too hot here." | yes | ok |
| 28.4 | split: Yash looks at his phone; the banner has arrived | banner text small but legible | ok |
| 30.5 | app takeover: Logs with Vachana's message, whole screen | yes | ok |
| 32.5 | Yash listening while the app plays the message (Pause), TTS caption | yes | yes, finally in sync |
| 36.5 | Yash speaking his reply, app recording, caption | yes | yes |
| 40.5 | centred app: his reply composed, Send | yes | ok |
| 41.0 | last frame: sending spinner, centred phone (s2b continues) | yes | n/a (join frame) |

## Files moved out of git by the listener

- `film/scene2/v3a/assets/walk.mp4` (24.0 MB) was too big for git. Moved to local path: `RENDERS:F0050/film/scene2/v3a/assets/walk.mp4` (inside renders_dir on yojitth-pc)
