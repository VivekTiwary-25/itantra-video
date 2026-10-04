# Film v3: spec (claude-lead, 4 Oct 2026). Target: rough full draft today, then polish.

Goal: `RENDERS:full_film_v3.mp4`, ~3:10 (max 4:30), 1920x1080, 30 fps, dialogue + sound + music mixed. Reference cut: `RENDERS:full_film_v1.mp4`. Base code: `film/scene2/v2/`, `film/scene3/v2/` (they now include the 30 Sep helper fixes, merged to main) and the must-fixes in `discussion/v2/002` and `004`.

## 0. Film rules (every task)
- Live camera video NEVER freezes or holds a frame (no more "hold last frame + slow push"). When a camera clip runs out, the app side takes over (camera panel slides out, the phone moves to the centre on the dark field) or we cut.
- Relays never show content. SOS never travels the relay chain. Vivek is never a trusted contact and never auto-accepts. No verification codes, debug screens, "demo/mock" labels, invented UI, invented numbers or claims. Narration and dialogue are never cut mid-word (Rule B windows from v2 still apply). Never speed up app screens or speech.
- Blue = Normal, red = SOS. Bluetooth is never crossed out.
- Captions under ALL speech (Vachana, Yash, Vivek, narration, the app's TTS): one style (`.caption` from the glass kit), bottom centre, never over phone UI or tech lines. Caption data: `film/captions/v3/<segment>.json` = list of {start, end, text} in segment seconds; compositions render them from that file.
- On-screen text: use EXACTLY the strings in section 3. Any new text goes to the lead first.
- No URLs, no Math.random/Date.now, no footage/deck/app media in git, no absolute paths, no file > 20 MB in git.

## 1. Glass kit (contract; built by F0003 in `film/common/glass/`)
One frosted-glass look for every card and panel (replaces the old blotchy blurred-video cards). Compositions copy `film/common/glass/` into their own `assets/glass/` at build time and link `assets/glass/glass.css` (+ `glass.js`). Until the kit exists, use these class names anyway with a minimal local fallback; the real kit drops in later.
- `.glass-card`: big title card. `.glass-card.full` = full-frame sheet, near-opaque (backdrop barely visible), so cuts between compositions under a full card are invisible.
- `.glass-panel`: smaller panel for text beside a person (dark frosted, readable over bright daylight footage).
- `.glass-circle`: white matte glass circle (light frosted, dark content on it).
- `.techline`: short tech line, top centre, small frosted pill, one at a time.
- `.caption`: caption text, bottom centre.
- `.label-pin`: map/sonar pin label.
- Tokens in `:root`: `--glass-tint`, `--glass-blur`, `--glass-border`, `--glass-shadow`, `--text`, `--text-dim`, `--blue` (Normal), `--red` (SOS), `--gold` (Bluetooth glow); font `SceneSans` (local Segoe UI Variable, as in scene 1).
- `glass.js`: `Glass.phone(el, {src, kind:'img'|'video'})` draws an Android phone mockup (thin dark bezel, punch-hole camera, 1080x2400 screen ratio) around a screen image/video; `Glass.icon(name)` returns inline SVG for `tower`, `mobile-data`, `wifi`, `internet`, `bluetooth`, `lock`, `mic`, `speaker`, `phone`; `Glass.cross(el, progress)` draws an animated strike line over an icon (progress 0..1, deterministic).

## 2. Segments, order, owners
Each segment is its own HyperFrames composition, rendered separately, joined by `film/final/assemble.py`.

| # | Segment | Folder | Length | Joins |
|---|---|---|---|---|
| 1 | intro | `film/intro_v3/` | ~25 s | ends on the full "How the app works" card (`.glass-card.full`) |
| 2 | s2a | `film/scene2/v3a/` | ~50 s | starts on that same full card; ends on Yash's phone centred (app takeover) right after the TTS |
| 3 | s2b | `film/scene2/v3b/` | ~35 s | starts on the same centred phone at the same slot time; ends on the full card "SOS: help from anyone nearby" over red frosted sonar |
| 4 | s3 | `film/scene3/v3/` | ~45 s | starts on that same full SOS card; ends right after Vivek's response is sent |
| 5 | exploded | `film/exploded/` | 15-18 s | |
| 6 | cards | `film/cards_v3/` | works-now ~8 s + closing ~6 s | |

Joins between compositions happen on identical frames (the same full card, or the same centred phone at the same slot time).

### intro
Vachana's short take, South Campus, 2 Oct. Script: "I'm Vachana from team chmod 777. For ISRO's problem SIH26173, we built iTantra. Speak, and your message travels phone to phone, no network needed. Let's see it work."
Open directly on her take (no campus, plant, airplane-mode or push-to-talk shots). Keep her uncovered on the left (shift/crop the frame if needed). Right side, all on glass, word-timed to her clean voice:
- name/team/PS line: `.glass-panel` with text 3.1.
- "Speak,": a waveform driven by her real voice (RMS envelope of the clean audio, precomputed to JSON at 30 fps).
- "and your message": the waveform settles onto a baseline; her words type out along it, word-timed.
- "travels phone to phone,": the text tightens into a compact message card that arcs into an Android phone mockup showing the real iTantra home screen (private input); a "New notification" banner drops down.
- "no network needed.": the phone floats onto a `.glass-circle`; tower, mobile data, Wi-Fi and internet icons get crossed out one by one (labels 3.3); Bluetooth stays, with a soft gold glow.
- On "Let's see it work" (or right after her last line if she doesn't say it) the circle grows to fill the frame and becomes the full "How the app works" card. The intro ends there.

### s2a (from v2 scene 2: doorway to Yash's TTS)
The card shrinks away to reveal her on the bench, then the split-screen send as in v2. No freeze: on Send the message card lifts off her app screen and flies out right; the sped-up walk enters moving the same way (label 3.5, real factor); N1 over the walk. At the walk's end the camera pulls up into a LANDSCAPE overhead of the campus (replaces the portrait map card) with pins "Vachana" and "Yash" and text 3.6, then zooms into Yash's pin onto his real shot. Notification, split screen `yash_app`; when the camera clip runs out, app takeover; the TTS plays (captioned); the segment ends on the centred phone. Yash's reply (PTT, his line, Send) sits behind a flag `YASH_REPLY` (default false = cut; the lead may switch it on).

### s2b
Push into Yash's phone; the screen goes dark and becomes the sonar view (existing renders `sonar_a`, `relay_1..3`, `sonar_b`, with N2, N3); the packet travels Vachana, relays, Yash. Tech lines at the top (3.7, 3.8, 3.9, one at a time, while the matching thing is on screen). Last ~1.5 s: the sonar tints red and frosts over into the full card 3.10.

### s3 (from v2 scene 3)
The full SOS card shrinks to reveal sospart1; Vachana's hands-free SOS (split, no frozen camera); `sos_in`, `sos_sonar` (N6), `sos_dive` with tech lines 3.11, 3.12, 3.13 during the SOS pulse; Vivek (ChatGPT gag, notification, Accept clearly visible and unhurried, TTS, his reply, Send). END right after his Send. `vachana_response` and `end_hold` are cut.

### exploded (15-18 s; Three.js in HyperFrames, sonar look; preview stills to the lead first)
The phone turns to three-quarter view and separates top to bottom into glass layers; a locked packet drops through and lights each layer as it is named; each label (3.14-3.19) appears with one soft glass tick (one sound family, under the music). Then it snaps back together.

### cards
Works now / Coming next (~8 s, 3.20 and 3.21; big and readable; "Coming next" clearly marked as next). Closing (~6 s, 3.22, no names).

## 3. On-screen text (final, humanised; do not change)
1. `Vachana` / `Team chmod 777` / `Problem statement SIH26173`
2. `New notification`
3. `Tower` / `Mobile data` / `Wi-Fi` / `Internet` / `Bluetooth LE`
4. `How the app works`
5. `Sped up N×` (N = the real speed factor, rounded to a whole number)
6. `~300 m, walking distance`
7. `Speech becomes text on the phone`
8. `Encrypted: relays can't read it`
9. `Hops phone to phone over Bluetooth LE`, with a second smaller line `6 hops shown on real phones`
10. `SOS: help from anyone nearby`
11. `No saved contact needed`
12. `Reaches the 3 strongest phones nearby first, then widens the search`
13. `The helper must accept`
14. `Screen and mic` / `Hold to talk`
15. `Speech to text on the phone, without internet` / `IndicConformer (9 Indian languages) · Whisper (English)`
16. `Encryption: only your contact can open it` / `Google Tink`
17. `Bluetooth radio: hops phone to phone, encrypted at every hop` / `Bluetooth LE · Noise XX`
18. `Speaker: reads it aloud` / `Piper · Meta MMS`
19. `Base: stock Android` / `No new hardware`
20. `WORKS NOW`: `Speech to text on the phone, English + 9 Indian languages` / `Encrypted: relays can't read it` / `6 hops over Bluetooth LE, shown on real phones` / `SOS to anyone nearby, no saved contact needed`
21. `COMING NEXT`: `Field trials with more phones` / `SOS chat after a helper accepts`
22. `iTantra` / `Speak. Send. Be heard.` / `Team chmod 777 · Team ID 148903` / `SIH26173 · NIE Mysuru`

## 4. Sound and music
One restrained music bed across the film: quiet under dialogue, ducked under TTS and speech, a little more tension in SOS, rises into the cards, resolves on the closing card. Procedural/offline only. A glass-tick family for the exploded view. Existing cues from T0035 (`RENDERS:sound/`). Final loudness -16 LUFS, true peak <= -1.5 dBTP.

## 5. Rendering
Renders run on utkarsh-pc first (RTX 4050), then yash-pc, then vivek-pc; never on yojitth-pc. The lead starts final renders over SSH. Worker tasks build, run `hyperframes.cmd check`, and make preview stills or short 540p previews only. Each composition folder has a `render.cmd`/`build` step that works from any clone given `machine.local.json` (footage_root, renders_dir), so the lead can run it over SSH on any render machine.
