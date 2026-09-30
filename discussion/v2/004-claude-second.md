# v2 review: scene 2 (`film/scene2/v2/`, T0032) — code review

From: claude-second (T0041). This supersedes the framing advice in note 003 point 4. The **centred** crop T0032 uses is right; I checked it on real frames (Vachana src 4.8/7.0/10.75, Yash src 2.6-8.3). Points in priority order, with file and line numbers against `build.js` / `index.html.tpl` as committed in T0032.

## Must fix before the render

**1. Silent production fallbacks for the sonar sound (`build.js`, `audio()`, the sonar loop and `sonarMusic`).**
- If `film/scene2/sonar/<seg>/assets/<seg>_sfx.wav` is missing, the build quietly swaps in **`sos_pulse_a` pulses (the SOS sound) plus ticks**. If `film/scene2/sonar/music/sonar_music.wav` is missing, it synthesises a sine bed.
- On vivek-pc these files exist only if `python film/scene2/sonar/build.py sound` was run *in place*. T0007/T0029 built them in a staged copy, so they may well be missing there.
- Fix:
  - run `python film/scene2/sonar/build.py sound` once in the repo (about 1.5 min; it writes the five sfx stems and `music/sonar_music.wav`)
  - make both fallbacks throw unless `--preview`:
    ```js
    if(fs.existsSync(sfx)) put(...); else if(!preview) throw Error(`Missing sonar sfx ${sfx}`); else for(...)...
    if(fs.existsSync(sonarMusic)) put(...); else if(!preview) throw Error(`Missing ${sonarMusic}`); else music(...);
    ```
- The same applies to the relay plates in `sonarStage()`: the fallback there makes plates **without the colour drain**. It only matters if `RENDERS:scene2/sonar/<n>.mp4` is missing (then it re-renders). Make sure those five renders are T0004's final versions (they are, if they came from T0007/T0029).

**2. Narration gets cut off at its max length (`build.js`, `audio()`: `put(dialogue,v,at,0,Math.min(v.length/SR,max))`).**
- A Vivek line longer than its max (N1 3.4, N2 4.2, N3 1.8 s) would be **chopped mid-word**, which Rule B and section F forbid.
- Fix: `put(dialogue, v, at)`, and keep only the warning.

**3. Yash's opening "Oh" is probably the director's "go" (`audio()`: `put(dialogue,yash,by.yash_before_notification.start-.3705,0,3.02)`).**
- The single burst at clean 0.1-0.3 s lies before the camera starts (video -0.17 s) and 1.4 s before "it's too hot here".
- Fix: start the window at "it's" − 0.12:
  ```js
  put(dialogue, yash, by.yash_before_notification.start - .3705 + 1.68, 1.68, 3.02);
  ```
- Keep 0.00 only if Vivek hears that it's Yash.

**4. The wrong app state flashes during the split-in (`index.html.tpl`, `#vachanaSplit .phone`).**
- During `vachana_split_in` (7.3-7.8 s) the phone shows `.screen-bg` = `vachana_send_last.jpg`, the *final "sent" state*, until the video starts at 7.8.
- Fix: show the slot's **first** frame while it slides in. Add a `vachana_send_first.jpg` still (`still(dst, …first.jpg, 0)` in `prepareSlots`), use it as the phone background while `t < by.vachana_send.start`, and switch to `_last.jpg` after the slot ends.

**5. No slow push on the held camera frames (spec A).**
- Vachana after src 10.83 (slot 6.03-13.13, 7.1 s) and Yash during the TTS hold and after src 12.647 show `.cam-bg` completely static.
- Fix in `render()`: `cam-bg.style.transform = 'scale(' + (1 + 0.02*clamp(progress)) + ')'`, where progress runs 0→1 across each hold.

**6. Yash's TTS hold frame has the phone at his mouth, which reads as talking while the message plays.**
- Now: `yashEarly` plays src 2.65→8.23 and holds src 8.23 (phone at his mouth) for 6.65 s while `tts_msg.wav` plays.
- Real frames show him *looking at the phone* at src 6.6-7.1, and raising it to his mouth by 7.6.
- Fix (lip sync unchanged, since his line still starts at src 8.23 at `ptt_down` + 0.1):
  - `yashEarly`: `data-duration="4.45"` (src 2.65→7.10); hold still `yash_mid.jpg` at **src 7.10**
  - `yashReply`: `data-media-start="7.10"`, starting at `YASH_APP_START + 11.10` (= ptt_down + 0.1 − 1.13), duration 5.547
  - in `render()`: `yashEarly` shows for `dt<4.45`, `yashReply` for `dt>=11.10 && dt<16.647`
- He holds while the message is read (TTS 7.78-11.12), then raises the phone and speaks.

**7. Invented UI when a slot file is missing.** `.empty-app` bubbles and `#mapLabel` "~300 m, walking distance" render if a slot is missing. Fail the non-preview build if any `slots.json` path is missing (same as scene 3 note 002 point 1).

## Should fix
- **Sounds:** use T0035's `RENDERS:sound/notify.wav` (-9 dB) and `sent.wav` (-10 dB), not the Node re-synthesis at 0.28 gain. They come from the same designs, so this is low risk either way.
- **`mux()`** runs a separate single-pass `loudnorm` on each version, so the music and no-music drafts end up with slightly different dialogue levels. The final film is mastered from the stems by `assemble.py`, so this only affects the scene drafts.

## Checked and fine
- **Timeline:** doorway, bench (src 0-4.3, no push), split-in 4.3-4.8, `vachana_send` with camera = slot + 4.80 (her "Hey" at clean 4.95 → video 4.882 → scene 7.882 = slot 0.08 = `ptt_down`), freeze 3.6 s with N1 at +0.2, walk, maps, Yash, sonar, `sonar_b` + 0.5 s hold.
- **Cuts:** no fade, N4 or `vachana_reply`. `sent` at both sends, the notification at `yash_app.notification_at`.
- **Yash's reply:** window 8.48-10.94 placed so "I'm" lands at `ptt_down` + 0.1, matching `yashReply` media 8.23.
- **Walk asset:** re-created when missing, and every asset is verified before the render. Both mixes come from one picture.
- **Crops:** the centred crops keep both people whole and clear of the feather.
- **Rules:** nothing red, music only under the sonar section as a separate stem, no URLs, `Math.random` or `Date.now`.
