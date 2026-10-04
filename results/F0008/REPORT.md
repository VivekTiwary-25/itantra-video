---
status: done
---

# Scene 3 v3

Built `film/scene3/v3/` from v2, with the 1.6 s full glass SOS card reveal, real app slots, camera-to-app takeovers, three exact SOS tech lines, captions from `film/captions/v3/s3.json`, and an ending 0.4 s after Vivek's Send. `vachana_response` and `end_hold` are absent. The build copies the local glass kit into its ignored assets and refuses a production render if an app slot or required speech asset is missing. No invented app UI is generated. The staged `sos_in` builder uses moving blurred footage instead of v2's looped camera still.

## Timeline (scene seconds)

| Segment | Start | End |
|---|---:|---:|
| `card_out` | 0.000 | 1.600 |
| `s3_open` | 1.600 | 4.467 |
| `vachana_sos` | 4.467 | 17.433 |
| `sos_in` | 17.433 | 19.433 |
| `sos_sonar` | 19.433 | 28.433 |
| `sos_dive` | 28.433 | 29.933 |
| `lab_open` | 29.933 | 31.233 |
| `vivek_app` | 31.233 | 51.400 |

N5 starts 1.900; Vachana's clean line starts 5.867 and completes at 10.587; SOS Send sound starts 15.697. N6 starts 20.433. The tech lines run 19.433–22.033, 22.033–25.333, and 27.433–29.933; the third starts when the last red pulse reaches Vivek at `sos_sonar` + 8.0. SOS notification starts 30.033. Accept is at 33.833; the recording continues without a cut through the tap. SOS TTS starts 39.013. Vivek's clean line starts 44.093, 0.1 s after `ptt_down`; Sent sound starts 51.003.

## Visible moving camera ranges

| Picture | Scene time | Source time |
|---|---:|---:|
| Blurred footage behind full card | 0.000–1.600 | `FOOTAGE:Video/sospart1.mp4` 0.000–1.600 |
| Revealed Vachana, full frame | 1.600–4.467 | `FOOTAGE:Video/sospart1.mp4` 0.000–2.867 |
| Vachana, left split | 4.467–12.240 | `FOOTAGE:Video/sospart1.mp4` 2.867–10.640 |
| Blurred `sos_in` sides in production build | 17.433–19.433 | `FOOTAGE:Video/sospart1.mp4` 8.600–10.640 |
| Sonar dive into lab | 28.833–29.933 | `FOOTAGE:Video/sospart2.mp4` 1.900–3.000 |
| Vivek lab, full frame | 29.933–31.233 | `FOOTAGE:Video/sospart2.mp4` 3.000–4.300 |
| Vivek, first split window | 38.733–40.033 | `FOOTAGE:Video/sospart2.mp4` 4.300–5.600 |
| Vivek, reply split window | 42.100–47.167 | `FOOTAGE:Video/sospart2.mp4` 5.600–10.667 |

The phone moves to the centre on a dark field wherever a camera window ends. Camera footage is not held or slowed. App recordings and speech are not sped up. The slot fields required are `vachana_sos`: `duration`, `listen_at`, `send_at`; `vivek_app`: `duration`, `accept_at`, `play_at`, `ptt_down`, `ptt_up`, `sent_at` (values in `slots.json`).

## Verification and previews

`python film/scene3/v3/build.py --page-only` passed with the real `RENDERS:scene3/app/vachana_sos.mp4` and `RENDERS:scene3/app/vivek_app.mp4`. `hyperframes.cmd check` passed: zero errors or warnings in lint, runtime, layout, and motion; 2/2 contrast checks passed. It reported two informational clipped-camera overflow notices, expected for the 1920 px footage inside 1232 px panels. Thirteen 960 px JPGs cover every requested beat, TTS, and the post-Accept result in `results/F0008/preview/`. `phone-review.jpg` was inspected at 320 px per frame; TTS captions sit beside the centred phone and the Accept controls and subsequent Logs screen are visible. `python -m py_compile` passed for the builder and preview script.

On this machine SciPy is absent, so the page-only preview uses the existing `RENDERS:scene3/v2/sonar/` videos. A production render with sound requires SciPy to regenerate the staged sonar stems; the production path fails clearly before rendering if it is missing. The cached `sos_in` preview still has v2's blurred static sides, while the staged production source has the moving-side fix. No full 1080p render was made for this worker task. The TTS caption wording follows the SOS text visible in the real app slot and Vachana's clean transcript; the lead should confirm it against `RENDERS:tts_itantra/tts_sos.wav` by listening.

## Files moved out of git by the listener

- `film/scene3/v3/assets/vachana.mp4` (22.9 MB) was too big for git. Moved to local path: `RENDERS:F0008/film/scene3/v3/assets/vachana.mp4` (inside renders_dir on utkarsh-pc)
