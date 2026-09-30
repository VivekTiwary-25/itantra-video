---
status: done
---

# v2 sound set

`film/sound/make_set.py` generates the five production WAVs into `RENDERS:sound/` by default, or into `--out <dir>`. Run `python film/sound/make_set.py`. It uses only the Python standard library and the existing T0024 `designs.json`; no audio source files are needed. `--sos-options` additionally generates all three SOS Send candidates in a `sos_send_options/` subdirectory.

The existing selections follow T0024's recommendations. The new `sos_send_a` is the recommended SOS Send cue: a measured downward two-note sound, lower and longer than the ordinary upward `sent_a` blip. B is a round single gesture; C is a three-step descent. The review MP3s are in `results/T0035/preview/`. `sos_send_options.mp3` plays A (0.00-0.72 s), B (1.32-2.00 s), then C (2.60-3.42 s), with 0.6 s gaps.

## Production files and starting mix gains

All measurements are on the uncompressed WAVs. Integrated LUFS is FFmpeg EBU R128, with sub-second cues padded to 1 s of silence for measurement. Apply the suggested gain at the sound's placement under dialogue; each is already normalized to a -12.0 dBFS peak before that gain.

| Production file | T0024 design | Length | LUFS | Suggested gain under dialogue |
|---|---|---:|---:|---:|
| `RENDERS:sound/notify.wav` | `message_a` | 0.620 s | -20.9 | -9 dB |
| `RENDERS:sound/sent.wav` | `sent_a` | 0.320 s | -21.8 | -10 dB |
| `RENDERS:sound/sos_notify.wav` | `sos_notice_a` | 1.160 s | -19.3 | -10 dB |
| `RENDERS:sound/sos_send.wav` | `sos_send_a` | 0.720 s | -20.4 | -11 dB |
| `RENDERS:sound/tick.wav` | `tick_b` | 0.115 s | -24.9 | -14 dB |

## SOS Send candidates

| Preview | Length | LUFS | Design |
|---|---:|---:|---|
| `preview/sos_send_a.mp3` | 0.720 s WAV source | -20.4 | Descending two-note confirmation; **recommended** |
| `preview/sos_send_b.mp3` | 0.680 s WAV source | -20.2 | Single rounded downward gesture |
| `preview/sos_send_c.mp3` | 0.820 s WAV source | -18.4 | Three measured descending notes |

The four individual and combined previews are each under 100 KB. Every WAV is 48 kHz, 16-bit stereo, with a -12.0 dBFS measured sample and true peak. Repeating the production generation yielded identical SHA-256 hashes for all five WAVs. The generator was run successfully on this machine with Python 3.2.2.
