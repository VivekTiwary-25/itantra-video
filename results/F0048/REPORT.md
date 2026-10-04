---
status: done
---
# F0048: one-command narration v4 pipeline

## Made
- `film/narration/prep_v4.py`: `python film/narration/prep_v4.py [--only N2a,N2b] [--no-copy]`. Test overrides: `--input`, `--out`, `--manifest`, `--model`, `--swarm`, and test-only `--skip-missing-denoise`.
- `film/narration/README_v4.md`: the command, what it does, and what to do after: check/fix `text`, commit the manifest, rebuild s2a (N1) / s2b (N2-N3) / s3 (N5-N6) / s4 (N7-N7d), re-render, assemble.

## How it works
1. **Takes:** for every line in `film/common/narration_v4.json`, it finds `local/narration_vivek/<id>.<wav|mp3|m4a|aac|ogg>` (names case-insensitive).
2. **Cleaning:** reuses `prep.py`'s own `source_info` (clipping check) and `chain()` (scene-1 voice chain, run from the repo root so its RNNoise paths resolve).
   - Only leading and trailing silence is trimmed (80 ms margins, -44 dBFS activity threshold as in prep.py).
   - loudnorm -18 LUFS; 48 kHz mono PCM16 → `RENDERS:narration/v4/<id>.wav`.
   - Never time-stretched: prep.py's `atempo` squeeze is deliberately not used.
   - A take prep.py would call clipped gets the 30 Sep fallback (chain + limiter + one static gain to -18 LUFS) and is marked `CLIPPED->fallback` in the table and in `cleaning`.
   - A failing take is reported as ERROR and the others continue.
3. **Transcription:** faster-whisper from `local/models/faster-whisper-medium.en`, CPU int8, word timestamps, audio decoded by ffmpeg into numpy (no PyAV).
   - Casing fixes for iTantra, chmod 777, SIH26173, Bluetooth LE, Google Tink.
   - Writes `duration`, `text`, `words`, `status: "real"`, `take`, `cleaning`.
   - Without faster-whisper or the model: the durations are still written and the text is left for the lead (warning).
4. **Copy:** scp to `RENDERS:narration/v4/` on utkarsh-pc and yash-pc.
   - Hosts and clone repos come from `local/swarm/itantra-video.json`; each clone's `renders_dir` is read over ssh from its `machine.local.json`.
   - Plus the render clone named in `tools/render_runner.py` (HOST/RDIR), because that is where renders happen.
   - BatchMode, ConnectTimeout 10, a timeout on every ssh/scp. Unreachable targets are skipped with a SKIPPED line.
5. **Output:** a table of id, new vs old duration and text, then the list of segments to rebuild.

## Tests (laptop, `--no-copy`, scratch manifest; the real `narration_v4.json` untouched)
- **Takes used:** three real-speech snippets cut from local footage audio, named `n2a.wav` (lower-case), `N5b.mp3` and a +21 dB `N7.wav`. They stay in `local/tmp`. Synthetic tones and pink noise are removed by the chain's `afftdn` denoiser by design, so they cannot stand in for a voice.
  - **Outputs:** all 48 kHz mono. N5b went through the normal chain to -18.4 LUFS (5.13 s, trimmed from 5.2 s). N2a and N7 were flagged clipped and took the fallback, -18.0 LUFS.
  - **Manifest copy:** got duration / status real / take / cleaning.
- **Not available on this laptop:**
  - **RNNoise models:** the test used `--skip-missing-denoise`; on vivek-pc the models exist and the full chain runs.
  - **faster-whisper:** transcription was skipped with a warning.
- **Copy step,** with a fake swarm config: targets parsed (two listener clones + the render clone `utkarsh` from `render_runner.py`). Unreachable hosts were skipped cleanly within ~7 s total.
