---
status: done
---
# Scene 1 report (lead foreman, 30 Sept 2026)

Scene 1 is built, start to finish, up to the doorway into scene 2. It ends on the empty phone shape, as agreed.

## Files on Vivek's PC (not in git)
- `RENDERS:scene1/scene1_draft.mp4`: the watchable draft. 1080p, 30 fps, 58.0 s, voice at -16 LUFS.
- `RENDERS:scene1/voice_before_after.mp3`: before/after of her voice, about 40 s. The order is: part 1 before, part 1 after, part 2 before, part 2 after. Both versions are set to the same loudness, so you're comparing clarity, not volume.
- `RENDERS:scene1/grade_before_after.jpg`: the colour draft. The top row is part 1 (before | after) and the bottom row is part 2 (before | after).
- `RENDERS:scene1/scene1_render_raw.mp4`: the HyperFrames render before I replaced its audio. Keep it only for debugging.

## Which clips are which
- **Part 1 = `FOOTAGE:Video/vachna part1.mp4` + `FOOTAGE:Audio/vachna part1.mp3`** (19.7 s). She greets, names the team and NIE, then reads the problem-statement title.
- **Part 2 = `FOOTAGE:Video/vachna part2.mp4` + `FOOTAGE:Audio/vachna part2.mp3`** (37.1 s). She explains what it means in her own words.
- **What the footage looks like.** Both are handheld, outdoors, in daylight, in front of the blue "NIE (N)" sign. There's a white building under construction behind her, with trees on the right. She stands centre-left, holding a phone. There's no HDR (8-bit bt709), and the two clips were already close in colour. Part 2 is a little tighter and about 3.5% brighter on the same wall and sign. A finger covers the lens for the first ~0.8 s of part 1, so the scene starts at 0.8 s.

## What she says compared with the official problem statement
- **The official title (SIH26173, ISRO):** "iTantra - Indian Multilingual TTS & STT Aided Neural Transceiver Radio Access for low bitrate links".
- **What she says:** "...Indian multilingual TTS and STT aided neural transceiver radio access for low bit rate communication."
- **The only wording change** is that she says "communication" instead of "links".
- **One word to listen to:** Whisper heard "STT" as "STD" (at about 13.8 s into the scene). It may just be her accent. The panel spells "STT" correctly at that moment anyway.

## What I built, and why
**Scene timeline (58.0 s):** part 1 runs 0-18.0 s, then there's a hard cut to part 2, which runs 18.0-55.1 s. The last frame is then held to 58.0 s for the doorway. The cut sits in a natural 0.8 s pause ("...low bit rate communication." / "What does that actually mean?"), and it's hidden by the panel changing its content at the same moment.

**Voice:**
- **Sync:** each clean audio file was lined up with its camera sound by cross-correlation. Part 1 is +0.571 s and part 2 is +0.389 s. I checked 3-second windows across both clips and found no drift. In the final render the voice lands within 25 ms of the picture at four points I measured, and I then nudged it to 0 ms.
- **Problem:** heavy low rumble from traffic or wind, plus steady tones, probably from the construction site behind her. Background noise was only 18-19 dB below her voice.
- **Clean-up chain:** high-pass at 100 Hz, then FFT denoise, then a gentle gate between words, then -2 dB at 250 Hz (mud), then +2 dB at 3 kHz (clarity), then de-ess, then light compression, then -16 LUFS with peaks at -1.5.
- **Result:** noise is now 25 dB below her voice in part 1 and 31 dB in part 2.
- **Checking for damage:** I can't hear, so I re-transcribed the cleaned audio. Whisper's word confidence stayed the same as the original (part 2: 0.908 cleaned vs 0.911 original), so the clean-up isn't hurting her words.
- **What to listen for:** a slight "underwater" or watery sound in part 1, which is the noisier take.

**Colour (draft):**
- Part 2 is matched to part 1 using the grey brick wall as the neutral reference.
- Then one look goes over both:
  - a gentle S-curve that rolls off the bright building
  - slightly warm mid-tones and cool shadows
  - saturation down 10% (the sign's blue and her dress were loud)
  - a soft vignette
- It's deliberately subtle ("natural, cinematic").

**The panel.** It's a solid, dark card (86% opaque, not see-through glass) on the right third of the frame. That area stays clear of her face in both takes. It floats a few pixels and has a slight 3D tilt. Every change is timed to her exact words:

| Scene time | She says | Panel shows |
|---|---|---|
| 7.1 s | "the problem statement iTantra from ISRO" | PROBLEM STATEMENT · ISRO / **SIH26173** · iTantra |
| 12.5 s | "TTS" | TTS: text becomes speech |
| 13.7 s | "STT" | STT: speech becomes text |
| 16.3 s | "low bit rate" | Low-bitrate link: too little bandwidth for voice |
| 18.4 s | "What does that actually mean?" | NO INFRASTRUCTURE, plus three icons (mobile signal, internet, Wi-Fi router) |
| 21.6 s | "lets two Android devices communicate" | **Phone to phone. Nothing in between.** |
| 24.6 / 25.3 / 26.1 s | "no SIM, no internet, no router" | each icon is struck through and fades (brief item 4) |
| 28.4 s | "on-device speech-to-text" | HOW A MESSAGE TRAVELS / Speech → text, on the phone itself |
| 32.4 s | "compact text" | a voice waveform squeezes down into a small TEXT tag |
| 33.9 s | "Bluetooth... relay layer" | Sent over Bluetooth, phone to phone, through relays; a small packet travels down the line |
| 39.9 s | "text-to-speech" | Text → speech, in the message's language |
| 47.6 s | "So in short, speech becomes text, text is sent..., becomes speech" | IN SHORT: three icons (mic → Aa → speaker) light up one by one |
| 54.7 s | (she has finished) | the panel folds into a phone shape in the centre, and the footage darkens and blurs behind it |
| 56.0 s | - | "Let's see it work." appears inside the phone and fades out |
| 57.3-58.0 s | - | the empty phone. Scene 2 starts inside it. |

- **Why this content:** the panel explains what she leaves unclear (the jargon in the title: TTS, STT, low-bitrate). It highlights her key words as pictures (the icons, the waveform shrinking, the packet), rather than repeating her sentences.
- **Claims:**
  - The panel adds no feature claims beyond the official problem statement and her own words.
  - I deliberately left out anything I can't confirm works on a real phone: the 10 languages, encryption, speed and size numbers, "offline" as a claim.
- **Readability:** the text is 24-50 px on a dark backing. HyperFrames' contrast check passed 22 of 22 text checks. I also checked it scaled down to 640x360 (phone size), where every main line still reads.

**The doorway into scene 2 (the missing "let's show you the demo" line).**
- Her real last phrase, "So in short, the speech becomes text, and text is sent locally, and the text again becomes speech", works well as a wrap-up, so I kept it.
- The panel collapses into the phone, a soft sound plays, and a short on-screen line hands over.
- The sound is made from scratch (in `make_sfx.py`, so there are no licence issues): a quiet airy swell plus a soft two-note glass tone, kept well below the voice (its peak is about 15 dB under hers).
- There's no music, as decided.

## Build (reproducible, in git)
- `film/scene1/prep.sh`: trims, grades and conforms the clips to a constant 30 fps, and builds the cleaned voice track. Its outputs go to `film/scene1/assets/`, which is git-ignored.
- `film/scene1/make_sfx.py`: the doorway sound.
- `film/scene1/index.html`: the HyperFrames composition. `hyperframes check` passes.
- `film/scene1/mux.sh`: swaps in the exact audio mix after rendering. HyperFrames' own mix came out 3 dB hot, because it copies the mono voice onto both channels.
- **To rebuild everything:** `bash film/scene1/prep.sh && python film/scene1/make_sfx.py`, then run `hyperframes.cmd render -q high -f 30 -o <raw>.mp4` in `film/scene1`, then `bash film/scene1/mux.sh <raw>.mp4 <final>.mp4`.

## What I was unsure about (small decisions I made)
1. **The on-screen handoff line is "Let's see it work."** Other options: "Here's how it works." or "Let's show you." It's a one-word change.
2. **The panel sub-lines "through relays" and "in the message's language"** follow what she says. If multi-hop relaying or multilingual TTS isn't confirmed working on a real phone yet, those sub-lines should go. Tell me and I'll remove them; it's a 4-minute re-render.
3. **The accent colour is a soft teal (#8FE3D4).** It's a placeholder until `brief/style.md` is written in batch 3. Red is reserved for SOS.
4. **Loudness:** -16 LUFS for now. The final film loudness gets set in batch 5.
5. **Font:** Segoe UI Variable, which is installed on this PC. It isn't in the repo, because the licence doesn't allow redistribution. Renders must happen on a Windows PC (vivek-pc), which is already the rule.
6. **I didn't stabilise the handheld shake.** It's mild and feels natural. Say if you want it steadier.
7. **RNNoise:** I tried a stronger neural denoiser, which needed downloaded model files. Claude Code's safety check blocked running them, so I didn't use it. The files sit unused in `local/models/rnnoise/` and can be deleted.

## What Vivek needs to decide
- Listen to `voice_before_after.mp3`. Is the voice clean enough, or does it sound watery? I can go gentler or stronger.
- Look at `grade_before_after.jpg`. Keep this look, or make it warmer, punchier, or more muted?
- Should "through relays" and "in the message's language" stay on the panel (point 2 above)?
- Is "Let's see it work." OK as the handoff line?

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
