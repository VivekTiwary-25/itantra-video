---
status: done
---
# Scene 1 report, v2 (lead foreman, 30 Sept 2026)

This version applies Vivek's review of v1. It still ends on the empty phone shape, which is the doorway into scene 2.

## Files on Vivek's PC (not in git)
- `RENDERS:scene1/scene1_draft_v2.mp4`: the new draft. 1080p, 30 fps, 56.5 s (1.5 s of pauses removed), voice at -16 LUFS.
- `RENDERS:scene1/voice_before_after.mp3`: an updated sample, about 47 s. The order is: part 1 before, part 1 after, part 2 before, part 2 after. Both versions are set to the same loudness, so you're comparing clarity, not volume.
- `RENDERS:scene1/grade_option_A.jpg`, `grade_option_B.jpg`, `grade_option_C.jpg`: three looks, each shown as before and after on the same two frames. **A is applied to the draft for now.**
- `RENDERS:scene1/scene1_draft.mp4` is v1, kept for comparison. `grade_before_after.jpg` is v1's grade and has been replaced by the options above.

## Changes, point by point
1. **Stronger noise removal (the AI denoiser now runs).** It's RNNoise, a neural speech denoiser built into ffmpeg (the "conjoined-burgers" general model), followed by a light FFT pass and a gentle gate between words.
   - Part 1: background between words went from -32 dB (original) to -40 dB (v1) to **-73 dB** (v2). Voice-to-noise went from 17.7 to 25 to **52 dB**.
   - Part 2: background between words went from -35 to -48 to **-66 dB**. Voice-to-noise went from 19.3 to 31 to **46 dB**.
   - Her words aren't damaged: Whisper's confidence on the denoised audio stayed the same as the original (part 2: 0.908 vs 0.911).
   - The gate stops short of dead silence between words, because fully silent gaps sound unnatural.
   - This time it wasn't blocked, so no permission change was needed. The model file lives in `local/models/rnnoise/cb.rnnn` (from github.com/GregorR/rnnoise-models).
2. **The pause at ~0:42 is cut** (cut 2 below). "…will again convert text into speech" now runs on without the gap.
3. **Other pauses** are listed in the cuts table below. Every cut sits inside a measured silence and is hidden by a small punch-in.
4. **The finger** is in shot from 1.2 to 1.9 s of the original, which is over "Hello dear viewers", so it couldn't be trimmed without cutting her first words. Instead, all of part 1 has one gentle crop (1640x922 from x 280, y 79, which is 1.17x). The finger reached x 275 / y 473, so none of it shows, and because the whole shot is cropped there's no jump.
5. **Team intro panel.** It's in the top area, over the building and trees, clear of her head (the panel's bottom edge is about 120 px above the top of her head). It reads TEAM **chmod 777** (in a code font), INSTITUTE **The National Institute of Engineering, Mysuru**, PRESENTING **Vachana**, and each item appears on its word.
6. **The problem-statement details** moved into the same top panel: **SIH26173** (ISRO · iTantra), TTS: text → speech, STT: speech → text, LOW-BITRATE LINK: too little bandwidth for voice.
7. **The part 2 explanation** stays on the right side.
8. **"No infrastructure"** is unchanged, as approved. Only its timing follows the new word timings.
9. **The connector line** now sits behind solid, opaque icon boxes, so it stops at each box's edge. When a step dims, only its text and icon fade; the box stays solid. The packet passes behind the Bluetooth box.
10. **Timing.** Every cue is now computed by `build.py` from her word timings (Whisper words, with each start re-measured from the sound so it isn't late) and shifted for the cuts. Each step starts appearing 0.12 s before its word and is fully visible within 0.3 s. **"Text → speech" now appears at 39.30 s, just as she starts "The text-to-speech" (39.42 s).** In v1 it started 0.4 s after the word began and took half a second to fade in, which is why it felt late. The full cue table is below.
11. **"Through relays" and "in the message's language"** are both kept.
12. **Colour:** three options.
   - **A, warm cinematic:** warm mid-tones and highlights, teal-leaning shadows, soft contrast with gentle highlight roll-off, and a vignette. **Applied.**
   - **B, punchy contrast:** a deep S-curve, +14% saturation and a little extra crispness.
   - **C, cool / muted:** lifted blacks, a cooler balance and -30% saturation.
   - Why A: it flatters skin in harsh midday sun without making the loud blue sign even louder (which B does), and a warm live-action look will contrast well with the dark sonar scenes later. C looks washed out in this light.
   - To switch: set `GRADE = 'B'` or `'C'` in `film/scene1/build.py` and rebuild.
14. **Lip sync (a fix I found myself).** I measured the final file's voice against the camera's own sound at 7 points across all five segments. It's now within 0-1 ms everywhere. v1 was actually about 50 ms late: I had nudged the voice 25 ms the wrong way. That's fixed in `mux.sh`.
13. **The ending** is kept exactly as it was: the panel folds into the phone, "Let's see it work.", then the empty phone. Its timing is tied to her last word.

## Every cut
Times are in the v2 scene. Each cut is inside a silence measured from the denoised audio.

| # | Scene time | Removed | Where (source) | What | How it's hidden |
|---|---|---|---|---|---|
| 1 | 12.80 s | 0.37 s | part 1, video 13.60-13.97 s | reading pause between "TTS" and "and STT" | 8% punch-in to a tighter frame; her face stays in the same spot (measured 0 px shift) |
| 2 | 42.30 s | 0.80 s | part 2, video 24.67-25.47 s | **Vivek's note:** the pause after "again" (she continues "convert text into speech") | 8% punch-in. She moved 63 px during the pause, so the tighter frame is shifted to keep her face in the same spot (measured 0 px) |
| 3 | 50.13 s | 0.37 s | part 2, video 33.30-33.67 s | hesitation in "text is sent … locally" | punch back out to the full frame; the tighter frame drifts slowly (57 px over 7.8 s, hidden in the handheld movement) so her face lines up here too (measured 0 px) |

**Skipped (the cut would visibly jump):**
- The 0.43 s pause in "the text-to-speech model … will" at ~41.2 s. It's only 1.5 s before cut 2, so it would need a second framing change right next to another one, and the frame would bounce back and forth.
- Sentence breaks ("…nothing. Our on-device…", "…another device. The text-to-speech…"). These are natural breathing pauses, so I left them.

## Cue table (scene time; each step starts 0.12 s before its word)
| Panel event | On her word | Starts |
|---|---|---|
| Top panel appears | "We are from team" | 1.60 s |
| Team: chmod 777 | "team" | 2.09 s |
| Institute | "National" | 3.99 s |
| Presenting: Vachana | "Vachana" | 5.99 s |
| Panel switches to the problem statement | "We are discussing" | 6.87 s |
| SIH26173 · ISRO · iTantra | "problem statement" | 8.03 s |
| TTS | "TTS" | 12.49 s |
| STT | "STT" | 13.32 s |
| Low-bitrate link | "low bit rate" | 15.96 s |
| Right panel, NO INFRASTRUCTURE | "What does that actually mean?" | 17.82 s |
| Phone to phone. Nothing in between. | "lets two Android devices" | 21.26 s |
| Mobile signal / Internet / Wi-Fi struck | "SIM" / "internet" / "router" | 24.32 / 24.92 / 25.54 s |
| HOW A MESSAGE TRAVELS | "Our on-device…" | 27.43 s |
| Speech → text | "on-device" | 28.09 s |
| Waveform, then it squeezes into TEXT | "speech" / "compact" | 28.54 / 32.02 s |
| Sent over Bluetooth | "Bluetooth" | 33.48 s |
| Packet travels to Text → speech | "relay" … "device" | 35.25 to 38.82 s |
| **Text → speech** | **"The text-to-speech"** | **39.30 s** |
| IN SHORT | "So in short" | 46.16 s |
| Mic / Aa / Speaker light up | "speech" / "text" / "speech." | 47.85 / 48.50 / 52.64 s |
| Doorway into the phone | 0.11 s after her last word | 53.17 s (the scene ends at 56.47 s) |

## Build (reproducible, in git)
- `film/scene1/build.py`: the single build script. It holds the denoise chain, the cut list (EDL), the crop and punch-ins, the grade, and the voice assembly, and it computes the cues and fills in `index.html` from `index.html.tpl`. `--html-only` re-fills the page without re-rendering the media. It replaces v1's `prep.sh`.
- `film/scene1/grades.sh`: the three looks. `film/scene1/words_p1.json` and `words_p2.json`: her word timings. `film/scene1/cues.json`: the computed cues and segments.
- `film/scene1/make_sfx.py`: the doorway sound (unchanged).
- `film/scene1/mux.sh`: swaps in the exact audio mix after rendering. It now reads its timings from `cues.json`.
- **To rebuild:** run `python film/scene1/build.py`, then `hyperframes.cmd render -q high -f 30 -o <raw>.mp4` in `film/scene1`, then `bash film/scene1/mux.sh <raw>.mp4 <final>.mp4`.

## What Vivek needs to decide
- Listen to the new `voice_before_after.mp3`. Is it clean enough now, and is there any watery or robotic sound? RNNoise can do that on some words. If you hear it, I can blend in some of the original.
- Pick grade A, B or C, or ask for a mix.
- Check the three cuts at 12.8 s, 42.3 s and 50.1 s. Does any of them feel like a jump?

---

# Batch 1 inventory: the other clips (Codex workers, reviewed by the lead)
Sources: T0001 (frame grids + moment log, codex-f1), T0002 (sync offsets, codex-f2), T0003 (transcripts, codex-vivek). Details are in `results/T0001..T0003/` and the reviews are in `reviews/`.

**Biggest finding: no phone screen is readable in ANY camera clip.** Every phone faces away from the camera. So every app moment in the brief needs real screen recordings from the three builds:
- Vachana: language selection, PTT, transcription, composer, Normal + Yash, Send
- Yash: notification, Logs, TTS, reply
- Vachana: Hands-free, SOS select, searching state
- Vivek: ChatGPT, SOS notification with Accept/Decline, Accept, reply
- Vachana: both incoming notifications

Two more things are missing: Yash on Instagram and Vivek in ChatGPT (neither is visible), and an overhead campus view.

| Clip | Length | What it shows | Clean audio (what's said) | Sync offset* | Story beat |
|---|---|---|---|---|---|
| normalpart1 | 10.8 s | Vachana on a concrete bench by flowering shrubs near the entry; another woman in the background; she raises the phone and speaks into it from ~3 s | "Hey dude, I'm in the campus near the entry benches, where are you?" (video ~4.9-9.5 s) | -0.068 s | Vachana sends the normal message (PTT). Screen hidden |
| normalpart2 | 202.4 s | One long moving walk: NIE sign and gate (0-6 s), tree-lined road with benches and people (6-118 s), white main building with an ambulance (118-150 s), garden path (150-202 s). Midday sun | none (camera audio is crew chatter; unusable) | - | Campus / distance footage for "Yash is far away". Ground level, not overhead |
| normalpart3 | 9.3 s | Static wide shot across the road to a white building with palms; a walker crosses from ~3 s | none | - | Establishing shot (best 0-3 s) |
| normalpart4 | 3.8 s | Yash seated on steps outside a glass entrance, phone to his ear | none | - | Yash hearing the message (TTS). Screen hidden |
| normalpart5 | 3.9 s | A woman in dark uniform walking toward camera on a sunny road, looking at her phone | none | - | Cutaway only |
| normalpart6 | 12.6 s | Yash in front of a big round hedge and flower bed, speaking into the phone (4-11 s) | "Oh, it's too hot here. I'm in the garden. I'll come to you" | -0.370 s | Yash replies (PTT). Screen hidden |
| sospart1 | 10.6 s | Vachana on a dirt path near the construction site, trees and rubble; taps the phone and raises it to her mouth ~4-5 s | "I'm lost somewhere near the construction site. Please reach me out. Help me anyone." | +4.271 s | Vachana's SOS (Hands-free). Screen hidden |
| sospart2 | 10.7 s | Vivek in a chemistry teaching lab (benches, glassware, people behind), taps the phone and speaks from ~6 s | "Wait, I'm in the chemistry lab. I'll come get you, wait." (video ~7.6-10.4 s; the clean file runs ~6 s past the video's end) | +0.065 s | Vivek replies to the SOS. Screen hidden |
| vachna part1/2 | 19.7 / 37.1 s | Scene 1 (above) | (above) | +0.571 / +0.389 s | Intro |

\*Offset = clean-audio time t plays at video time t + offset. All pairs lock with a strong match. Codex reported some drift, but my finer check showed there's none: its method was comparing near-silent stretches.

**Beats with no footage at all:**
- B02-B07: Vachana's app steps
- B08: Yash on Instagram
- B09-B11: Yash's notification, Logs, TTS
- B14: Vachana receiving the reply
- B17-B22: SOS select, searching, Vivek on ChatGPT, Accept/Decline, Accept, SOS open
- B25: Vachana receiving the response

Most of these are app screens. They can come from screen recordings (`adb screenrecord` from each actor's phone running its build), cut against the camera clips above, which already give us the people, places and voices.
