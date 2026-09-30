# Lip-sync audit — T0020

Offsets place clean time `t` at video time `t + offset`. I decoded both tracks to mono 4 kHz PCM with a 300–3400 Hz band-pass filter. For every 2 s clean-audio window at a 0.5 s step, I searched every full 2 s placement in the camera audio with absolute normalized waveform cross-correlation. Peak ratio compares the winning lag against the strongest lag more than 50 ms away. Only ratios ≥2 count toward the median. Times below use the median of those confident offsets and T0003 word boundaries; source durations come from ffprobe. A low-ratio window supplies no drift evidence.

## normalpart6

Video: `FOOTAGE:Video/normalpart6.mp4` (12.647 s). Clean: `FOOTAGE:Audio/Normalpart6.mp3` (12.010 s). Confirmed offset **-0.37050 s** from 10/20 confident windows; range -0.37525 to -0.36925 s; spread **6.00 ms**, median absolute deviation 0.25 ms.

| Clean window (s) | Best video window start (s) | Offset (s) | Peak ratio | Use? |
|---:|---:|---:|---:|:---:|
| 0.0–2.0 | 0.84325 | 0.84325 | 1.218 | no |
| 0.5–2.5 | 0.12950 | -0.37050 | 3.862 | yes |
| 1.0–3.0 | 0.62950 | -0.37050 | 4.909 | yes |
| 1.5–3.5 | 1.12950 | -0.37050 | 4.716 | yes |
| 2.0–4.0 | 1.62950 | -0.37050 | 3.433 | yes |
| 2.5–4.5 | 2.12425 | -0.37575 | 1.825 | no |
| 3.0–5.0 | 2.61625 | -0.38375 | 1.716 | no |
| 3.5–5.5 | 3.11750 | -0.38250 | 1.513 | no |
| 4.0–6.0 | 3.61750 | -0.38250 | 1.282 | no |
| 4.5–6.5 | 4.11750 | -0.38250 | 1.019 | no |
| 5.0–7.0 | 4.65000 | -0.35000 | 1.018 | no |
| 5.5–7.5 | 0.41750 | -5.08250 | 1.305 | no |
| 6.0–8.0 | 5.61875 | -0.38125 | 1.045 | no |
| 6.5–8.5 | 6.11875 | -0.38125 | 1.398 | no |
| 7.0–9.0 | 6.62475 | -0.37525 | 2.868 | yes |
| 7.5–9.5 | 7.13075 | -0.36925 | 6.172 | yes |
| 8.0–10.0 | 7.62975 | -0.37025 | 6.717 | yes |
| 8.5–10.5 | 8.12475 | -0.37525 | 6.109 | yes |
| 9.0–11.0 | 8.62975 | -0.37025 | 4.455 | yes |
| 9.5–11.5 | 9.12475 | -0.37525 | 3.827 | yes |

No confident window starts: 0.0–0.0 s clean time; 2.5–6.5 s clean time.

| Spoken phrase | Video start (s) | Video end (s) | Fully inside video? |
|---|---:|---:|:---:|
| Oh, it's too hot here. | -0.37050 | 2.34950 | no |
| I'm in the garden. | 8.22950 | 9.02950 | yes |
| I'll come to you | 9.14950 | 10.26950 | yes |

Opening word positions from T0003:

| Word | Video start (s) | Video end (s) |
|---|---:|---:|
| Oh, | -0.37050 | 0.00950 |
| it's | 1.42950 | 1.54950 |
| too | 1.54950 | 1.66950 |
| hot | 1.66950 | 1.86950 |
| here. | 1.86950 | 2.34950 |

“Oh” is timed at −0.37050 to +0.00950 s. **0.37050 s of its 0.380 s interval falls before the video**; only 0.00950 s remains after video zero. This is based on the T0003 word boundary, whose “Oh” probability is 0.363.

**Verdict:** Offset confirmed in the speech-bearing windows; opening “Oh” is effectively cut off at video zero.

## sospart1

Video: `FOOTAGE:Video/sospart1.mp4` (10.640 s). Clean: `FOOTAGE:Audio/sospart1.mp3` (5.495 s). Confirmed offset **+4.27100 s** from 7/7 confident windows; range 4.27100 to 4.27125 s; spread **0.25 ms**, median absolute deviation 0.00 ms.

| Clean window (s) | Best video window start (s) | Offset (s) | Peak ratio | Use? |
|---:|---:|---:|---:|:---:|
| 0.0–2.0 | 4.27125 | 4.27125 | 5.177 | yes |
| 0.5–2.5 | 4.77125 | 4.27125 | 5.492 | yes |
| 1.0–3.0 | 5.27125 | 4.27125 | 4.756 | yes |
| 1.5–3.5 | 5.77100 | 4.27100 | 5.180 | yes |
| 2.0–4.0 | 6.27100 | 4.27100 | 5.144 | yes |
| 2.5–4.5 | 6.77100 | 4.27100 | 6.064 | yes |
| 3.0–5.0 | 7.27100 | 4.27100 | 4.972 | yes |

No confident window starts: none.

| Spoken phrase | Video start (s) | Video end (s) | Fully inside video? |
|---|---:|---:|:---:|
| I'm lost somewhere near the construction site. | 4.27100 | 6.87100 | yes |
| Please reach me out. | 7.19100 | 7.93100 | yes |
| Help me anyone. | 8.37100 | 8.99100 | yes |

**Verdict:** Offset confirmed across every measured window; all listed speech is inside the video.

## sospart2

Video: `FOOTAGE:Video/sospart2.mp4` (10.701 s). Clean: `FOOTAGE:Audio/sospart2.mp3` (16.625 s). Confirmed offset **+0.06600 s** from 6/30 confident windows; range 0.06600 to 0.06600 s; spread **0.00 ms**, median absolute deviation 0.00 ms.

| Clean window (s) | Best video window start (s) | Offset (s) | Peak ratio | Use? |
|---:|---:|---:|---:|:---:|
| 0.0–2.0 | 0.06350 | 0.06350 | 1.446 | no |
| 0.5–2.5 | 0.56475 | 0.06475 | 1.828 | no |
| 1.0–3.0 | 1.06475 | 0.06475 | 1.776 | no |
| 1.5–3.5 | 1.56475 | 0.06475 | 1.618 | no |
| 2.0–4.0 | 2.06600 | 0.06600 | 1.301 | no |
| 2.5–4.5 | 0.22650 | -2.27350 | 1.115 | no |
| 3.0–5.0 | 6.90725 | 3.90725 | 1.065 | no |
| 3.5–5.5 | 6.65550 | 3.15550 | 1.141 | no |
| 4.0–6.0 | 8.17125 | 4.17125 | 1.007 | no |
| 4.5–6.5 | 4.57000 | 0.07000 | 1.187 | no |
| 5.0–7.0 | 5.07000 | 0.07000 | 1.054 | no |
| 5.5–7.5 | 5.52875 | 0.02875 | 1.369 | no |
| 6.0–8.0 | 6.06600 | 0.06600 | 2.903 | yes |
| 6.5–8.5 | 6.56600 | 0.06600 | 3.149 | yes |
| 7.0–9.0 | 7.06600 | 0.06600 | 4.056 | yes |
| 7.5–9.5 | 7.56600 | 0.06600 | 4.734 | yes |
| 8.0–10.0 | 8.06600 | 0.06600 | 4.619 | yes |
| 8.5–10.5 | 8.56600 | 0.06600 | 6.080 | yes |
| 9.0–11.0 | 8.55025 | -0.44975 | 1.221 | no |
| 9.5–11.5 | 8.67650 | -0.82350 | 1.012 | no |
| 10.0–12.0 | 7.10475 | -2.89525 | 1.223 | no |
| 10.5–12.5 | 7.60475 | -2.89525 | 1.050 | no |
| 11.0–13.0 | 3.84750 | -7.15250 | 1.022 | no |
| 11.5–13.5 | 8.60350 | -2.89650 | 1.129 | no |
| 12.0–14.0 | 7.11700 | -4.88300 | 1.039 | no |
| 12.5–14.5 | 8.13600 | -4.36400 | 1.056 | no |
| 13.0–15.0 | 7.46475 | -5.53525 | 1.196 | no |
| 13.5–15.5 | 6.34575 | -7.15425 | 1.225 | no |
| 14.0–16.0 | 8.29950 | -5.70050 | 1.012 | no |
| 14.5–16.5 | 8.67150 | -5.82850 | 1.432 | no |

No confident window starts: 0.0–5.5 s clean time; 9.0–14.5 s clean time.

| Spoken phrase | Video start (s) | Video end (s) | Fully inside video? |
|---|---:|---:|:---:|
| wait | 7.60600 | 8.08600 | yes |
| I'm in the chemistry lab | 8.08600 | 9.16600 | yes |
| I'll come get you | 9.16600 | 9.88600 | yes |
| wait | 9.88600 | 10.40600 | yes |

The clean recording ends 5.99082 s after the video at this offset; its final spoken phrase ends inside the video. T0003 provides no punctuation for this clip, so the phrase grouping above uses its word sequence.

**Verdict:** Offset confirmed around the spoken reply; no confident evidence in the earlier and later stretches, and clean audio extends beyond the video.

