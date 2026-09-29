# Clean-audio sync, six pairs

`offset_s` means clean-audio time `t` plays at video time `t + offset_s`. Negative values place the clean recording before video zero. All values are to the nearest millisecond. Peak ratio compares the selected correlation peak with the strongest peak more than 0.2 s away; high is at least 2.0, medium is 1.4–2.0, low is below 1.4. Drift is last-third offset minus first-third offset.

| Pair | Offset (s) | Confidence | Peak ratio | First third (s) | Last third (s) | Drift (ms) | Clean audio outside video at stated offset |
|---|---:|---|---:|---:|---:|---:|---|
| normalpart1 | -0.047 | high | 2.974 | -0.047 | -0.068 | -21 | First 0.047 s and last 0.864 s |
| normalpart6 | -0.370 | high | 7.841 | -0.022 | -0.386 | -364 | First 0.370 s |
| sospart1 | +4.271 | high | 4.083 | +4.737 | +4.271 | -466 | None |
| sospart2 | +0.066 | high | 6.059 | +0.110 | -0.233 | -343 | Last 5.991 s |
| vachna part1 | +0.571 | high | 6.355 | +0.770 | +0.574 | -196 | Last 1.570 s |
| vachna part2 | +0.389 | high | 11.156 | +0.390 | +0.396 | +6 | Last 0.882 s |

Verdicts:

- **normalpart1:** Speech-energy alignment peaks clearly at -0.047 s. The two band-passed waveforms have almost no sample-level coherence at that point; verify this pair by listening or with a visible clap/word onset before replacement. Its 21 ms first-to-last difference is also measurable.
- **normalpart6:** The strongest whole-pair waveform alignment is -0.370 s, but the first third aligns near -0.022 s. A single offset will not synchronize the whole clip; inspect for an internal timing change or edit.
- **sospart1:** The later portion aligns at +4.271 s, while the first third aligns at +4.737 s. Treat +4.271 s as a later-section anchor only and align sections separately.
- **sospart2:** The strongest whole-pair match is +0.066 s. First and last sections differ by 343 ms, and nearly six seconds of the clean file extend beyond the video; use section-specific alignment and trim as needed.
- **vachna part1:** The whole-pair anchor is +0.571 s. The first third is about 196 ms later than the last; inspect the timing change before replacing camera audio across the whole clip.
- **vachna part2:** +0.389 s is consistent across the clip (6 ms first-to-last difference). This is the only pair with a strong peak and near-constant alignment throughout.

Method: ffmpeg decoded each source to mono 16 kHz PCM with a 300–3400 Hz band-pass filter under `local/tmp/T0002/`. The script correlated speech-energy envelopes or band-passed waveforms, then repeated the search on first and last thirds within ±0.5 s of the whole-pair offset. Large drift values indicate the chosen single offset is only an anchor; the outside-video intervals are calculated from that anchor and source durations. No source audio or decoded PCM is included here.
