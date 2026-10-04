---
status: done
---
# F0016: film-wide music bed (procedural) + mix plan

## Made
| File | What it is |
|---|---|
| `film/music/make_bed.py` | Rewritten; it replaces the failed F0011 sketch. Writes `RENDERS:music/bed_v3.wav` from the cue sheet. Uses numpy + scipy, is fully offline and deterministic (fixed-seed noise), and takes about 1.5 min on this laptop. |
| `film/music/cues.json` | Section starts in film seconds, a per-section `lufs` target, crossfade 2.5 s, `closing_chord_at` 180, the ducking settings, and `tts_windows`. The TTS windows are placeholders (66.5-70.5, 149-153); retime them to the final cut. |
| `film/music/duck.py` | Writes `RENDERS:music/bed_v3_ducked.wav` from the bed plus a dialogue stem. Details under "Ducking". |
| `film/music/MIX.md` | The one-page mix plan: target levels, assembly order, and the loudnorm/ebur128 commands. |
| `results/F0016/preview/bed_excerpt.mp3` | Film 80-140 s (s2b into s3 at 110 s, so the tension step lands about 30 s in). 60 s, 128 kbps, 0.96 MB. |

## Key, tempo and pulse
- **Key:** D Dorian throughout (D minor with B natural; only natural notes are used). It fits the existing UI cues in `film/sound/`: notify E5/A5, sent E5/B5, SOS notice D5/G5.
- **Pulse:** `pulse_bpm` 72. Pulse by section:
  - intro: none
  - s2a: soft quarter-note plucks at 72 BPM, chords every 8 beats
  - s2b: one low sonar bloom every 4 beats (3.3 s, a D3 glide down, same feel as the sos_pulse cues) over a D2/A2 hum
  - s3: plucks at 84 BPM (7/6 of the base), lower register, with a quiet E5/F5 rub for tension
  - exploded: no pulse, slow glass pings
  - cards: no pulse; a rise, then a soft D5/A5 chime on the closing chord
- **Never used:** drums, hits, sirens or booms.

## Section levels (measured on the rendered bed, un-ducked)
| Section | Film s | Target | Measured |
|---|---|---|---|
| intro | 0-25 | -28 | -28.0 LUFS |
| s2a | 25-75 | -25 | -24.9 LUFS |
| s2b | 75-110 | -25 | -25.0 LUFS |
| s3 | 110-155 | -24 | -24.0 LUFS |
| exploded | 155-172 | -25 | -25.0 LUFS |
| cards | 172-186 | -23 | -23.5 LUFS (lower because of the 2.5 s end fade) |

- **Whole bed:** 186.0 s, 48 kHz stereo. Integrated -24.9 LUFS (ffmpeg ebur128 agrees), true peak -10.9 dBFS, loudness range 4.4 LU.
- **Sound balance:** most of the energy is 120-1000 Hz, and above 1 kHz is about -30 to -40 dB, so the bed sits under the dialogue band. Sub-60 Hz content appears only in s3, from the A1/D2 pad notes, sustained and never a hit.
- **Section changes:** each uses a 2.5 s equal-power crossfade plus a gain glide. 1 s RMS around each boundary moves smoothly. The largest single-sample step in the file is 0.02, so there are no clicks.

## Ducking
- **Settings:** -10 dB under speech and a further -4 dB inside `tts_windows`. Detection: 10 ms RMS against a -45 dBFS threshold, held 250 ms. Movement: one pole in dB, 150 ms attack, 600 ms release.
- **Test with a synthetic stem** (noise bursts with syllable gaps, at 30-33, 67-70 and 120-125 s):
  - steady -10.0 dB under speech, with no pumping between syllables
  - -14.0 dB inside the TTS window
  - -8.9 dB 0.3 s after onset (the 150 ms time constant)
  - back to -0.5 dB 2 s after speech ends

  The test files stayed in `local/tmp`.

## Notes
- The task's -10 dB duck and the ~-30 LUFS under-speech target don't quite agree: with the bed at about -24 between lines, -10 dB gives about -34. MIX.md treats -30 as a ceiling and says to use `duck.speech_db: -6` if the bed feels too far back.
- No audio is in git. The bed, the ducked bed and the test stems are in `local/`. The only audio in results is the required 0.96 MB excerpt.
