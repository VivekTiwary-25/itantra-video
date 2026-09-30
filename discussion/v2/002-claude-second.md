# v2 review: scene 3 (`film/scene3/v2/`, T0033) — first note

From: claude-second (T0041). Findings for the render helper, most important first. I haven't edited anything. I checked the code, T0033's stills, the real camera frames and the clean-audio energy.

## Must fix before the render

**1. The final picture would show the invented app UI ("mock") whenever a slot file is missing.**
- `build.py:185` `screen()`: when `slots.json`'s path doesn't exist, it builds a placeholder video *and* a `.mock` layer.
- `index.html.tpl:47-51`: that layer carries made-up UI text ("SOS request nearby / Someone needs help / Accept", "Vivek replied / Help is coming").
- That's a recreated app (the brief forbids it), and it's red-buttoned text that `qc.py` can't detect: its placeholder probe only knows scene 2's `APP:` card.
- Fix: in the non-`--page-only` path, fail loudly if any slot is missing. In `main()`, after `write_page(...)`:
  ```python
  if missing and not args.page_only:
      sys.exit("missing app slots, refusing to render: " + ", ".join(missing))
  ```
  Or at least drop the `.mock` div when rendering.

**2. `vachana_response` and `end_hold` render an invisible phone.**
- `.app-only .screen` has no height; only `.split .screen` sets `height:1000px`. T0033's `response_open.jpg` / `last_frame.jpg` show just the header text on black.
- Fix in `index.html.tpl` (style block):
  ```css
  .app-only .screen{position:absolute;top:40px;left:50%;transform:translateX(-50%);height:1000px;border-radius:32px;border:1px solid rgba(255,255,255,.14);overflow:hidden;box-shadow:0 22px 65px #000a;background:#101820}
  ```
  This replaces the current `.app-only .screen` rule. Then check that `response_side.jpg` (the blurred sides) shows the app, not black.

**3. Layout jump at the cut `vachana_sos` → `sos_in`.**
- `vachana_sos` ends in the new split screen (camera left, app right, h=1000).
- `sos_in` (unchanged sonar code) opens on the OLD centred layout: the phone at full height 1080, 509 px wide at x=705.5, radius 28, over sospart1's last frame blurred 40 px at 55 % brightness.
- The hard cut from one to the other will read as a glitch.
- Smallest fix inside v2 (a "leaving" move per spec A): over the last 0.5 s of `vachana_sos` (st ≥ duration − 0.5, power2.inOut), move `#vachana-field .screen` to the centred frame and fade the camera panel into a blurred full-frame background:
  - screen → `left:705px; top:0; height:1080px; width:509px; border-radius:28px`, with the field background going transparent
  - `.camera` → width 1920, `filter: blur(40px) brightness(.55)`
- The last frame then equals `sos_in` frame 0. Otherwise the lead must accept a hard cut.
- Also set `APP_STILL['search_xy']` in `film/scene3/sonar/cues.py` to where "Searching for nearby help…" really sits in the recording's last frame (fraction of the 1080x2290 cropped still). It's 0.5/0.5 now, and the red rings grow from there.

**4. The SOS send sound is a placeholder.**
- `build.py:305` uses T0024's `sos_pulse_a` (a sonar-type pulse) at `send_at`.
- The spec wants T0035's new `sos_send.wav`. When `RENDERS:sound/sos_send.wav` exists, use it at the gain T0035 recommends. The same goes for `sos_notify.wav` (not `sos_notice_a`) and `sent.wav`/`notify.wav`.

## Should fix

**5. Framing: centre the person a little more.**
- Real frames (sospart1 src 2.9-10.6, sospart2 src 4.7-10.65) show nobody cut off with the current crops (Vachana x≈600-990 in the 1232 panel; Vivek x≈700-1150, so he sits close to the feather).
- Shifting both crops 250 px right centres them and trims the empty left:
  - `.camera-vachana .camera-motion{left:-250px}`
  - `.camera-vachana .camera-still,.camera-vachana .camera-last{background-position:-250px center}`
  - add the same two rules for `.camera-vivek`
  - in `render()`: `v.style.objectPosition = sos ? '36.3% center' : '36.3% center'` (0.363 × 688 = 250), so the enter move lands exactly on the panel crop.

**6. A two-frame backward jump when Vivek's split starts.**
- `lab_open` ends on src 4.767, but the held still `vivek_first` is src 4.70 (`build.py:208`: `still(... 1.70)`).
- Use `1.766` so the still is the last frame of `lab_open`.

**7. `message_a` at `vachana_response` + 0.15 s** is a guess (`build.py:307`). Take the notification moment from `vachana_response.log` (the banner's arrival, minus the slot in-point) so the sound lands with the banner.

**8. Narration loudness.** `loudnorm=I=-16` (single-pass) on each short narration clip can pump. Prefer a measured static gain (as in scene 1's `build_voice`), or the -18 LUFS the cleaned files already have, with one static gain.

**9. RNNoise model.** The `CHAIN` uses `local/models/rnnoise/sh.rnnn` as well as `cb.rnnn` (`build.py:27`). Scene 1 only ever used `cb.rnnn`. If `sh.rnnn` isn't on vivek-pc, `spoken()` crashes after the long picture render. Check that it exists before rendering, or drop that step.

## Checked and fine
- **Rule B windows:**
  - sospart1 clean 0.00-4.72 (the file is only 5.47 s and starts on speech; "anyone." decays by about 4.75), so the window to 5.02 keeps "…Help me anyone." whole.
  - sospart2 7.54-10.34: speech energy is actually 7.8-10.0 s. The bursts at clean 1.0-2.1 and 11.9-12.1 (likely "go"/chatter) are outside the window.
  - Both lines are placed so the first word lands at `listen_at` / `ptt_down` + 0.1.
- **Lip sync:**
  - vachana: camera src = slot + 2.867, and `listen_at` 1.4 → src 4.267 = clean 0 at +4.271.
  - vivek: moving from slot 9.99 at src 4.75, so the line at slot 12.86 → src 7.62 ≈ video 7.6.
- **Accept:** 2.6 s into the unsped slot, with nothing cut before it.
- **Timeline:** N5 at 3.3 and N6 at 21.83 (they don't overlap her line at 7.27 or the dive). The intro card uses the same CSS values as scene 2's card. Music is a separate stem. There's no relay chain, packet or blue relay point. No `Math.random`/`Date.now`, no URLs.
