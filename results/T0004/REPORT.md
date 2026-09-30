---
status: done
---
# T0004: scene 2 sonar campus + three relay callouts (claude-second)

All five segments are built from code in git. All pass `hyperframes check` with 0 errors, and all render at exactly the lengths below. Each segment has an sfx stem, and there's one music stem for the whole section. `sonar_a` + `relay_1` (and v1 of the other three) were pushed early in commit "T0004 progress 1". This report covers the polished version.

## Segments (1920x1080, 30 fps; lengths checked by counting the rendered frames)
| Segment | Length | Frames | What happens |
|---|---|---|---|
| `sonar_a` | 7.000 s | 210 | From black (fade 0-1.4 s). Three pulses reveal the campus from point clouds and outlines: the main road, the oval, the courtyard blocks, and the southern buildings. The industrial units to the east are faint context. The camera glides down and settles on the "overview" framing at 6.2 s, then holds. The points light up at V 3.00, R1 3.14, R2 3.28, R3 3.42 and Y 3.56 s. The labels "Vachana" and "Yash" fade in from 3.35 s. Relays are a blue dot only. |
| `relay_1` | 6.000 s | 180 | Vaishnavi, `FOOTAGE:Video/normalpart5.mp4`. Freeze at 3.0 s of the source. |
| `relay_2` | 6.000 s | 180 | Utkarsh, `FOOTAGE:Video/normalpart4.mp4`. Freeze at 2.2 s of the source. |
| `relay_3` | 6.000 s | 180 | Thrisha, `FOOTAGE:Video/normalpart3.mp4`. Freeze at 6.5 s of the source. |
| `sonar_b` | 6.000 s | 180 | Opens on the overview and pushes in slowly to a tighter frame on the route. One packet hops V→R1 (0.55-1.10), R1→R2 (1.22-1.72), R2→R3 (1.84-2.42), R3→Y (2.54-3.12) and leaves a thin blue route behind it. Each relay flashes as the packet passes. At 3.12 Y pulses (a ring, plus a sonar pulse from Y). **The frame is completely still from 5.2 s to 6.0 s.** |

**Shape of each relay segment** (the same timing for all three; everything is in `film/scene2/sonar/cues.py`):
- 0-0.8: the sonar camera dives into the relay's point. The point flares, and the flare slides onto the person as the clip fades up (0.5-0.85).
- 0.8-2.0: live clip (1.2 s).
- 2.0: freeze, with a slow push-in about the phone (x1.075 over 2.0-6.0).
- 2.05-2.55: colour drains.
- 2.35: a faint blue glow on the phone.
- 2.45-2.80: the callout line slants up, then runs flat (2.80-3.00).
- **3.00: the tick.**
- 3.00-3.35: the text fades in, then holds, fully visible, for 1.8 s (3.35-5.15).
- 5.15-5.40: the text and line fade out.
- 5.10-5.60: colour returns.
- 5.3-6.0: the clip carries on.

Callout text (your lines, split over two lines): "Her phone passes the message on. / She just keeps walking.", "His phone relays it in the background. / His call carries on.", and "Her phone hands it forward. / She keeps going." The text is 32 px Segoe UI Variable (via `local()`). The line is 2 px #2EA8FF with a dark edge and a soft blue glow. There's no number, nothing says "tested", "measured" or "range", and no screens are visible.

## Sound (48 kHz stereo, all procedural numpy/scipy with fixed seeds; nothing downloaded)
Every stem is exactly as long as its segment. Each stem is also placed in its composition, so the renders carry the sfx.

**Loudness**
| Stem | Integrated | Peak |
|---|---|---|
| sonar_a sfx | -29.6 LUFS | -18.0 dBFS |
| relay_1 sfx | -32.5 LUFS | -16.6 dBFS |
| relay_2 sfx | -32.6 LUFS | -17.2 dBFS |
| relay_3 sfx | -32.1 LUFS | -17.7 dBFS |
| sonar_b sfx | -29.8 LUFS | -15.4 dBFS |
| music | -22.0 LUFS | -9.6 dBFS |

Global quiet/level knobs: `SFX_GAIN_DB` and `MUSIC_LUFS` in `sound.py`.

**Cue times (seconds, segment time)**
| Stem | Cues |
|---|---|
| `sonar_a_sfx.wav` | Soft low sonar pings at 0.35, 2.25 and 4.30. A tiny glass blip as each point lights: 3.00, 3.14, 3.28, 3.42, 3.56. |
| `relay_N_sfx.wav` | Faint ping at 0.00. Dive whoosh peaking at 0.65. Very soft air settle on the freeze at 2.00. **Callout tick at 3.00.** Soft air lift as colour returns at 5.10. |
| `sonar_b_sfx.wav` | Ping at 0.15. A tiny air swish on each hop. Blips as the packet reaches R1 at 1.10, R2 at 1.72 and R3 at 2.42. **Soft two-note chime at 3.12** as it reaches Y. The tails drop 4 dB over the last 0.5 s. |
| `sonar_music.wav` (31.0 s) | Version (a): sonar_a → relay_1 → relay_2 → relay_3 → sonar_b, back to back. D-minor bed: sub drone, filtered pad, and a muted 16th-note ostinato at 96 BPM. The ostinato dips during each relay freeze and comes back with the colour. It settles on D minor at the arrival and fades out by 31.0 s. Version (b) is simply without this stem. |

**Narration zones** (music time; the music is already 8-10 dB lower here, and you can duck it further):
- **0.0-3.5 s** (sonar_a)
- **29.0-30.8 s** (sonar_b 4.0-5.8)

## Build and render
1. `python film/scene2/sonar/build.py` (from the repo root; needs `machine.local.json`, ffmpeg, numpy and scipy). It:
   - writes each segment folder (`index.html` from `shared/*.tpl`, plus `geo.js`)
   - **copies in** gsap, three (vendored r160), `sonar.js`, `overlay.js` and `sonar.css` (these copies are not committed)
   - builds the graded relay plates (`<seg>/assets/<seg>_plate.mp4`: live → freeze → live, with the colour drain baked in, about 4 min)
   - builds the sfx stems (`<seg>/assets/<seg>_sfx.wav`) and `music/sonar_music.wav`
   - Steps can be run alone: `build.py pages | plates | sound`.
2. For each segment: `cd film/scene2/sonar/<segment> && hyperframes.cmd render -q high -f 30 -o <out>.mp4`. On this PC with standard quality: about 85 s for the sonar segments and 50 s for the relays.
3. Optional review join: `bash film/scene2/sonar/preview.sh <dir with the 5 renders> <out.mp4> a|b [540]`.

**Colour on the relay clips:**
- First a light match to each other: per-channel gains halfway toward the three clips' shared average, clamped to ±8 %. The gains are printed by the build.
- Then `GRADE_V1` from `film/scene1/grades.sh`.
- For the drain: the grey is full greyscale, slightly darker and flatter, merged through a feathered ellipse around the phone.
- The sonar is not graded.

**Files in git:**
- `film/scene2/sonar/`: `build.py`, `cues.py` (every time and relay spec), `sound.py`, `preview.sh`, `shared/` (`sonar.js` = Three.js renderer, `overlay.js` = points/labels/packet, templates, css), and the generated `<segment>/index.html`, `geo.js`, `hyperframes.json` and `meta.json`.
- `film/scene2/sonar/music/sound_summary.json`: the measured levels and cues.
- `film/scene2/geo/campus_outlines.json`: traced by eye from Esri z18 in the stitched 1547x1260 pixel frame (the origin is stated in the file). It has 14 campus buildings (4 with courtyards), the oval, the pitch, 24 faint context units and the 5 points. The imagery stays in `local/` and is not committed.

**Previews:**
- `results/T0004/preview/`: stills of each segment, plus `sonar_section_preview_a_540p.mp4` (31 s, 3.6 MB, version a with music).
- The full-res renders are in `RENDERS:scene2_sonar/` on yojitth-pc.

## Things I decided that you may want to check
- **Thrisha is the walker in normalpart3.** She enters at about 4.5 s. The 0-3 s part has no Thrisha in it, so I used her part: the live clip is 5.0-6.5 s, the freeze is at 6.5 s, and it carries on 6.5-7.2 s. Her phone is clipped in her **front jeans pocket**, and the callout points there. It fits "she keeps going", but the phone is small in frame. A background walker is also holding a phone, and he gets no callout.
- **V position.** Your gate point (345,605) doesn't match OSM, which has the main-road junction at about (350,515) in this frame. I put V **on the internal road at (330,598)**, about 30 px from your point. R1 is at (271,715), R2 at (325,780), R3 at (440,796) and Y at (560,830). All sit on the OSM internal roads, and the hops are roughly even (about 85-130 px). All are illustrative.
- **Red:** the area that keeps its colour is tight on the phone (a per-relay ellipse), so Utkarsh's red shirt and Thrisha's pink shirt go grey. No red is used in any graphic.
- **The flare-to-person match.** At the end of each dive the point's flare slides onto where the person is when the clip comes up. For relay_3 that's the left edge of frame, where she walks in.
- **The packet** is the same 16 px rounded blue square as scene 1's packet, for continuity. It has no text or content.
- **Sound:** I can't hear it. The levels are measured, but the taste of the pings, tick, chime and music needs Vivek's ears.
- **The Three.js deprecation warning** is the only check warning. It comes from the vendored global `three.min.js` r160 build and is harmless.
- **No S-tasks were queued.** The pieces depended closely on each other (shared cues, one renderer), so it was quicker and safer to build them in one pass than to hand pieces to the Codex workers. That also kept the lead's and workers' usage untouched.
