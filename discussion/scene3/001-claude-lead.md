# Scene 3 (SOS) + title card + final assembly: the plan everyone builds to (claude-lead, 30 Sept 14:50)

Vivek approved all of this. Target: a full first cut around **17:00 IST**. claude-second stops around 18:00. Quality first: if something won't be ready, say so; don't rush it.

## Scene 3 cut list (lead's decisions; all lengths fixed unless marked slot)
Footage:
- `FOOTAGE:Video/sospart1.mp4`: Vachana near the construction site, 10.64 s. Clean audio `Audio/sospart1.mp3`, offset **+4.271 s** (clean t plays at video t+4.271). Line: "I'm lost somewhere near the construction site. Please reach me out. Help me anyone." (video ~4.27-8.99 s).
- `FOOTAGE:Video/sospart2.mp4`: Vivek in the chemistry lab, 10.70 s. Clean audio `Audio/sospart2.mp3`, offset **+0.065 s**. Line: "Wait, I'm in the chemistry lab. I'll come get you, wait." (video ~7.6-10.4 s).
- Details: `results/T0010/scene3_prep.md`.

| # | Segment | Length | What |
|---|---|---|---|
| 1 | `s3_open` | 4.1 s | sospart1 src 0.0-4.1 (she walks into place, lost, takes out her phone). **N5** "What if you need help, but don't know who's nearby?" starts at 0.3 s. Cut straight in from scene 2's last frame. |
| 2 | slot `vachana_sos` | slot, placeholder 14.0 s | App, centred portrait layout with blurred/darkened sospart1 on the sides (same layout as scene 2). Hands-free listening while her clean SOS line plays → text appears → review → she selects **SOS** (the contact row disappears) → Send → "Searching for nearby help…". The lead supplies `listen_at` (seconds into the slot where her line should start). |
| 3 | `sos_in` | 2.0 s | **claude-second.** Starts on the slot's last frame (the searching state). The pulsing "Searching for nearby help…" grows out of the phone and becomes the first red sonar wave. |
| 4 | `sos_sonar` | 9.0 s | **claude-second.** Scene 2's sonar campus. Vachana's point is the source; repeated RED circular waves spread outward. **N6** "iTantra searches nearby for help. If someone accepts, they can hear the SOS and reply." starts at 1.0 s (about 6.5 s long). A wave reaches Vivek's point at about 8.0 s and his point lights red. |
| 5 | `sos_dive` | 1.5 s | **claude-second.** Dive into Vivek's point (same dive as scene 2). The red glow becomes the notification glow on his phone in the lab: end exactly on graded sospart2 src 3.0 s, with a soft red glow at the phone that fades in the last frames. |
| 6a | `lab_a` | 1.6 s | sospart2 src 3.0-4.6: Vivek at the bench, looks at his phone. The phone's notification sound plays at 0.1 s. |
| 6b | slot `vivek_sos` | slot, placeholder 12.0 s | App, centred layout, sides = blurred sospart2. The SOS notification with **Accept / Decline** → he taps **Accept** (clearly, unhurried) → the SOS opens → Play: Vachana's SOS is heard (the slot's own audio) → he holds to talk. |
| 6c | `lab_b` | to end of line + 0.4 s | sospart2 from src 7.3 s with his clean line "Wait, I'm in the chemistry lab. I'll come get you, wait." |
| 6d | slot `vivek_reply` | slot, placeholder 5.0 s | His reply text → Send → the sent state, held about 1 s. |
| 7 | slot `vachana_response` | slot, placeholder 7.0 s + 0.5 s hold | Vachana's app: Vivek's response arrives (notification → open → visible). Sides = the app itself, blurred and dark. End of scene 3. |

Narration (computer voice "david", on vivek-pc in `RENDERS:scene3/narration/david/N5.wav`, `N6.wav`; the lead makes them): fixed starts, own track.

## Rules for scene 3
- SOS is ONE source: red circular waves from Vachana. **Never the relay chain, no packet, no hops, no blue relay points lighting up.**
- Vivek is NOT a trusted contact. Accept is explicit. Nothing auto-accepts.
- No "demo", debug or setup labels. Red is allowed here (this is SOS). The campus stays in scene 2's cold tones; only the SOS wave and Vivek's point are red.
- **Music: ONE version.** Low tactical music under `sos_in` + `sos_sonar` + `sos_dive` only, quieter where N6 speaks, delivered as a **separate stem** (`sos_music.wav`, 12.5 s) that is NEVER baked into a video or the sfx stem, so it can be dropped without re-rendering. No music anywhere else in scene 3.
- Colour: camera clips get `GRADE_V1` (`film/scene1/grades.sh`). App screens are never graded.
- Everything procedural and local: no downloaded audio, no CDN, fonts via `local()`.

## Title card (straight after scene 3, no montage)
Calm and confident, not dramatic. Dark background, clean type. Each sentence fades in on its own with a calm pause between (scene 2's soft callout tick is fine, quietly). No whooshes. The team line stays small at the bottom.
1. "We built iTantra so you can reach people over long distances, even with no cell network."
2. "Speak in any of 10 languages, and your message is read aloud on the other side."
3. "It travels phone to phone, through the people around you, across {DISTANCE} of campus."
4. "No towers. No internet. No new hardware. Just the phones people already carry."
5. "iTantra. Speak. Send. Be heard."
6. (small, bottom) "Team chmod 777 · Team ID 148903 · NIE Mysuru"

`{DISTANCE}` is a build parameter, default "~400 m". The lead sets it from the Google Maps walking distance, rounded UP to a clean number, so the card and the map never disagree.

## Final assembly
scene 1 v3 → scene 2 → scene 3 → title card = `RENDERS:full_film_v1.mp4`. Music is a separate layer across the whole film (scene 2 sonar music, scene 3 SOS music): deliver the film with music, the film without, and the music-only track.
