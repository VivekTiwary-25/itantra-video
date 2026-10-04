---
status: done
---

# F0020 — Scene 2 v3a fixes

- Held the recorded `vachana_send` app's **“Sent to Yash”** frame beneath the flying message card. The lifted message area no longer becomes a blank screen.
- Added a 1.9× Yash notification punch-in and a 1.7× Logs-row punch-in, with 0.6 s easing. The screen recording runs at its original speed. The notification arrives at app time 1.45 s; the punch stays through 0.8 s after the tap. The overlapping Logs punch stays through the row opening.
- Set `Sped up 26×` to 34 px, bottom left. Rebuilt with the F0013 overhead route and current glass kit. Captions use the kit's 46 px type; split captions are centred at x=616 within the camera panel and stay clear of the phone.
- Rebuilt `film/scene2/v3a/index.html` and the local assets. `results/F0020/preview/` contains all twelve F0004-named stills, `banner_punch.jpg`, `logs_punch.jpg`, a 480-px-per-frame `phone_sheet.jpg`, and a 960×540 H.264/AAC preview (5.05 MB).

`node film/scene2/v3a/build.js --preview` completed, including `hyperframes.cmd check`; `git diff --check` passed. The preview stills were extracted from the final rendered movie and reviewed at phone size. The default cut remains **44.154 s**. Its final 30 fps frame remains `yash_app` at slot time **11.690 s**, on `#0a0d12`, with phone rect **x=735, y=40, width=450, height=1000 px**. `YASH_REPLY` remains false.

Local render artifacts: `RENDERS:scene2/v3a/scene2_picture_540.mp4`, `RENDERS:scene2/v3a/scene2_dialogue_sfx.wav`, and `RENDERS:scene2/v3a/scene2_music.wav` (silent bed).

## Files moved out of git by the listener

- `film/scene2/v3a/assets/walk.mp4` (24.0 MB) was too big for git. Moved to local path: `RENDERS:F0020/film/scene2/v3a/assets/walk.mp4` (inside renders_dir on yash-pc)
