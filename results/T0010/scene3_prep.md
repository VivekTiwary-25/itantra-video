# Scene 3 SOS footage prep

Source times below are seconds from the start of each video. Observations come from frames sampled at approximately 1-second intervals; the eight linked previews are ungraded frames at 960 × 540 px. This is an inventory and cut suggestion, not an edit or proof of app behavior.

## `FOOTAGE:Video/sospart1.mp4` — Vachana near construction

Duration 10.640 s; 1920 × 1080, approximately 30 fps, BT.709. Fixed wide shot. Vachana stays around the center, with the unfinished high-rise behind her, rubble at frame left, trees, and a dirt road. No other person is apparent in the sampled frames.

| Video interval | Picture and phone position |
|---|---|
| 0–1 s | Vachana enters/settles left of center, looking down. Gold phone is low at her right side; display faces her. |
| 1–2 s | She reaches the center of the path and starts to bring the phone up from waist height. |
| 2–3 s | Phone comes to mid-chest; she looks down and starts using it with both hands. |
| 3–4 s | Centered, head down, both hands on the phone at chest height. |
| 4–5 s | Still looking at the phone; mouth begins to move. Phone upright at chest height, back toward camera. |
| 5–6 s | She lifts phone closer to her mouth and looks up; speech/action reads clearly in the wide shot. |
| 6–7 s | Turns toward frame left while holding phone near mouth, apparently speaking. |
| 7–8 s | Faces more toward camera again; phone upright near mouth/chest. |
| 8–9 s | Phone stays near mouth, then lowers slightly; she glances toward frame right. |
| 9–10 s | Looks off toward frame right, phone in both hands at upper chest. |
| 10–10.640 s | Looks back down and touches hair/forehead; this feels like an outtake tail. |

**Clean speech timing.** `results/T0003/clean__sospart1.json` gives the word times in the separate recording. Applying the task's video offset **+4.271 s** yields:

| Spoken phrase | Clean time | Calculated video time |
|---|---:|---:|
| “I'm lost somewhere near the construction site.” | 0.000–2.600 | **4.271–6.871** |
| “Please reach me out.” | 2.920–3.660 | **7.191–7.931** |
| “Help me anyone.” | 4.100–4.720 | **8.371–8.991** |

The JSON contains no initial “I think”; that phrase appears only in the camera-audio ASR. These are arithmetic positions, **not verified mouth-sync points**. `results/T0002/sync.md` says the first third aligns near +4.737 s while the later section aligns at +4.271 s (466 ms difference). If clean audio replaces camera sound, check the mouth at the first sentence and align sections separately.

**Suggested cuts:** 0.7–2.4 s for the lost-location setup and phone raise; 3.8–9.4 s for her plea and anxious look around. End before the hair adjustment after 10 s. A single 3.8–9.4 s section is usable if timing is corrected locally. Preview frames: [1 s](preview/sospart1_1s.jpg), [4 s](preview/sospart1_4s.jpg), [6 s](preview/sospart1_6s.jpg), [9 s](preview/sospart1_9s.jpg).

**Limitations:** The photographed display faces Vachana and is unreadable, so Hands-free, composer review, SOS selection, sending, or a searching state cannot be established by this shot alone. Harsh daylight makes the sky/white building bright compared with her face, though she remains visible. The fixed composition is fairly steady; the construction area and rubble are legible. No apparent background people in the sampled frames.

## `FOOTAGE:Video/sospart2.mp4` — lab responder

Duration 10.701 s; 1920 × 1080, approximately 30 fps, BT.709. Fixed wide chemistry-lab shot. The man in a white polo occupies frame left. Several people work behind him at the center benches; the earlier inventory does not confirm his identity from the image alone.

| Video interval | Picture and phone position |
|---|---|
| 0–1 s | At left foreground, occupied with the bench apparatus; phone is not yet a clear focal point. |
| 1–2 s | Still working near the apparatus, head down; background people remain visible. |
| 2–3 s | Starts shifting attention from apparatus toward the phone. |
| 3–4 s | Holds phone low at chest/waist level, looking down at it. Screen faces him, away from camera. |
| 4–5 s | Both hands on phone near chest; appears to tap/read. |
| 5–6 s | Raises one hand/phone while looking down; transition from interaction to speaking. |
| 6–7 s | Phone comes up beside his face; he briefly touches his hair/temple. |
| 7–8 s | Looks back to phone at chest level, then starts lifting it toward mouth. |
| 8–9 s | Phone held horizontally close to mouth; visible speaking posture. |
| 9–10 s | Continues speaking into phone close to mouth. |
| 10–10.701 s | Continues looking at phone, held near mouth, through the clip end. |

**Clean speech timing.** `results/T0003/clean__sospart2.json` starts the recognized line at 7.540 s of the separate recording. Applying the **+0.065 s offset specified in T0010** yields:

| Spoken phrase | Clean time | Calculated video time |
|---|---:|---:|
| “Wait,” | 7.540–8.020 | **7.605–8.085** |
| “I'm in the chemistry lab.” | 8.020–9.100 | **8.085–9.165** |
| “I'll come get you,” | 9.100–9.820 | **9.165–9.885** |
| “wait.” | 9.820–10.340 | **9.885–10.405** |

`results/T0002/sync.md` reports +0.066 s, just 1 ms above the task value, but its first/last-third offsets differ by about 343 ms. The audio file is 16.63 s long, so almost six seconds extend beyond video end at this anchor. Check the final spoken section against the mouth before committing to a replacement track, and trim the excess clean recording.

**Suggested cuts:** 0.0–2.5 s establishes ordinary lab work before the phone; 3.0–5.7 s covers the phone interaction; 7.6–10.6 s carries the reply. For a tighter responder shot, use 3.0–10.6 s, leaving enough time to read the shift from phone interaction to speech. Preview frames: [0 s](preview/sospart2_0s.jpg), [4 s](preview/sospart2_4s.jpg), [6 s](preview/sospart2_6s.jpg), [9 s](preview/sospart2_9s.jpg).

**Limitations:** The phone display is hidden throughout. This cannot verify the ordinary app being used beforehand, an SOS notification, explicit Accept/Decline, acceptance, Logs, or the reply interface. The busy lab background has several people and equipment; it supports the location but distracts from the phone. Exposure is more even than the outdoor shot, though bright fluorescent ceiling lights and the white polo attract the eye. The camera appears steady in the sampled frames.
