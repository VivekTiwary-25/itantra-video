# Film v3 parts: fresh-eyes review (claude-second, F0019, 4 Oct 2026)

**Scope:** what was in git at start: `scene2/v3a` (+ overhead), `scene2/v3b`, `scene3/v3`, `exploded`, `cards_v3`, `captions/v3`. `intro_v3` holds only `prep.py` (F0005 failed: no ASR models on that clone), so there is no intro composition to review.

**Sources:** code, plus stills in results F0004/F0008/F0009/F0012/F0013 (F0014/F0015/F0017 had no previews yet).

## Must-fix before render

1. **App media committed to git (spec 0).** These files are frames of the real app recordings:
   - `film/scene2/v3b/assets/yash_slot.jpg`
   - `film/scene3/v3/snaps_accept/*` and `film/scene3/v3/snaps_accept2/*` (e.g. `frame-01-at-35.2s.png` shows the Logs screen with Vachana's SOS text)

   The root rule `film/*/assets/` does not match `film/scene2/v3b/assets/`, which is one level deeper, so the v3b assets are not ignored (the glass kit copy there is committed too).

   Fix:
   - `git rm --cached -r film/scene2/v3b/assets film/scene3/v3/snaps_accept film/scene3/v3/snaps_accept2`
   - add `film/scene2/v3b/.gitignore` containing `/assets/`
   - add `/snaps_*/` to `film/scene3/v3/.gitignore`

   v3b's build already re-creates `yash_slot.jpg` locally (`build.js:69`).
2. **Assembly inputs for s2a are wrong (my F0018 file, written before s2a landed).** As written, `assemble_v3.py` stops on a missing s2a, and in a draft it would slate it.
   - In `film/final/v3_segments.json`, s2a entry (lines 20-21), set:
     - `"video": "RENDERS:scene2/v3a/scene2_picture.mp4"`
     - `"stems": {"dx": "RENDERS:scene2/v3a/scene2_dialogue_sfx.wav", "sfx": null}`
     - `"tts_events": "RENDERS:scene2/v3a/audio_events.txt"`
     - `"expected_duration": 44.154`
     - `render_cmd`: `node film/scene2/v3a/build.js --render`
   - s2a's events file labels the playback `TTS`, not `app TTS`. In `film/final/assemble_v3.py:196` change `if "app TTS" in label` to `if re.search(r"\bTTS\b", label)`.

   I can do both as a 5-minute follow-up if you queue it; this task's `writes:` don't allow it.
3. **There is no intro.** F0005 could not run (faster-whisper and RNNoise models missing on that clone). The intro → s2a join is therefore unverified. Re-queue F0005 on a machine that has `local/models/`. When it is built, its last frame must be s2a's frame 0 exactly:
   - markup `<div id="card" class="glass-card full"><div class="cardTitle">How the app works</div></div>`
   - with s2a's local CSS (`film/scene2/v3a/index.html.tpl:7-8`: `rgba(13,20,29,.94)`, 88 px title), at scale 1, full frame

   If you take should-fix 3 below, both sides change together.

## Should-fix

1. **s2b → s3 card background.** Same text, size and position, but s2b ends warmer than s3 begins (960 px stills, top-left corner): s2b R35 G28 B36 vs s3 R32 G31 B37. `film/scene3/v3/index.html.tpl:13`: raise `.card-red` from `rgba(105,17,30,.16)` to about `.26`, then compare the two frames (s2b 32.367 s, s3 0.0 s) at full size until they match.
2. **s2a captions use their own style, not the kit's** (spec 0: one `.caption` style). `film/scene2/v3a/index.html.tpl:17` redefines `.caption` (43 px, `.56` box, fixed 1120 px width), while s2b and s3 use the kit's (38 px, `.35` strip). Delete the base `.caption{…}` rule and keep only the position variants `.caption.side` / `.caption.splitSide` (left, bottom, width). The stills show no collisions either way.
3. **The two full cards look different.** "How the app works" (s2a local CSS: `.94`, 88 px) vs "SOS: help from anyone nearby" (kit: `.86`, 64 px, in both s2b and s3). Pick one. Simplest: s2a uses the kit card and `h1`/`.card-title` at 64 px, or the kit adds a `.card-title.xl`. Tell the intro builder the same.
4. **s2b hard-codes the s2a end.** `film/scene2/v3b/build.js:68` uses its own `start_state.slot_time` (11.724). Today that equals s2a's last frame (`end_state.slot_time` 11.690) + 1/30, so the join is continuous: same 450×1000 phone at (735, 40), same `.phone` CSS, `#0a0d12`. It breaks if the TTS length or `YASH_REPLY` changes. Read `film/scene2/v3a/timeline.json` `end_state.slot_time + 1/30` instead, and fail if the geometry differs.
5. **s3 still builds scene music.** `film/scene3/v3/build.py:395-401` puts `sos_music.wav` into `scene3_music.wav` and mixes it into `scene3_mix.wav`, and from there into `scene3_v3.mp4`. The assembler only takes `scene3_dialogue_sfx.wav`, so the film is safe, but the playable scene file contradicts "music is one film-wide bed". Drop the `put(music, …)` line, or mux `scene3_dialogue_sfx.wav`.
6. **"Yash" pin label is not in spec section 3.** It appears in `film/scene2/v3a/index.html.tpl:26` (fallback) and `overhead/overhead.js` (`pin('yash','Yash',…)`); "Vachana" is only in section 3 as part of item 1. The existing sonar renders already label both names, so I suggest adding `Vachana` / `Yash` (map pins) to section 3 rather than removing them.
7. **Overhead uses held camera frames (lead's call).** By F0006's design, `walk_last.jpg` shrinks and tilts for about 0.8 s after the live walk ends. `yash_first.jpg` dissolves in and pushes from 1.16 to 1.0 over about 1 s before the cut to his live clip. That is close to section 0's banned "hold + slow push". If you want it strict, play `assets/yash.mp4` from source 0 under the dissolve (overhead t 4.02 → 5.0). Then start `yashFullVideo` at media-start 0.98, and shift the Yash speech offset `yAt` (`build.js`) and the 1.31 s caption offset by the same 0.98 s. Otherwise keep it as designed.

## Fine (checked)
- **On-screen text:** every string in s2a, s2b, s3 (tech lines are built in `build.py:78-82`), exploded and cards matches section 3 character for character, including the `·` (U+00B7) and `×` (U+00D7). `Sped up 26×` is right (156.65 s shown in 6 s). No number or claim changed.
- **Captions:** all match the speech actually heard.
  - Clean transcripts in T0003: Vachana's message and its TTS; "It's too hot here." (s2a plays only 1.48-3.02 s of Normalpart6, after "Oh"); Vachana's SOS line and its TTS; Vivek's reply.
  - s2b N2 "does" follows Vivek's recording (per F0009).
  - N1, N5 and N6 can only be checked against `RENDERS:narration/vivek/report.json`, which is not on this machine. Worth one look on vivek-pc.
  - Every caption sits inside its audio window. Tech lines (top) and captions (bottom) overlap in time only in s2b at 4.45-4.75 s, with no spatial collision. Side captions during app takeovers stay clear of the phone UI (stills `tts_takeover`, `09-sos-tts`, `10-vivek-reply`).
- **Hard rules:**
  - no `Math.random`/`Date.now`/absolute paths/URLs (only SVG namespace strings)
  - relays show no content (F0009's packet check)
  - SOS uses a local red pulse, not the relay chain
  - Vivek accepts with a real recorded tap, and the recording continues through it
  - s3's `sos_in` uses moving footage
  - placeholders are refused in production builds (s3, s2b)
  - camera windows end with an app takeover, not a hold
- **Sound:** no music inside s2a (its music stem stays silent), s2b (sonar music omitted), exploded or cards. Stems:
  - s2a `scene2_dialogue_sfx.wav`
  - s2b embedded (narration + sonar sfx; no separate stem, which the assembler handles)
  - s3 `scene3_dialogue_sfx.wav`
  - exploded `ticks.wav`
  - cards `cards_sfx.wav`
