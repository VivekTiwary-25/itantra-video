# Scene 2 section handover: sonar campus + three relay callouts (lead → claude-second)

Vivek approved scene 2 and the split of work (30 Sept). Deadline: **tonight, 30 Sept, 23:59 IST.** You own this section end to end. You may queue `S`-prefixed tasks to `codex-f1` and `codex-f2` (both idle), only for this section. I (lead) do scene 1 v3, the app screen recordings, the other scene-2 cuts, narration, and the final assembly and render on vivek-pc.

**Usage: I must not run out.** Please do the building and your own reviews, and only come back to me for real decisions. When you're done, send back ONE report (`results/T0004/REPORT.md`) plus a short note in this folder.

## Where this sits in scene 2
The steps below are Vivek's story, and your section is **steps 10-12**:
- **9.** (mine) The Yash clip ends. Narrator: "But how did that happen? Bluetooth doesn't reach that far."
- **10.** Dark sonar view of campus. Pulses reveal buildings as shapes and outlines. Points light up where people are standing.
- **11.** Dive into each point, and it becomes that person's real clip. For each person:
  - freeze on their frame with a slow push-in
  - colour drains from everything except their phone
  - a thin electric-blue callout line draws itself out from the phone (slanting up, then flat), with a soft tick
  - a short, calm line fades in, saying their phone passes the message along and they don't have to do anything
  - colour returns and they carry on
- **12.** Back to sonar. The message hops across the points to Yash. Narrator: "And that's how it gets there."
- **13.** (mine) Narrator: "His reply comes back the same way." Then a cut to the app. The reply is **not** shown travelling through the sonar.

## Deliverables (fixed lengths, so I can cut them in blind)
All are 1920x1080 at 30 fps. Each is a HyperFrames composition under `film/scene2/sonar/`. Render the preview on your side; I do the final render on vivek-pc from your code in git.

| Segment | Length | Content |
|---|---|---|
| `sonar_a` | 7.0 s | Opens from black. Sonar pulses reveal the campus. At about 3 s, five points light up: **V** (Vachana, start), **R1, R2, R3** (relays) and **Y** (Yash, end). Small readable labels: "Vachana", "Yash", and just a dot for each relay. The narrator line from step 9 plays over 0-3.5 s, so keep the start calm. |
| `relay_1` | 6.0 s | Vaishnavi walking, `FOOTAGE:Video/normalpart5.mp4` (3.87 s long). |
| `relay_2` | 6.0 s | Utkarsh on a call, `FOOTAGE:Video/normalpart4.mp4` (3.77 s). |
| `relay_3` | 6.0 s | Thrisha passing, `FOOTAGE:Video/normalpart3.mp4` (9.28 s). The best clean part is 0-3 s, before a walker crosses. If Thrisha *is* that walker, use her part. Check the frames. |
| `sonar_b` | 6.0 s | Back in sonar. ONE compact message packet hops V → R1 → R2 → R3 → Y, and Y's point pulses on arrival. The narrator says "And that's how it gets there." at about 4.0-5.8 s. End on a still frame, so I can cut straight out. |

**Each relay segment** follows this shape:
- 0-0.8 s: dive from the sonar into that point (you choose how: a zoom through the point, or a match-dissolve).
- About 1.2 s of the live clip.
- Freeze, with a slow push-in.
- Colour drains, except the phone.
- The callout draws on, with a tick.
- The text fades in and holds about 1.8 s.
- Colour returns and the clip carries on (if the clip runs out, hold the last frame or use slow motion).

The clips are short (3.8 s), so the freeze has to do the work.

**Callout lines** (short, calm, different each time; they must not suggest anyone was tested or measured):

| Relay | Line |
|---|---|
| R1 Vaishnavi | "Her phone passes the message on. She just keeps walking." |
| R2 Utkarsh | "His phone relays it in the background. His call carries on." |
| R3 Thrisha | "Her phone hands it forward. She keeps going." |

You can tighten the wording, but keep the meaning and keep it short. **Nothing may say "tested", "measured", "range" or any number.**

## The look (Vivek's words: "cinematic: motion and restraint, not decoration")
- **Callouts:** a thin line (2 px), small clean text (about 30-34 px, the same Segoe UI Variable as scene 1, via `local()` @font-face), and a faint glow on the phone. The line draws itself on: first a slant up, then flat, and the text fades in at the end of the line.
- **Colour:** **electric blue** (about #2EA8FF) with a faint dark edge or shadow, so it doesn't blend into the sky. Test it on the real frames. **Blue = relays. Red is reserved for SOS; never use it here.**
- **Colour drain:** everything goes grey except a soft area around the phone (a feathered mask). Keep it subtle and smooth.
- **Sonar:** inspired by the sonar in The Dark Knight: mostly dark space, scanning pulses, structures appearing from luminous point clouds and outlines, intermittent light, and recognisable geography underneath. **Not** a generic neon cyberpunk map. Use Three.js (a local copy is at `film/vendor/three/three.min.js`, r160; no CDN; workers have no internet). Plain canvas or SVG is fine too if it looks better.
- **The message packet:** one compact, locked shape. Relays must **never** show the message content.
- **Live-action colour:** match the clips to each other, then apply the shared look, which is scene 1's v1 grade: `GRADE_V1` in `film/scene1/grades.sh`. Apply it with ffmpeg to the relay clips before compositing.

## Campus geometry (real)
OpenStreetMap has the campus boundary (way 1448581759) and the roads around it, in `film/scene2/geo/nie_north_osm.json`. **It has no campus buildings**, so trace them from satellite imagery:
- Esri World Imagery, zoom 18. The bbox is lat 12.3690-12.3756, lon 76.5832-76.5915, which stitches to 1547x1260 px, north up.
- You have internet in Claude Code (the Codex workers do not). Tile URL: `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`.
- **Don't commit the imagery.** Commit only your traced outlines, as `film/scene2/geo/campus_outlines.json`, in lat/lon or in that pixel frame (say which).

**What's where.** The campus is the western cluster, bounded by the diagonal main road on the west. It contains the oval sports ground, the courtyard blocks (several under construction), the two courtyard buildings in the south-west, and the white buildings to the south-east. The industrial units east of the campus line are not campus. Include them only as faint context, or leave them out.

**The points** are in the stitched-image pixel frame, and they're illustrative placements, not measured:
- **V** (Vachana, the entry benches near the main gate): about (360, 610). The gate is where the internal road meets the main road, around (345, 605).
- **Y** (Yash, the garden by the southern white buildings): about (560, 830).
- **R1, R2 and R3:** spread them along the internal road or paths between V and Y, roughly evenly, so that each hop looks like a short, plausible step. Keep it simple.

## Sound (two versions, as stems)
- **Sound effects stem** (`<segment>_sfx.wav`, 48 kHz stereo) for each segment:
  - sonar pulses: soft, low and restrained, like a sonar ping or swell, no booms
  - callout ticks: a soft tick when the line lands
  - a small whoosh for each dive
  - a soft chime when the packet arrives at Y
  - Aim for a quiet mix; I'll balance it against the voice.
- **Music stem** (`sonar_music.wav`), one continuous low, tactical, restrained bed covering the whole section (`sonar_a` through `sonar_b`, 31 s), for **version (a)**. Version (b) is simply without it.
  - Make it yourself (synthesised in Python; no licensed or downloaded music).
  - I'll duck it under the narrator. Also give me a "narration zones" list, so the music leaves room there: 0-3.5 s, and in `sonar_b` 4.0-5.8 s.
- **Generate everything procedurally** (Python/numpy), deterministic. **No downloaded audio.**

## Rules (from the brief; all apply)
- Blue for relays, red kept for SOS.
- Relay phones never show message content; their screens aren't visible anyway.
- Nothing claims that the multi-hop relay was tested or measured. It's shown as *how the system works*.
- No "demo", debug or setup labels anywhere.
- Relays do nothing themselves. The point is that the message goes through them automatically.

## Hand-back
- **Code in git:** `film/scene2/sonar/` (the compositions, a `build` script, and the procedural sound scripts), plus `film/scene2/geo/campus_outlines.json`.
- **Media:** stays on the machines. `codex-vivek` or I will render on vivek-pc. If you pre-render previews on your side, keep them in `local/`, and put small stills or GIFs in `results/T0004/preview/`.
- **`results/T0004/REPORT.md`:** what you made, each segment's exact length, the sound cue times, how to build/render, and anything you were unsure about.
- **Timing:** please have `sonar_a` + `relay_1` ready first (by around 16:00 IST) so I can start cutting. The rest follows.
