# Lead → dispatcher (17:05): four decisions and one ordering request

1. **SOS screens are being re-recorded now** (Vivek approved typing the filmed lines into the director console; the first helper's SOS clips show the old text "I need help near the south gate." / "I'm coming. Stay where you are." and must NOT be used). New clips land in `RENDERS:scene3/app/` by about 17:25: `vachana_sos.mkv`, `vivek_take.mkv`, `vachana_response.mkv`, each with a `<name>.log` of tap times. Until then scene 3 keeps placeholders.

2. **There is no "Searching for nearby help…" screen in the app.** After Send the app shows a red ring animation (about 0.7 s), then a red check with **"SOS sent"** (about 1 s), then Home. Decision: `sos_in` starts from the "SOS sent" frame, `RENDERS:scene3/app/vachana_sos_sent.png` (re-saved with the new take), and the red ring/check is what grows out of the phone and becomes the first red sonar wave. No invented "Searching…" text. N6 ("iTantra searches nearby for help…") carries the word.

3. **Scene 3 slot mapping** (for whoever preps the slots; times are from each clip's `.log`):
   - `vachana_sos` ← `vachana_sos.mkv`: from `handsfree_tap` − 1.0 s to the "SOS sent" frame + 0.6 s (cut before the app returns to Home). `listen_at` = `handsfree_tap` + 0.4 s (her spoken SOS line starts there; it is 4.7 s long and the listening lasts 5.0 s).
   - `vivek_sos` ← `vivek_take.mkv`: from 3.0 s before `tap_accept` − 2.5 s (so the banner is seen arriving) to just before `ptt_down`. Keep the status bar (the banner drops over it). Lay `RENDERS:tts_itantra/tts_sos.wav` (iTantra's own TTS voice, 3.85 s) over it starting 0.15 s after `tap_play`, at dialogue level; drop the recording's own audio.
   - `vivek_reply` ← `vivek_take.mkv`: from `ptt_up` to 1.4 s after `tap_send` (the "Sent to Vachana" check must be visible; the app leaves it after about 1.5 s, so hold the last frame for 0.6 s).
   - `vachana_response` ← `vachana_response.mkv`: from `tap_notification` − 2.5 s to `tap_log_entry` + 4.5 s. Keep the status bar.
   - Trim any Chrome "page still loading" frames at the start of a clip.

4. **Map and title distance.** Google Maps would not open a walking route from a link (it showed Vivek's personal places, so the helper rightly stopped). The drawn map card stays ("about 190 m", straight line). So the title card's `{DISTANCE}` must be **"~200 m"** (190 rounded up), not the default "~400 m": please make sure the title render (S0005) uses `DISTANCE = "~200 m"` in `film/title/build.py`. Vivek decides later if he wants the longer walking figure.

**Ordering request:** T0030 (full film) must run AFTER the scene 3 slots are prepped from the new recordings and scene 3 is re-rendered. Please queue that as an S-task for codex-vivek ahead of T0030 (or fold it into one). If the recordings are not there when it starts, it should wait-and-check for up to 15 minutes rather than assemble placeholders.
