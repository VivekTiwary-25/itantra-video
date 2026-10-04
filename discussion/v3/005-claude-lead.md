# Film v4 changes (claude-lead, 4 Oct 13:20): Vivek's notes on full_film_v3_draft

Everything in `001-claude-lead.md` still applies unless changed here. Vivek's notes are the source of truth; where this file and 001 disagree, this file wins.

## G. Global
- G1. Live video never freezes. Where narration needs more time than a camera clip has, continue the shot (later source) or loop a short, invisible section of OUR OWN render (sonar pings, map pulses); never hold a camera frame.
- G2. App recordings are always shown stable: NO zoom, punch-in or crop on the app recording, and the message text is never cut off. Remove the punch-ins added in F0020 (s2a) and F0015 (s3). Readability comes from the phone size in the layout, not from zooming.
- G3. Narration: Vivek is re-recording ALL lines: N1, N2, N2a-N2f, N3, N5, N5a-N5b, N6, N7, N7a-N7d. They land as `local/narration_vivek/<id>.wav` on vivek-pc; the lead runs `film/narration/prep.py` and copies the results to every render machine as `RENDERS:narration/v4/<id>.wav`, and writes their real durations and transcripts into `film/common/narration_v4.json`.
  - Until then that file has PLACEHOLDER durations. Every composition MUST read each line's start rule and duration from `film/common/narration_v4.json` at build time and stretch its beat (loops of our own render, longer holds of graphics) to the line's length + 0.4 s, so the real takes drop in with a rebuild and no code change. If a placeholder wav is missing, build a silent placeholder of that duration (preview only).
  - Captions for narration come from the `text` field in that file (the lead fills it from a transcription of the real take).
- G4. Captions: every caption must match the audio word for word (the lead re-checks against transcriptions).
- G5. Music bed lower across the whole film and ducked further under narration, dialogue and app TTS (assembler).
- G6. Render and check at 1080p; the final export only is upscaled to 2560x1440 (ffmpeg lanczos) for YouTube.
- G7. Blue = Normal, red = SOS (accent only), gold only on Bluetooth.

## I. Intro (`film/intro_v3/`, rebuilt as v4)
- Keep the opening name/team/PS part exactly as now: the short take `FOOTAGE:Video/20261002_081346_short_intro.mp4` + `vacchna_short_intro.mp3` from her first word to the end of "SIH26173." (clean 1.36-7.02 s) with the current panel.
- Then the ORIGINAL LONG intro, part 2, clean take 1 (`FOOTAGE:Audio/vachna_south_campus_intro_part_2_take_1.mp3`; its camera clip is one of `FOOTAGE:Video/20261002_073404_long_intro.mp4` / `20261002_072612_long_intro_2.mp4`: find the one that matches by cross-correlation). Cut list (clean-audio seconds of part 2 take 1, word timings in `local/intro_words/vachna_south_campus_intro_part_2_take_1.words.json`):
  1. "But what does that mean?" 0.60-1.72 (bridge)
  2. "Our system, iTantra, lets two Android phones communicate even when there is no SIM, mobile tower, internet router connection." 2.06-8.74
  3. "A speaker talks and our on-device speech-to-text model converts speech into compact text." 9.22-13.88
  4. "A Bluetooth-based transport and relay layer sends the text to another phone." 14.24-18.26
  5. "There, text is converted back to audible speech in the messenger's language by text-to-speech model." 18.80-24.58
  Cut: "So in short, speech become text and text is sent and text again becomes speech." (repeats) and "Do you think?". Expected total ~33 s. Hide every cut behind a graphic change.
- Graphics: ONE fixed glass panel area on the right; its content morphs inside it (no panel-to-panel swaps, no old image fading into a new one). One beat per explaining sentence, with time to read:
  - sentence 2: the phone in the centre of the right side; five small round glass badges in a circle around it: `Tower`, `Mobile data`, `Wi-Fi`, `Internet`, `Bluetooth LE`; crosses on all but Bluetooth (soft gold glow). No big circle.
  - sentence 3: a waveform driven by her voice turns into a line of text on the phone.
  - sentence 4: the text folds into a compact message that travels to a second phone (Bluetooth glyph gold).
  - sentence 5: the second phone reads it aloud (sound waves from its speaker).
- End: no growing circle and no card shrinking into a corner. A frosted panel with `How the app works` drops down over her shot and, continuing down, reveals scene 2 underneath, already moving (the intro's last ~1.0 s shows `FOOTAGE:Video/normalpart1.mp4` from src 0.0; s2a continues from that exact source time).

## S2. Scene 2
- s2a starts with a mode card, same glass design as the SOS card: title `Normal` with the subline `a private message to someone you trust`, over the moving bench shot, ~2.5 s, then it clears.
- The walk must travel FROM Vachana's pin TOWARD Yash's (down-right on the map), not away.
- One smooth, direct zoom onto Yash's pin (one ease, no shake, no second push).
- Yash: re-sync so his listening matches the app playing the message. Never speed up the app screen: trim idle stretches of the recording or shift his camera clip. Keep his video, audio, his reply line and the sent ting (`YASH_REPLY` = true), but do not show the reply arriving back at Vachana.
- Relay clips: the names on the relay pins for Trisha's and Vaishnavi's clips are swapped; check who is actually in each clip against the pin name and fix the labels (Utkarsh's is right).
- Sonar explanation (s2b), after N2 "But how does that happen?": the opening pings around Vachana loop while N2a-N2e play. Every visual lives INSIDE the sonar map, attached to the pins, synced to the words; at most two short labels at once, in the existing glass pills; blue for Normal, gold only on Bluetooth:
  - N2a: a small waveform rises from Vachana's pin and condenses into a line of her real message text ("Hey dude, I'm in the campus..."). Label `Speech to text on the phone, without internet`.
  - N2b: the text folds into a small capsule, a lock snaps shut on it, a size readout ticks up to `~1.2 KB` beside it. Label `Sealed for Yash only` + small `Google Tink`.
  - N2c: faint dotted arcs preview the path from Vachana to nearby phone dots; each relay dot shows a small closed lock. Label `Bluetooth LE, encrypted at every hop`.
  - N2d: the capsule sits on one relay dot while a thin clock ring fills around it, then that dot drifts along a footpath like a person walking. Label `Waits up to 24 h and moves as people walk`.
  - N2e: a small hop counter ticks 1 to 6. Label `6 hops, tested on real phones`.
  - Then the real relay plays (N2f), then N3.

## S3. Scene 3
- SOS card: neutral frosted glass like the others (no red background); red only as a small accent on the word `SOS`. Title `SOS`, subline `help from anyone nearby, no saved contact needed`. N5 plays over the card. s2b ends on this same card (the join).
- "SOS sent" cuts straight to the sonar (no blur transition; drop `sos_in`'s blurred look).
- SOS explanation: the red pulse around Vachana loops while N5a, N5b, N6 play. Same rules (inside the map, synced, max two labels, red for SOS):
  - N5a: no line to any specific person, just her pin pulsing outward. Label `No saved contact needed`.
  - N5b: a small timer chip counts up while, step by step: the 3 strongest nearby phone dots light up with red rings (`3 strongest phones`); the ring widens (`5 phones at 10 s`); it hops outward (`2 hops at 25 s`), then (`3 hops at 60 s`).
  - N6: Vivek's dot gets a small `Accept` / `Decline` chip; `Accept` lights up. Then Vivek's pin and the scene continue as now.

## S4. Scene 4: recap + bonus (Blender on utkarsh-pc; replaces the exploded view)
- Bridge from scene 3: push into Vivek's phone on the lab clip; the lab darkens and the phone lifts out alone into the dark studio.
- Phone on a slow showroom turntable spin, rim light (N7). It opens to the processor layer; numbers appear one at a time with soft ticks (N7a-N7b): `One speech model for 9 Indian languages` / `697 MB` with a bar shrinking from `~5.9 GB`; `English: 98 MB`; `10 s of speech to text in ~1.3 s`; `Ordinary mid-range phone, ~0.9 GB of memory in use`.
- It closes; a second phone slides in on its own turntable; a message packet travels between them over Bluetooth: `~1.2 KB, 60 to 90× smaller than raw voice` (N7c); the second phone lights up and reads it aloud.
- Ends on `No new hardware.` (N7d), then straight into the cards.
- Model: the downloaded phone teardown model (lead puts it in `local/models3d/` on utkarsh-pc with its LICENSE-NOTE.md); remove any Apple logo or wordmark; keep the back camera turned away from view.
- Fallback if Blender isn't running within 30 min: a simple 3D phone body (Three.js or Blender primitive) for the spins, handing off to the image-layer teardown (`film/exploded_v2/`) at the matching three-quarter angle.

## C. Cards
- Speed up the transition into the closing card.

## T. On-screen text added in v4 (humanised; numbers and claims unchanged; use exactly)
`Normal` / `a private message to someone you trust` · `SOS` / `help from anyone nearby, no saved contact needed` · `Speech to text on the phone, without internet` · `Sealed for Yash only` / `Google Tink` · `~1.2 KB` · `Bluetooth LE, encrypted at every hop` · `Waits up to 24 h and moves as people walk` · `6 hops, tested on real phones` · hop counter `1`-`6` · `No saved contact needed` · `3 strongest phones` · `5 phones at 10 s` · `2 hops at 25 s` · `3 hops at 60 s` · `Accept` / `Decline` · `One speech model for 9 Indian languages` · `697 MB` · `~5.9 GB` · `English: 98 MB` · `10 s of speech to text in ~1.3 s` · `Ordinary mid-range phone, ~0.9 GB of memory in use` · `~1.2 KB, 60 to 90× smaller than raw voice` · `No new hardware.` · intro badges `Tower` / `Mobile data` / `Wi-Fi` / `Internet` / `Bluetooth LE` · `How the app works`.

## Stills before full renders
Vivek wants stills (full size + 480 px) of the intro, the two sonar explanations and scene 4 before any full render of those parts. Put them in each task's `results/<id>/preview/`; the lead sends them.
