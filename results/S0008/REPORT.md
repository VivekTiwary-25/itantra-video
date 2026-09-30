---
status: done
---

# S0008 caption timing refresh

Updated `film/captions/captions.json` to scene 2 duration 102.5 s and scene 3 duration 60.2 s. Scene 3's stored segment starts now match T0016. Regenerated all three transparent overlays and SRTs. The machine has no Python executable, so `results/S0008/build.mjs` generated the files using the same HTML/CSS/JS and SRT template as `film/captions/build.py`.

For Yash's first line, the confirmed clean-audio offset of -0.37050 s places “Oh” at scene 33.56250 s, during the end of `maps`; the line ends at 36.28250 s. His second line comes from the clean track beginning at 3.97050 s in `yash_after_notification` and therefore starts at 53.46250 s. Scene 3's SOS line remains at slot 4.1 + `listen_at` 0.171 = 4.271 s. Vivek's line remains at 44.505 s. Narration uses the timelines' fixed starts and the existing phrase lengths: N1 3.1 s, N2 4.2 s, N3 1.4 s, N4 2.0 s, N5 3.6 s, and N6 6.5 s. T0016 gives the N5/N6 starts; their existing caption spans supply the phrase lengths.

## Caption starts, seconds from each scene's start

| Scene | Caption | Old | New |
|---|---|---:|---:|
| 1 | Hello, dear viewers. | 0.490 | 0.490 |
| 1 | We are from team chmod 777 | 1.850 | 1.850 |
| 1 | from the National Institute of Engineering. | 3.360 | 3.360 |
| 1 | I am Vachana. | 5.930 | 5.930 |
| 1 | We are discussing on the problem statement | 7.070 | 7.070 |
| 1 | iTantra from ISRO. | 8.820 | 8.820 |
| 1 | So, it's Indian multilingual TTS | 10.990 | 10.990 |
| 1 | and STT aided neural transceiver | 13.260 | 13.260 |
| 1 | radio access for low bit rate communication. | 14.510 | 14.510 |
| 1 | What does that actually mean? | 18.020 | 18.020 |
| 1 | Our system, iTantra, | 19.940 | 19.940 |
| 1 | lets two Android devices communicate | 21.380 | 21.380 |
| 1 | even when there is no SIM, | 23.250 | 23.250 |
| 1 | no internet, no router, connections, nothing. | 24.920 | 24.920 |
| 1 | Our on-device speech-to-text model | 27.720 | 27.720 |
| 1 | takes the speech and converts | 29.690 | 29.690 |
| 1 | the speech into compact text. | 31.430 | 31.430 |
| 1 | The Bluetooth-based transport and relay layer | 33.500 | 33.500 |
| 1 | will send this text into another device. | 35.870 | 35.870 |
| 1 | The text-to-speech model will again | 39.420 | 39.420 |
| 1 | convert text into speech, | 42.300 | 42.300 |
| 1 | which is in the message's language. | 44.800 | 44.800 |
| 1 | So, in short, | 46.390 | 46.390 |
| 1 | the speech becomes text and text is sent | 47.840 | 47.840 |
| 1 | locally, and the text again becomes speech. | 50.560 | 50.560 |
| 2 | Hey dude, I'm in the campus near the entry benches, | 7.882 | 7.882 |
| 2 | where are you? | 11.202 | 11.202 |
| 2 | Let's see how far that message | 21.033 | 21.033 |
| 2 | actually has to travel. | 22.533 | 22.533 |
| 2 | Oh, it's too hot here. | 33.933 | 33.563 |
| 2 | I'm in the garden. I'll come to you. | 50.230 | 53.463 |
| 2 | But how did that happen? | 57.167 | 61.400 |
| 2 | Bluetooth doesn't reach that far. | 59.367 | 63.600 |
| 2 | And that's how it gets there. | 86.167 | 90.400 |
| 2 | His reply comes back the same way. | 88.467 | 92.700 |
| 3 | What if you need help, but don't know who's nearby? | 0.300 | 0.300 |
| 3 | I'm lost somewhere near the construction site. | 4.271 | 4.271 |
| 3 | Please reach me out. | 7.191 | 7.191 |
| 3 | Help me anyone. | 8.371 | 8.371 |
| 3 | iTantra searches nearby for help. | 21.100 | 21.100 |
| 3 | If someone accepts, they can hear the SOS and reply. | 24.300 | 24.300 |
| 3 | Wait, | 44.505 | 44.505 |
| 3 | I'm in the chemistry lab. | 44.985 | 44.985 |
| 3 | I'll come get you, wait. | 46.065 | 46.065 |

The changed scene 2 cue ends are 55.503, 63.600, 65.600, 91.800, and 94.700 s, respectively; the “Oh” cue still ends at 36.283 s. Every updated boundary is within 0.001 s of its mapped source or narration time. The scene 3 cue times already matched the T0016 timeline; its duration and stored segment metadata were stale.

## Checks

- `hyperframes.cmd check film/captions/scene1`: passed; zero lint, runtime, layout, or motion issues.
- `hyperframes.cmd check film/captions/scene2`: passed; zero lint, runtime, layout, or motion issues.
- `hyperframes.cmd check film/captions/scene3`: passed; zero lint, runtime, layout, or motion issues.
- Every cue overlapping a centred app phone, including the scene 2 send freeze, is left-aligned. The left caption box spans x=42–692; the phone spans x=717–1203. Other cues are bottom-centred.

`brief/style.md` is still absent. No media, fonts, URLs, or absolute paths were added.
