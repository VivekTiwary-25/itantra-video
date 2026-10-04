# Overhead module (s2a, 5.0 s)

`Overhead.mount(el, opts)` once, then `Overhead.render(t)` on every seek, where t is seconds inside the 5.0 s segment (pure function of t). Text and map timings are unchanged since F0013.

## Options
| Option | Type | Use |
|---|---|---|
| `geo` | object | `window.OVERHEAD_GEO` (local OSM + outlines, written by `build.py`). |
| `walkVideo` | HTMLVideoElement | **Preferred (F0026).** The walk clip, timed by the composition (HyperFrames `class="clip"` + `data-start`/`data-duration`/`data-media-start`). The module moves it into its stage and shrinks/tilts it into the ground while it keeps playing (module t 0-0.88; hidden from 0.88). It must be playing from module t 0 to at least 0.88 s. |
| `yashVideo` | HTMLVideoElement | **Preferred (F0026).** Yash's clip `FOOTAGE:Video/normalpart6.mp4` from source 0.0, playing from module t **4.02** to 5.0 (`data-duration="0.98"`). The module shows it under the dissolve and push (t 4.02-5.0). The module's last frame is his live frame at source ~0.95 s. |
| `walkStill`, `yashStill` | image URL | Old fallback, used only when the matching video option is absent (held stills: not for the final film). |

`mount` needs `walkVideo` or `walkStill`, and `yashVideo` or `yashStill`. Video elements get the classes `overhead-walk` / `overhead-yash` and `overhead-live`. They are muted; the composition owns their timing and audio.

## What s2a (F0027) must change
Times are film seconds in today's s2a cut (overhead 24.78-29.78).

1. **Walk.** Pass a walk video that is still moving during overhead t 0-0.88 (film 24.78-25.66).
   - Today `walk.mp4` ends exactly at 24.78, and its last frame was used as `walk_last.jpg`.
   - Either extend the staged walk by 0.9 s of `FOOTAGE:Video/normalpart2.mp4` after the ramp's last source frame (202.15 s, at the ramp's closing speed or real speed), or start the overhead 0.9 s earlier over the walk's tail.
   - Then pass that `<video>` as `walkVideo`. s2a renders the overhead from `overhead.start - 0.6` with t clamped at 0, so the walk video must already be playing then too, or keep the walk layer above it until 24.78.
2. **Yash under the dissolve.**
   - Add `<video id="yashOverhead" class="clip" src="assets/yash.mp4" data-start="{overhead.start + 4.02}" data-duration="0.98" data-media-start="0" muted playsinline>`, today data-start 28.80.
   - Pass it as `yashVideo`, and drop `yashStill` / `assets/yash_first.jpg` from the final build.
3. **Continue Yash's live clip from where the module ends.** Every Yash camera source time moves 0.98 s later:
   - `yashFullVideo` `data-media-start` 0 → **0.98** (film 29.78-32.43 now shows source 0.98-3.63)
   - `yEarly` `data-media-start` 2.65 → **3.63**
   - the camera-exit source window 6.60-7.10 → 7.58-8.08
   - `YASH_REPLY` `yReply` 7.10 → 8.08
   - The clip is long enough (more than 12.6 s).
4. **Shift his speech and caption 0.98 s earlier on the film timeline.** His words now appear 0.98 s sooner in the shot, so the audio must follow the picture.
   - `yAt` in `build.js` (`by.yash_before_notification.start - .3705 + 1.48`): subtract 0.98.
   - The "It's too hot here." caption (`yash_before_notification.start + 1.31` → `+ 2.85`): becomes `+ 0.33` → `+ 1.87`.
   - With `YASH_REPLY`, his reply audio and caption keep their offsets relative to the `yReply` window, whose source moved with it.
   - Check his line still sits inside the full shot: film 30.11-31.65 against shot 29.78-32.43, which is fine.
5. Do not speed up or stretch anything: the shift is a source offset only.

## Preview (local)
```
python film/scene2/v3a/overhead/build.py          # assets/, stills, geo.js, index.html
# live clips for the preview (ignored, local only):
ffmpeg -ss <normalpart2 duration - 1.2> -i <footage>/Video/normalpart2.mp4 -t 1.2 -an -vf "scale=1920:1080:flags=lanczos,fps=30" -c:v libx264 -crf 18 -pix_fmt yuv420p film/scene2/v3a/overhead/assets/walk-tail.mp4
ffmpeg -i <footage>/Video/normalpart6.mp4 -t 1.2 -an -vf "scale=1920:1080:flags=lanczos,fps=30" -c:v libx264 -crf 18 -pix_fmt yuv420p film/scene2/v3a/overhead/assets/yash-head.mp4
hyperframes.cmd snapshot film/scene2/v3a/overhead --at 0.2,0.6,4.3,4.97 --no-end
```
`preview.html` uses the live clips. Set `const live = false` in it (or add `?stills` when opening it in a browser) to see the old still fallback.
