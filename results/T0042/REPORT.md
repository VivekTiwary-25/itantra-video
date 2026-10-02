---
status: done
---

# T0042 — 30 s intro scaffold

Made `film/intro30/scene/`: eight timed camera slots, a projective phone-screen insert, three ambience/effect slots, a required clean-dialogue slot, the approved V1 camera grade, a movable top glass panel, and the 28–30 s handoff to “How the app works.” The panel uses the scene 1 glass treatment; the end title uses the existing `film/title/` dark background and type language. `brief/style.md` is still absent, so the built scene 1 values and `results/T0026/style.md` guided the visual tokens.

Preview: `results/T0042/preview/intro30-placeholder-540p.mp4` (30.000 s, 960×540, 30 fps, 167,102 bytes) plus seven PNG stills and `contact-sheet.jpg`. This preview is silent and labels missing media in grey. It is not release footage.

## Fill these slots in `shots.json`

Set each `clip` to an original `FOOTAGE:Video/<name>` or `FOOTAGE:Audio/<name>` reference. Set `in` and `out` in source seconds; `out - in` must equal `dur` within one frame. A repeated source filename is fine.

| Time | Slot | Needs |
|---|---|---|
| 0–3 | `campus_wide` | Wide empty South Campus sunrise shot. |
| 3–6 | `path_walk` | Chest-height walk down the empty path. |
| 6–10 | `stairs_plant` | Front take: down stairs, stop at plant, look around. |
| 10–12 | `phone_out` | Front take: take phone out; select a trim that omits password entry. |
| 12–14 | `airplane_mode` | Over-shoulder take: airplane mode switched on. |
| 14–18 | `push_to_talk` | Over-shoulder take: press and hold PTT. End before release and before baked transcription appears. |
| 18–28 | `short_intro` | Short intro to camera at the stairs, through “no network needed.” |
| 28–30 | `handoff` | Same short take with “Let's see it work.” |
| 12–18 | `phone_screen` | Clean SDR screen recording matched to the over-shoulder actions. Prefer the USB rerecording without the floating recorder icon. The current four corner coordinates are preview estimates and must be measured on the incoming shot. Screen recording is not graded. |

Sound slots: `campus_ambience` (0–18 s, South Campus room tone), `footsteps` (3–6 s, if usable), `stairs_ambience` (18–30 s, talking spot), optional `low_hum` (14–18 s), and required `short_intro_voice` (18–30 s, separate clean audio, synced to lips). The voice chain follows scene 1 v3; this clone currently lacks `local/models/rnnoise/cb.rnnn` and `sh.rnnn`, so those local models must be present before a production audio build. Ambient and effect slots may remain empty; all camera, phone-screen, and clean-voice slots must be filled.

Set `panel_top` after checking a real stairs frame. The initial 64 px value is for the placeholder only. The 60 px PS ID and 58 px six-word promise hold from 18 s until the 28 s transition. The screen insert uses a four-corner projective transform; check its corners against the real phone and keep the over-shoulder cut before PTT release.

## Checks

- `python film/intro30/scene/build.py --preview` built the placeholder composition.
- `python film/intro30/scene/build.py --self-test` passed the production guard.
- Plain `python film/intro30/scene/build.py` rejected all ten empty required slots before rendering.
- `hyperframes.cmd check film/intro30/scene` passed: no lint, runtime, layout, motion, or contrast errors.
- HyperFrames rendered the 30 s placeholder; ffprobe verified the final 540p file.

To use the real take, fill `shots.json`, adjust `panel_top` and the screen's four `corners`, run plain `python film/intro30/scene/build.py`, then render the generated HyperFrames composition. No footage or audio source was committed.
