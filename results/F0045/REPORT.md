---
status: done
---
# F0045: assembler v4 + cards

1. **`film/final/v3_segments.json`:** order is now intro, s2a, s2b, s3, **s4**, cards. The exploded entry is replaced by s4: `film/scene4/`, `film/scene4/render.cmd`, picture `RENDERS:scene4/scene4.mp4`, dx embedded, events `RENDERS:scene4/audio_events.txt`, `expected_duration` null. Scene 4 is not in git yet, so its entry is marked TODO; set it from its REPORT.
2. **Music (spec 005 G5):**
   - **Levels:** every section target in `film/music/cues.json` is 4 dB lower (intro -32, s2a -29, s2b -29, s3 -28, s4 -29, cards -27 LUFS). The `exploded` section is renamed `s4`; `make_bed.py` gives s4 the glassy exploded-view sound.
   - **Ducking:** `duck.speech_db` -14 dB, `tts_extra_db` -4 dB. `duck.py` ducks wherever the dialogue envelope finds speech AND inside every `speech_windows` / `tts_windows` entry.
   - **Where the speech windows come from:** the assembler collects them per segment from `audio_events.txt` (dialogue / narration / TTS lines; sfx ignored), else from the timeline's `narration_starts` plus each line's duration in `film/common/narration_v4.json`. It writes them into the film cue sheet and the report.
   - `film/music/MIX.md` is updated.
3. **`assemble_v3.py --final-export`:** after a non-draft assembly whose QC exits 0, it writes `RENDERS:full_film_v4_1440p.mp4`: `scale=2560:1440:flags=lanczos`, H.264 High, CRF 16, bt709, master audio copied. It checks size and frame count. It refuses with `--draft` or `--no-qc` (exit 1, nothing written). The 1080p master stays the reference.
4. **Cards:** the transition into the closing card is now 8.0-8.35 s (was 8.0-8.8), same blur and scale style; everything else is unchanged. `hyperframes.cmd check` passes.
5. **`film/final/caption_check.py`:**
   - It transcribes the dialogue stem with faster-whisper (word timestamps; `local/models/faster-whisper-medium.en` if present), or reads a saved words file (`--words`, `--save-words`).
   - Captions come from `film/captions/v3/<segment>.json`, moved to film time with the assembly report.
   - Each heard word is assigned to exactly one caption (the one containing its midpoint, else the nearest within 0.3 s), then compared word for word after normalising case, punctuation and hyphens.
   - It prints the mismatches (missing / extra / no speech heard); exit 1 if any.
6. **README:** `README_v3.md` section 5 documents all of this.

## Tests (laptop; no video renders)
- **Draft assembly:** `assemble_v3.py --draft` runs end to end with the new order, s4 as a slate (QC exit 0).
- **Speech windows:** pulled from the real timelines, e.g. s2a N1 19.08-22.28, s2b N2 1.4-3.2 / N3 30.4-32.0, s3 N5 1.9-5.3 / N6 20.43-24.43, with placeholder durations from `narration_v4.json`.
- **`duck.py` unit test:** with silent dialogue, a forced speech window and a TTS window, the bed sits at -14.0 dB in the speech window, -18.0 dB in the TTS window, and recovers to -0.1 dB after.
- **`export_1440()`:** run on a 2 s 1080p clip, it gives H.264 High 2560x1440 with the AAC copied. The guard was checked too.
- **`caption_check.py` on synthetic captions and words** (`test_words.json`, output in `caption_check_test.txt`): it flags exactly the two planted problems, an extra "Oh" and a caption with no speech under it. The other 4/6 captions match.
- **faster-whisper is not installed on this laptop,** so the transcription path itself is untested here. It needs `pip install faster-whisper` + the model on the machine that runs it.
