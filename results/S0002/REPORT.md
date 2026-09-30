---
status: failed
---

# S0002 — scene 2 slot preparation

The required raw take, `RENDERS:scene2/app/vachana_send.mkv`, is absent. `RENDERS:scene2/app/vachana_send.mp4` is also absent. The real take could not be prepared, so the two requested drafts and four take-specific stills could not be made. The existing T0007 drafts were left intact; they do **not** contain these changes.

## Made

- `film/scene2/main/prep_slot.py` crops the status-bar top, trims VFR MKV/MP4 input, makes 30 fps H.264 yuv420p with even dimensions and CRF 16, and either encodes AAC 48 kHz or drops audio. It validates the output before replacing an existing prepared slot. It applies no grade or colour filter.
- `film/scene2/main/slots.json` now points `maps` to `RENDERS:scene2/app/maps_fallback.mp4`. The 1080×2400, 105-frame, silent fallback rendered successfully at high quality.
- `vachana_send` timing now uses source `--in 1.55`: logged PTT down 1.63 becomes slot 0.08, PTT up 6.84 becomes slot 5.29, and Send 13.67 becomes slot 12.12. `sent_at` is 12.27. Duration is 394 frames / 30 = 13.133333 s, leaving about 1.013 s after the Send tap.
- `build.py` now measures each present slot's aspect and centres it at full frame height. Its automatic T0007 preview write was removed so later builds do not overwrite another worker's results. `index.html` and `timeline.json` were regenerated. `hyperframes.cmd check` passed with no errors; it reported the existing duplicate-media lint warning and intentional side-layer overflow information.
- Two source previews are in `results/S0002/preview/`: `maps_fallback.jpg` and `sonar.jpg`, each 960 px wide. These are not stills from the requested new drafts.

The clean spoken line is at slot 0.182–4.762 s. PTT down at 0.08 s precedes her voice by 0.102 s; PTT up at 5.29 s follows it by 0.528 s. This is the intended alignment from the tap log, pending visual review against the missing take.

## Prepare recordings

Run this exact command when the missing take is restored, then run `python film/scene2/main/build.py`:

```powershell
python film/scene2/main/prep_slot.py vachana_send local/renders/scene2/app/vachana_send.mkv --in 1.55 --audio drop
```

Examples for remaining real recordings under `local/renders/`; choose each actual trim start after reviewing that take:

```powershell
python film/scene2/main/prep_slot.py yash_receive local/renders/scene2/app/raw/yash_receive.mkv --in 0 --audio keep
python film/scene2/main/prep_slot.py yash_reply local/renders/scene2/app/raw/yash_reply.mkv --in 0 --audio keep
python film/scene2/main/prep_slot.py vachana_reply local/renders/scene2/app/raw/vachana_reply.mkv --in 0 --audio keep
python film/scene2/main/prep_slot.py maps local/renders/scene2/app/raw/maps.mkv --in 0 --audio drop
```

Each command uses the slot duration in `slots.json` unless `--dur` is supplied. `--crop-top` defaults to 110 px. A real `maps` recording would need `maps.path` changed back to `RENDERS:scene2/app/maps.mp4` before building.

## New timeline specified by `timeline.json`

These are the composition times after the slot-duration change. They are not yet present in the existing draft MP4 files.

| Segment | Start | End |
|---|---:|---:|
| Doorway | 0.000 | 3.000 |
| Bench | 3.000 | 7.700 |
| `vachana_send` | 7.700 | 20.833 |
| Freeze; N1 at 21.033 | 20.833 | 24.433 |
| Walk | 24.433 | 30.433 |
| `maps` | 30.433 | 33.933 |
| Yash before notification | 33.933 | 36.600 |
| `yash_receive` | 36.600 | 45.600 |
| Yash after notification | 45.600 | 52.667 |
| `yash_reply` | 52.667 | 57.167 |
| `sonar_a`; N2 at 57.167 | 57.167 | 64.167 |
| `relay_1` | 64.167 | 70.167 |
| `relay_2` | 70.167 | 76.167 |
| `relay_3` | 76.167 | 82.167 |
| `sonar_b`; N3 at 86.167 | 82.167 | 88.167 |
| Sonar fade; N4 at 88.467 | 88.167 | 90.767 |
| `vachana_reply` | 90.767 | 97.767 |
| Final hold | 97.767 | 98.267 |

## Checks and remaining work

The prep tool passed synthetic MKV checks with AAC kept and dropped, including frame rate, frame count, crop, and output streams. The map fallback has 105 frames at 30 fps and no audio. `hyperframes.cmd check` passed on the updated composition with the missing take still shown as a placeholder.

After restoring the raw take: prepare it with the command above, build the scene, verify both `RENDERS:scene2/scene2_draft_music.mp4` and `RENDERS:scene2/scene2_draft_nomusic.mp4` at −16 LUFS and ≤−1.5 dBTP, and extract the six requested 960 px JPGs from the new no-music draft: dissolve, PTT hold, Send tap, after freeze, maps, and sonar. Those render and preview requirements remain incomplete.

## Files moved out of git by the listener

- `film/scene2/main/assets/walk.mp4` (29.7 MB) was too big for git. Moved to local path: `RENDERS:S0002/film/scene2/main/assets/walk.mp4` (inside renders_dir on vivek-pc)
