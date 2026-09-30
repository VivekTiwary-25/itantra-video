---
status: done
---

# T0030 — first full cut

## Made

- `RENDERS:full_film_v1.mp4` — picture with dialogue, sound effects and the two sonar music sections.
- `RENDERS:full_film_v1_nomusic.mp4` — same picture with dialogue and sound effects.
- `RENDERS:full_film_v1_music_only.wav` — separate music layer, non-silent only at 117.874–148.859 s and 176.042–188.528 s.
- `RENDERS:full_film_v1_report.json`, copied to `results/T0030/assemble_report.json` for review.
- `results/T0030/preview/contact_sheet.jpg` — one labeled frame every 10 s, from 0:00 through 4:00. `preview/joins.jpg` and its six source JPGs show the three cuts frame by frame.

All three required outputs probe at **241.800 s**. The film has 7,254 frames at 1920×1080, nominal 30 fps. Encoded audio is **−16.01 LUFS** integrated and **−2.05 dBTP**. The video was joined by H.264 stream copy. Its decoded timing scan found no variable intervals; the final MP4's average-rate fraction reads about 30.003 fps because the mux reports the last video packet about 21 ms short. QC now accepts this small container rounding while still checking decoded timing.

| Scene | Starts | Length |
|---|---:|---:|
| Scene 1 v3 | 0:00.000 | 0:56.467 |
| Scene 2 | 0:56.467 | 1:42.500 |
| Scene 3 | 2:38.967 | 1:02.833 |
| Title | 3:41.800 | 0:20.000 |

## Scene 3 and title

The replacement SOS logs are dated after 16:55. All four app slots were prepared from the replacement recordings with recording audio dropped. Vachana's Hands-free line begins at slot +1.400 s; iTantra's own SOS TTS begins at Vivek's slot +8.290 s, 0.15 s after `tap_play`. The reply slot holds its last confirmation frame for 0.6 s. Status bars are retained on `vivek_sos` and `vachana_response`. The `SOS sent` image now drives `sos_in`; no invented searching label appears. Scene 3 rebuilt with no missing assets at 62.833 s, with separate dialogue/SFX and music WAVs.

| Slot | Raw trim, seconds | Prepared length |
|---|---:|---:|
| `vachana_sos` | 0.640–13.607 | 12.967 s |
| `vivek_sos` | 4.460–17.727 | 13.267 s |
| `vivek_reply` | 21.250–26.183, final 0.6 s held | 4.933 s |
| `vachana_response` | 4.330–13.797 | 9.467 s |

The title was rebuilt and rerendered with **`~200 m`**; a rendered frame was visually checked. S0005 had already built the title at `~400 m`, so its composition and quiet tick audio were reused while the distance render was replaced. No S-task had prepared the replacement scene 3 recordings; S0006 was a read-only audit.

`film/final/assemble.py` now uses a small peak limiter when the raw mix cannot reach −16 LUFS under the true-peak ceiling by linear gain alone. The raw mix measured −17.43 LUFS and −2.58 dBTP; the limiter made the requested level without exceeding the peak ceiling. The script also checks the intermediate stream-copy frame rate before accepting it. `film/final/qc.py` now avoids classifying the closing title as an app placeholder; a known marked placeholder still tests positive.

## Joins and placeholders

The last scene 1 frame and first scene 2 frame both show the same empty, dark phone shape. The scene 2→3 cut moves from Yash's opened reply to Vachana on campus. The scene 3→title cut moves from Vachana's opened SOS response to the title gradient. Each pair has distinct, visible frames; none is black or duplicated. The stills are in `preview/joins.jpg`. Mean absolute RGB differences on the 960 px review JPGs are 5.10, 81.54 and 7.61 respectively.

**Remaining marked `APP:` placeholder cards: none.** The drawn campus map fallback remains at **1:26.900–1:30.400** (scene 2's `maps` slot). It says about 190 m and is a designed map visual, not a marked app placeholder.

## Full-film QC

`python film/final/qc.py` produced `results/T0030/qc.json`. Overall **FAIL** because of quiet stretches in the existing edit; these need a sound pass. No additional music was placed outside the two sonar sections.

| QC check | Result | Observation |
|---|---|---|
| Container, dimensions, codec, pixel format | INFO | MP4, 1920×1080, H.264, yuv420p |
| Frame rate; variable timing | INFO | Nominal 30/1; no changed intervals decoded |
| Audio codec, rate, channels | INFO | AAC, 48 kHz stereo |
| Stream duration alignment | INFO | 0.021 s apart |
| Black and flat frames | INFO | No run of 1 s or more |
| Frozen holds | INFO | 31 detected; review intended holds in `qc.json` |
| Placeholder card | INFO | None |
| Integrated loudness; true peak | INFO | −16.01 LUFS; −2.05 dBTP |
| Full-scale samples; channel balance | INFO | 0 clipped samples; 0 dB RMS gap |
| 10 s short-term level outliers | **FAIL** | 70–90, 150–160, 190–200 and 210–250 s |
| Silence longer than 1.5 s | **FAIL** | 20 intervals; longest 206.284–222.402 s (16.118 s) |

The longer gaps occur in app interaction and the quiet title, which contains only restrained ticks. The full interval list and 10 s loudness table are in `qc.json`. This is a first review cut, not a passed final sound mix.
