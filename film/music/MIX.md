# Film v3 mix plan (music bed + dialogue)

## Files
- `film/music/cues.json`: section starts in film seconds, per-section loudness targets, ducking settings and the app's TTS windows. Retime it whenever the cut changes, then re-run both scripts.
- `python film/music/make_bed.py` writes `RENDERS:music/bed_v3.wav` (48 kHz stereo, 16-bit, full film length).
- `python film/music/duck.py --dialogue <dialogue stem>` writes `RENDERS:music/bed_v3_ducked.wav`. The dialogue stem is every voice plus the app's TTS, at film length, 48 kHz 16-bit. Each section of the bed is already set to its `lufs` target, so ducking is the only automation the assembler needs.

## Music
| Item | Value |
|---|---|
| Key | D Dorian, throughout (D minor with B natural). Fits the UI cues in `film/sound/`: notify E5/A5, sent E5/B5, SOS notice D5/G5. |
| Pulse | 72 BPM soft quarter notes in s2a. In s2b, one sonar bloom every 4 beats (3.3 s). In s3, 84 BPM. No pulse in intro or exploded; cards have only the closing chime. |
| Sound | Detuned additive pads, filtered noise air, soft rounded plucks, low sonar blooms, one shared room reverb. No drums, hits, sirens or booms. |
| Joins | 2.5 s equal-power crossfades at every section change, plus a smooth gain glide. |
| Ending | Gentle rise into the closing card (+3 dB, filter opening). A clean Dm(add9) chord with a soft D5/A5 chime lands at `closing_chord_at` (film 180 s). The last 2.5 s fade out. |

Section levels (un-ducked bed, integrated per section):

| Section | Film s | Bed | Character |
|---|---|---|---|
| intro | 0-25 | -28 LUFS | very quiet warm pad, no beat |
| s2a | 25-75 | -25 LUFS | light pulse under the walk and overhead |
| s2b | 75-110 | -25 LUFS | sonar: low D hum, slow blooms |
| s3 | 110-155 | -24 LUFS | lower register, faster pulse, quiet E/F rub on top |
| exploded | 155-172 | -25 LUFS | glassy, airy, slow pings |
| cards | 172-186 | -23 LUFS (rising) | rise, then resolves on the closing card |

## Target levels
| Element | Target |
|---|---|
| Dialogue (voices + app TTS) | about -18 LUFS short-term (3 s) on every line |
| Bed between lines | about -24 LUFS short-term (the un-ducked levels above, ±1-2 LU by section) |
| Bed under speech | about -30 LUFS short-term at most. duck.py's -10 dB puts it at about -34 to -35, which is safe. If the bed then feels too far away under speech, set `duck.speech_db` to -6. |
| Bed under the app's TTS | a further -4 dB (`tts_windows`), so the phone's voice stays clear |
| UI cues (`RENDERS:sound/`) | peaks about 6-10 dB under dialogue peaks; never masking a word |
| Whole film | -16 LUFS integrated, true peak <= -1.5 dBTP |

## Assembly order
1. Make the dialogue stem at film length (voices + TTS). Normalise each line to about -18 LUFS short-term.
2. Run `duck.py` with that stem. Check that the `tts_windows` in `cues.json` match the final TTS times.
3. Sum the dialogue stem, the ducked bed and the UI cue stem.
4. Final pass on the sum: `ffmpeg -i mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:linear=true` (two-pass: measure first, then apply with `measured_*`). The relative balance above stays as it is, and the whole mix moves to -16 LUFS. If the true peak lands above -1.5 dBTP, use the limiter that loudnorm falls back to, never a hard clip.
5. Check: `ffmpeg -i final.wav -af ebur128=peak=true -f null -` should give I about -16.0, true peak <= -1.5 dBTP.

## Do not
- Do not raise the bed under speech to fill gaps. The dialogue carries the film.
- Do not add sirens, booms or trailer hits.
- Do not cut the bed: retime `cues.json` and re-render (about 1.5 min).
