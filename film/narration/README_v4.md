# Narration v4: one command (spec 005 G3)

Vivek's new takes go in `local/narration_vivek/` on vivek-pc. Name each file after its line id: `N1`, `N2`, `N2a`-`N2f`, `N3`, `N5`, `N5a`, `N5b`, `N6`, `N7`, `N7a`-`N7d`. `.wav` / `.mp3` / `.m4a` / `.aac` / `.ogg` all work, and case does not matter (`n2a.wav` is fine). Then, on vivek-pc, from the lead folder (outside any sandbox):

```
python film/narration/prep_v4.py                 # every line that has a take
python film/narration/prep_v4.py --only N2a,N2b  # just these
python film/narration/prep_v4.py --no-copy       # do not push to the render machines
```

## What it does
1. **Cleans each take** with `film/narration/prep.py`'s tools: the scene-1 voice chain (RNNoise models from `local/models/rnnoise/`) and the clipping check.
   - Only leading and trailing silence is trimmed, with 80 ms margins. Nothing inside the line is cut, and nothing is time-stretched.
   - Loudness -18 LUFS, 48 kHz mono PCM16, written to `RENDERS:narration/v4/<id>.wav`.
   - A take the check calls clipped is not rejected: it gets the 30 Sep fallback (chain + limiter + one static gain to -18 LUFS). The table marks it `CLIPPED->fallback`; listen to it.
2. **Transcribes each output** with faster-whisper (`local/models/faster-whisper-medium.en`, CPU int8, word timestamps; audio decoded by ffmpeg, no PyAV).
   - It fixes the casing of iTantra, chmod 777, SIH26173, Bluetooth LE and Google Tink.
   - It writes `duration`, `text`, `words`, `status: "real"`, `take` and `cleaning` into `film/common/narration_v4.json`.
   - Without faster-whisper or the model it still writes the durations; fill `text` by hand.
3. **Copies the new wavs** with scp to `RENDERS:narration/v4/` on utkarsh-pc and yash-pc. Hosts and clone paths come from `local/swarm/itantra-video.json`; `renders_dir` is read from each clone's `machine.local.json`. It also copies to the render clone used by `tools/render_runner.py`.
   - Unreachable machines are skipped with a `SKIPPED` line, and every ssh/scp has a timeout. Re-run with `--only` for those lines once the machine is back.
4. **Prints a table:** id, new duration vs the old placeholder, transcript. Then the list of segments to rebuild.

## After it runs
1. Read the table. Check each transcript against what Vivek meant to say, and fix any wrong word in `text` by hand. Captions are built from `text`, and `film/final/caption_check.py` checks them against the audio after assembly.
2. Commit `film/common/narration_v4.json`. It holds only durations, text and word timings; the wavs stay in RENDERS.
3. Rebuild the segments whose lines changed, so their beats stretch to the new durations:

   | Lines | Segment | Rebuild |
   |---|---|---|
   | N1 | s2a | `node film/scene2/v3a/build.js` (then render) |
   | N2, N2a-N2f, N3 | s2b | `film\scene2\v3b\render.cmd` |
   | N5, N5a, N5b, N6 | s3 | `python film/scene3/v3/build.py` |
   | N7, N7a-N7d | s4 | `film/scene4/render.cmd` |

4. Re-render through the render runner, then assemble (`film/final/README_v3.md`).

## Testing without the real takes
- `--input`, `--out` and `--manifest` point at a scratch folder and a copy of the manifest, so the real manifest is not touched.
- `--skip-missing-denoise` (tests only) drops RNNoise when its model is absent, as on laptops other than vivek-pc. Without it, a missing model is an error.
