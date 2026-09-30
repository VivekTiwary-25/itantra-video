---
status: done
---

# Sound options pack

Made 15 deterministic procedural sounds in five groups. `film/sound/make_options.py` reads the design data beside it and writes 48 kHz, 16-bit stereo WAVs at a -12 dBFS sample peak. Its default destination is `RENDERS:sound_options/`, read from `machine.local.json`; `--out <dir>` overrides it. Every sound has short attack and release fades.

The repo deliverable is `results/T0024/preview/`: 15 individual 96 kbps MP3s, each under 100 KB, plus `all_options.mp3` (19.020 s). `ORDER.txt` gives each option's start and end time in that sequence, with 0.600 s of silence between sounds. The root `.gitignore` excludes MP3s; the small `preview/.gitignore` admits these previews.

## Suggested starting choices

| Use | Option | Reason |
|---|---|---|
| Message notification | `message_a` | Warm short rise without a sharp edge. |
| Sent confirmation | `sent_a` | Simple quiet two-note upward cue. |
| Callout tick | `tick_b` | Lowest, most muted tick for text landings. |
| SOS notification | `sos_notice_a` | Repetition conveys urgency without a siren. |
| SOS sonar pulse | `sos_pulse_a` | Low sweep with a soft tail, leaving room for narration. |

These are suggestions from the design and measurements; Vivek's ear decides the final choices.

## Measurements

LUFS is FFmpeg EBU R128 integrated loudness. Sounds shorter than one second were padded with silence to one second so the integrated meter could resolve them. Spectral centre is the RMS-weighted mean of FFmpeg `aspectralstats` frame centroids on the uncompressed WAV. All WAV sample peaks measured -12.00 dBFS.

| Option | Duration (s) | LUFS | Spectral centre (Hz) | Intended feel |
|---|---:|---:|---:|---|
| `message_a` | 0.620 | -20.9 | 872 | Warm, welcoming two-step chime |
| `message_b` | 0.680 | -21.6 | 778 | Clear, light glassy rise |
| `message_c` | 0.720 | -20.1 | 708 | Soft, rounded descending reply |
| `sent_a` | 0.320 | -21.8 | 898 | Quiet upward two-note assurance |
| `sent_b` | 0.340 | -20.6 | 820 | Mellow downward double tap |
| `sent_c` | 0.300 | -21.0 | 992 | Crisp, small ascending blip |
| `tick_a` | 0.085 | -23.9 | 1257 | Barely-there clean pinpoint |
| `tick_b` | 0.115 | -24.9 | 777 | Muted wooden tap |
| `tick_c` | 0.100 | -24.5 | 2006 | Fine airy sparkle |
| `sos_notice_a` | 1.160 | -19.3 | 761 | Firm repeating paired notes; urgent but calm |
| `sos_notice_b` | 1.180 | -18.0 | 751 | Measured three-step attention cue |
| `sos_notice_c` | 1.340 | -18.1 | 796 | Tense descending pair, repeated gently |
| `sos_pulse_a` | 1.200 | -19.3 | 156 | Soft low sweep with a long calm tail |
| `sos_pulse_b` | 1.220 | -20.2 | 114 | Round low heartbeat-like bloom, one pulse |
| `sos_pulse_c` | 1.240 | -20.4 | 143 | Deep, airy downward sonar wash |

## Verification and notes

The 15 WAVs were generated transiently inside the allowed result path for checking, then removed so that only small previews are committed. All were 48 kHz stereo with -12.00 dBFS sample peak; first and last samples were zero. A second generation produced an identical SHA-256 for a checked WAV. The combined MP3 duration is 19.020 s, and every individual MP3 is below 100 KB.

Python is unavailable on this worker machine, so the MP3 previews were synthesized with a temporary local Node implementation of the same equations and design data. The Python/numpy generator was reviewed but could not be executed here. On a machine with Python and numpy, run `python film/sound/make_options.py` to write the production WAVs into `RENDERS:sound_options/`.
