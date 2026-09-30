---
status: done
---
# T0014: scene 3 red SOS sonar (sos_in, sos_sonar, sos_dive), claude-second

All three segments build, pass `hyperframes check` with 0 errors, and render at exactly their lengths on yojitth-pc. The only warning is Three.js r160's own deprecation note. Each segment has an sfx stem, and there's one separate music stem. I did all the building myself, so no S-tasks were needed.

## Segments (1920x1080, 30 fps; frame counts checked in the renders)
| Segment | Length | Frames | What happens |
|---|---|---|---|
| `sos_in` | 2.000 s | 60 | Opens on the slot's last frame (the searching state): the phone centred at full height with 28 px corners, over sospart1 (its last frame), graded, blurred and at 55 % brightness. Two soft red rings grow out of the "Searching for nearby help…" spot (0.15 and 0.55 s) with a red glow. At 0.75-1.20 the phone shrinks into the centre and fades. A soft red flare hands over to the sonar campus (fades in 0.85-1.15), with the camera close on Vachana's point. The first red wave leaves her point at 1.10. The camera pulls back and lands exactly on `sos_sonar`'s first frame. |
| `sos_sonar` | 9.000 s | 270 | Scene 2's campus in its cold tones, drifting slowly. Red waves leave Vachana's point at 0.90, 2.70, 4.45 and 5.975 s, and her point breathes with each one. Each wave reaches a little further; the earlier waves fade before Vivek. **The 5.975 wave reaches Vivek at 8.00 s**: his point appears lit red, with a red ping and the label "Vivek". It stays calm through 1.0-7.5 s for N6. |
| `sos_dive` | 1.500 s | 45 | The scene 2 dive, into Vivek's point (0-0.95). The red flare slides onto his phone as graded sospart2 fades up (0.62-1.0). A soft red glow at the phone fades in over 1.2-1.5. **The last frame is src 2.967 (frame 89) of sospart2**, so `lab_a` continues cleanly at src 3.0. The plate plays src 1.9-2.967 from 0.4 s. |

The cuts are continuous: the last frame of `sos_in` matches the first of `sos_sonar` (same camera and wave state), and the last of `sos_sonar` matches the first of `sos_dive`. All three run on one shared "sonar time", so the waves and camera carry across the cuts.

**Positions** (image-frame pixels, same frame as scene 2, illustrative):
- **V (Vachana): (330,598)**, the same as scene 2.
- **Vivek: (350,722)**, inside the courtyard block just south of her (block_d), 126 px (about 70 m) from V. It stands in for the chemistry lab. I don't know which building the lab really is, so move it in `cues.py` if the lead or Vivek does.

**Colours:** the red waves use T0012's `#E65A63` ring, `#D62F40` glow and `#A52936` wake. Vivek's point is red. The campus and Vachana's point keep scene 2's cold tones. There are no relay points, packet, hops or route.

## The app still (build input)
- The input is `RENDERS:scene3/app/vachana_sos_last.png`, the portrait last frame of the `vachana_sos` slot. **It isn't recorded yet, so `sos_in` shows a marked placeholder card** (`APP: vachana_sos (last frame: searching)`).
- Once the still exists, run `python film/scene3/sonar/build.py plates pages` and re-render `sos_in`.
- The build crops the top 110 px, like the scene 2 slots, and **never grades the still**.
- **Set `APP_STILL['search_xy']` in `cues.py`** to where the pulsing "Searching…" element sits, as a fraction of the cropped still. The default is the centre (0.5, 0.5). The red rings grow out of that spot.
- I tested this path with a synthetic still, and the layout and rings worked. I then deleted the test image.

## Sound (48 kHz stereo, all procedural with fixed seeds)
The stems are exactly as long as their segments and are placed in their compositions.

| Stem | Level | Cue times |
|---|---|---|
| `sos_in_sfx.wav` | -27.4 LUFS, peak -16 dBFS | Soft searching pulses at 0.15 and 0.55. A soft swell at 0.75 as the phone goes into the campus. A red SOS wave at 1.10. |
| `sos_sonar_sfx.wav` | -27.8 LUFS, peak -16 | Red SOS waves (low, soft tone plus a swell, no boom) at 0.90, 2.70, 4.45 and 5.975. The ones inside the N6 zone are 3 dB softer. **A low two-note "found" tone at 8.00** as the wave reaches Vivek. |
| `sos_dive_sfx.wav` | -29.5 LUFS, peak -16 | A quiet dive whoosh peaking at 0.80. The last 0.25 s dips, leaving room for `lab_a`'s notification sound at +0.1. |
| **`sos_music.wav`** (separate; not in any video or sfx stem) | -22.0 LUFS, peak -9.7 | 12.5 s covering sos_in → sos_sonar → sos_dive. A low C-minor bed with a soft double "heartbeat" on every red wave, and a faint tension tone rising into the arrival. **It's 9 dB lower from music time 3.0 to 9.5 s** (sos_sonar 1.0-7.5, N6). It settles by 12.5 s, and there's no music in the lab. |

Stem files:
- `film/scene3/sonar/<segment>/assets/<segment>_sfx.wav`
- `film/scene3/sonar/music/sos_music.wav`
- the measured levels and cues: `film/scene3/sonar/music/sound_summary.json`

## Build and render
1. Run `python film/scene3/sonar/build.py` from the repo root. It needs `machine.local.json`, ffmpeg, numpy and scipy. It builds:
   - the plates: sides, the app still if present, and the dive plate
   - the pages: `index.html` per segment, plus copies of gsap, three, `sonar.js`, `sos.js` and the css (the copies are not committed)
   - the sound
   - Steps can be run alone: `build.py plates | pages | sound`. It takes about 3 min here.
2. Render each segment: `cd film/scene3/sonar/<segment> && hyperframes.cmd render -q high -f 30 -o <out>.mp4`. On this PC with standard quality it takes under 1 min each.
3. T0016 picks the segments up from `film/scene3/sonar/`.

**Files in git** (`film/scene3/sonar/`): `build.py`, `cues.py` (every time and position), `sound.py`, `shared/` (`sos.js` for the waves and points, `sos.html.tpl`, plus copies of scene 2's `sonar.js`/`sonar.css`), the generated `<segment>/index.html`, `geo.js`, `hyperframes.json` and `meta.json`, and `music/sound_summary.json`. Scene 2's folder is unchanged.

**Preview:**
- `results/T0014/preview/`: 7 stills, plus `sos_section_preview_540p.mp4` (12.5 s, with music, 1 MB).
- Full-res renders are in `RENDERS:scene3_sonar/` on yojitth-pc.

## Things to check
- **Vivek's point:** it's illustrative, in the courtyard block south of Vachana. Move it if the real chemistry lab is elsewhere; the wave timing re-derives from `WAVE_SPEED`, so only the last wave's start time in `WAVES` needs retuning.
- **"The search keeps reaching further":** each wave fades a little further out than the last, and only the last one reaches Vivek. It's how I showed repeated searching without earlier waves passing him unanswered. It doesn't claim any range, and no numbers are shown.
- **The red glow at his phone** is deliberately soft (visible, not a flash) on the bright lab frame.
- **Sound taste** needs Vivek's ears.
