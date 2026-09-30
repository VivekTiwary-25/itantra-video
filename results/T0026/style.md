# iTantra film style — draft from built scenes

**Status:** review draft for `brief/style.md`, 30 September 2026. These are the values in the built 1920×1080, 30 fps scenes, with recommendations where the files differ. Apply numeric values at 1080p. A recommendation is not a claim that the existing render already uses it. Sources are repository-relative so this file can be committed safely.

## Colour and light

| Role | Value and use | Source |
|---|---|---|
| Main text | `#F3F5F8` on dark plates/panels. | `film/scene1/index.html.tpl` `--ink`; `film/scene2/sonar/shared/sonar.css` `--ink` |
| Secondary / muted text | `#C1C8D2` for panel sublines; `#6F7886` for faint arrows. | `film/scene1/index.html.tpl` `--ink-2`, `--ink-3` |
| Glass backing and edge | `rgba(9,12,17,.86)` with `1px solid rgba(255,255,255,.11)`. Opaque icon boxes are `#17262A`, edge `#2F5A55`. | `film/scene1/index.html.tpl` `--panel`, `--line`, `--box`, `--box-edge` |
| Soft teal | `#8FE3D4` for explanation eyebrows, panel icons and small packet. It is distinct from the relay route. | `film/scene1/index.html.tpl` `--accent`, `#packet`, `.step .dot` |
| Relay blue | `#2EA8FF` for active relay points, route and sealed packet; pale trail `#BFE6FF`. Do not use for SOS. | `film/scene2/sonar/shared/sonar.css` `--relay`, `.ov-trail`; `film/scene2/sonar/cues.py` `COLOURS` |
| SOS red | `#E65A63` ring, `#D62F40` glow, `#A52936` faint wake. Red is confined to the SOS wave, Vivek's reached point and phone glow. | `film/scene3/sonar/shared/sos.html.tpl` CSS variables; `film/scene3/sonar/cues.py` `COLOURS`; `discussion/scene3/001-claude-lead.md` “Rules for scene 3” |
| Sonar campus | Near-black ground; cold points `#B4D6F4`, hot returns `#F2F9FF`, ground grain `#7AA2C6`, scan ring `#7FB4DE`; people `#EAF4FF` and names `#E8F0F8`. The shader's normal floor is `.34`; SOS uses `.6` with the cold scan ring hidden. | `film/scene2/sonar/shared/sonar.js` uniforms and `render`; `film/scene2/sonar/shared/sonar.css`; `film/scene3/sonar/shared/sos.js` `sonar.render` |
| Black / overlays | Scene 1 uses black around the video and `#05070A` for dim, reaching `.93` during the doorway. Scene 2's base is `#05070A`; its doorway uses `rgba(5,7,10,.97)` and frosted matte `rgba(10,13,18,.72)`. Its end fade reaches `.91` over the base. | `film/scene1/index.html.tpl` `#dim`, doorway timeline; `film/scene2/main/index.html.tpl` `#root`, `#door`, `.matte`, `#fade`, `render` |
| Phone surround | Camera sides: `blur(40px) brightness(.55)`; doorway picture: `blur(40px) brightness(.42)`. Keep the live footage visible as context, with the centre phone readable. | `film/scene2/main/index.html.tpl` `.sides`, `#door .picture`; `queue/codex-vivek/T0007.md` shared rules |

Blue relay marks and the colder, desaturated sonar environment have different jobs; they should not be collapsed to a single blue. Likewise, the `.86` floating glass, `.72` doorway matte and `.97` solid phone doorway serve different depths rather than being alternate values for one panel.

## Type

Use locally installed faces only. The reusable face declaration is `@font-face { font-family: 'SceneSans'; src: local('Segoe UI Variable Display'), local('Segoe UI Variable'), local('Segoe UI'); font-weight: 100 900; }`; body falls back to `sans-serif`. Scene 1 also uses `SceneMono` from `local('Consolas')` for the team name only. Keep `./gsap.min.js` and other scripts local. Sources: `film/scene1/index.html.tpl`, `film/scene2/sonar/shared/sonar.css`, `film/scene3/sonar/shared/sonar.css`.

| Role | Built specification at 1080p | Source |
|---|---|---|
| Eyebrow | 24px / 600, uppercase, `.16em` spacing, teal. The top multi-column panel's small keys are 24px / 700, `.14em`. | `film/scene1/index.html.tpl` `.eyebrow`, `.col .k` |
| Headline | Explanation headline 50px / 650, line-height `1.08`, spacing `-.01em`. Scene 2 doorway title is 64px / 600, spacing `-.015em`. | `film/scene1/index.html.tpl` `.big`; `film/scene2/main/index.html.tpl` `#door .title` |
| Panel body / step | Top values 42px / 600, line-height `1.12`; top problem identifier 50px / 650; adjacent values 36px / 550. Explanation step lead 36px / 650, line-height `1.1`; supporting line 28px / 500. | `film/scene1/index.html.tpl` `.col .v`, `#ps`, `.step .t1`, `.step .t2` |
| Small label | Panel subline 28px / 500; icon labels 26px / 600; sonar person names 28px / 600, `.02em` spacing and dark text shadow. Small `TEXT` pill is 22px / 700, `.06em`. | `film/scene1/index.html.tpl` `.col .sub`, `.ic .lab`, `#pill`; `film/scene2/sonar/shared/sonar.css` `.ov-lab` |
| Relay callout | 32px, line-height `1.3`; lead line 600 with `.005em`, second line 450 in `#DCE4EC`. | `film/scene2/sonar/shared/relay.html.tpl` `#txt` |
| Team name | `Consolas` via `SceneMono`, 42px / 700, `-.01em` (inherits the top value size). | `film/scene1/index.html.tpl` `.col .v`, `.col .v.mono` |
| Title card | **Not built yet.** The approved plan specifies clean type on dark, one sentence fading in at a time with calm pauses, and a small team line at bottom. No size, weight or spacing is fixed in code. Before building, propose 50px / 650 for statements (the scene 1 headline) and 24px / 600 for the team line (the existing eyebrow scale), then review the actual card. | `discussion/scene3/001-claude-lead.md` “Title card”; reference sizes: `film/scene1/index.html.tpl` |
| Spoken captions | **No established rendered caption token.** The brief requests one restrained style that avoids phone UI and graphics. Set size and safe position against real frames during the finish pass; do not infer a caption size from the 26–28px graphics labels. | `brief/film-brief.md` item 57; `brief/decisions.md` batch 5 |

## Panels and phone inserts

For a new **floating explanation panel**, copy the scene 1 `.glass` treatment: `background: rgba(9,12,17,.86)`, `border: 1px solid rgba(255,255,255,.11)`, `border-radius: 30px`, `box-shadow: 0 40px 90px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.08)`, `backdrop-filter: blur(20px) saturate(115%)`, and a top wash from `rgba(255,255,255,.06)` to transparent over 120px. Its content is clipped within the rounded shape. Put the 24px teal eyebrow above a 50px headline and use 28px secondary text. Source: `film/scene1/index.html.tpl` `.glass`, `.glass::before`, `.eyebrow`, `.big`, `.step .t2`.

For a **full-height app recording**, the established scene 2 frame is 486×1080 at `left: 717px`, radius 28px, `#0A0E14` backing, with blurred/dark side imagery. The screen recording itself uses `object-fit: contain`; it receives no grade. The doorway is a different shape: 452×940 at `(734,70)`, radius 64px, border `rgba(255,255,255,.24)` and fill `rgba(5,7,10,.97)`. Sources: `film/scene2/main/index.html.tpl` `.screen`, `#door`; `queue/codex-vivek/T0007.md` doorway and app layout.

## Motion and timing

Keep reveals tied to words. Scene 1 cue times are in `film/scene1/cues.json`; `film/scene1/index.html.tpl` says the step cue lands about **0.12 s before** the spoken word and sets `IN = 0.3` s. Standard step motion is 10px vertical or 14px horizontal travel with `power2.out`; larger glass entrances take 0.6–0.7 s with 10px blur clearing and `power2.out`. Card exits take 0.35–0.4 s with `power1.in`. The top panel floats ±5px over 3 s, and the side panel ±7px over 3 s, both `sine.inOut` yoyo; side panel yaw slowly shifts from −5° to −2° over 16 s. Source: `film/scene1/index.html.tpl` timeline.

The scene 1 **doorway morph** starts at cue `door = 53.166` s and takes 1.6 s with `power3.inOut`, ending at the 452×940 phone shape. Background dim rises to `.93` over 1.5 s and footage grows to `1.07` over 1.7 s. Scene 2 resumes that shape: expand at 0.2–1.4 s with `power3.inOut`, then shrink/fade at 2.6–3.4 s. The title appears at 1.0 s; the bench-to-app dissolve is 0.5 s. Sources: `film/scene1/cues.json`, `film/scene1/index.html.tpl`, `film/scene2/main/index.html.tpl`, `film/scene2/main/timeline.json`.

The scene 2 bench push begins at 5.4 s and runs 2.3 s, with `power3.inOut`, tracked toward the hands/phone. It is a functional move into the UI, unlike the gentle relay punch-ins. Each relay clip freezes at 2.0 s, pushes from `1` to `1.075` from 2.0–6.0 s (about **8%**) with `sine.inOut`, draws its callout slant at 2.45–2.80 s and flat at 2.80–3.00 s (`power2.inOut`, then `power2.out`), ticks at 3.00 s, and fades the 32px callout in at 3.00–3.35 s. It is fully held to 5.15 s, then leaves by 5.40 s. Sources: `film/scene2/main/index.html.tpl` `render`; `film/scene2/sonar/cues.py` `RELAY_SHAPE`; `film/scene2/sonar/shared/relay.html.tpl` timeline.

Sonar uses slow camera drift and waves rather than fast cuts. The scene 2 reveal fades in over 1.4 s; relay dives take 0.8 s. SOS `sos_in` takes 2.0 s, the campus view 9.0 s, and the dive 1.5 s; the red wave reaches Vivek at 8.0 s of `sos_sonar`. SOS phone shrink is 0.75–1.20 s; the last dive fades to the lab over 0.62–1.0 s and ends with a 0.3 s soft red phone glow. Sources: `film/scene2/sonar/cues.py`, `film/scene3/sonar/cues.py`, `film/scene3/sonar/shared/sos.html.tpl`.

## Sound and picture finishing

- Use the separately recorded clean dialogue where available and sync it to the camera takes. The scene 1 voice chain (RNNoise, FFT noise reduction, gate, EQ, de-esser and compressor) is in `film/scene1/build.py` `CHAIN`; scene 2 reuses it in `film/scene2/main/build.py`. Target dialogue and narration about **−16 LUFS integrated**, and the final encoded mix **−16 LUFS ±0.2, true peak at or below −1.5 dBTP**. Measure the encoded output, as the scene 2 finalizer does. Sources: `film/scene1/build.py`, `film/scene2/main/build.py`, `queue/codex-vivek/T0007.md`.
- Keep music **separate from video and SFX**. The scene 2 `sonar_music.wav` covers only `sonar_a` through `sonar_b` (31 s), with a music/no-music mix. The scene 3 `sos_music.wav` covers only `sos_in` through `sos_dive` (12.5 s), then settles before the lab. Both music generators target about **−22 LUFS for the bed**. Duck for narration: scene 2's generated bed uses about 7 dB reduction in narration zones and its assembly adds a small edge duck; scene 3 uses 9 dB reduction under N6. Keep the effects soft: interface blips, sonar pings and controlled SOS pulse, with no trailer booms or whooshes on the title card. Sources: `film/scene2/sonar/sound.py`, `film/scene2/main/build.py`, `film/scene3/sonar/sound.py`, `discussion/scene3/001-claude-lead.md`.
- Apply the approved **`GRADE_V1` to camera clips only**, after checking and properly converting HDR if needed; never grade app screen recordings. The exact ffmpeg filter string is in `film/scene1/grades.sh`: `curves=master='0/0.02 0.12/0.10 0.5/0.5 0.82/0.84 0.94/0.92 1/0.955',colorbalance=rs=-0.02:bs=0.035:rm=0.025:bm=-0.02:rh=0.01:bh=-0.01,eq=saturation=0.9,vignette=a=PI/7`. It gives mild contrast, cool shadows, slightly warm mids, 10% less saturation and a soft vignette. Sources: `film/scene1/grades.sh`, `brief/decisions.md`, `queue/codex-vivek/T0007.md`, `discussion/scene3/001-claude-lead.md`.

## Never do

- Never show private-message content on a relay phone. The private route may show a compact sealed packet; the relays remain people carrying it without reading it. Sources: `brief/decisions.md`, `discussion/scene2-sonar/001-claude-lead.md`.
- Never depict SOS using the private relay chain, packet or blue relay hops. Show red waves from Vachana to a nearby responder. Sources: `brief/decisions.md`, `discussion/scene3/001-claude-lead.md`, `film/scene3/sonar/shared/sos.js`.
- Never make Vivek a trusted contact or auto-accept an SOS. Show **Accept / Decline** and an explicit Accept. Never stage Yash or Vivek waiting inside iTantra; a notification interrupts ordinary phone use. Sources: `brief/decisions.md`, `brief/three-app-builds.md`, `discussion/scene3/001-claude-lead.md`.
- Never show six-digit verification, authentication exposition, debug/setup screens, or visible “demo”, “mock”, “simulation” labels in shipped pictures. Temporary slot placeholders must be replaced before release. Sources: `brief/film-brief.md`, `brief/decisions.md`, `queue/codex-vivek/T0007.md`.
- Do not add new capability or networking claims in a recap. The later approved scene 3 handover replaces the older brief's proposed montage with a direct title card after the response. Keep the title calm, sentence-by-sentence, with no dramatic whooshes. Sources: `brief/film-brief.md` items 46–50 and 61; `discussion/scene3/001-claude-lead.md` “Title card” and “Final assembly”.
- Do not fetch fonts, scripts, images or audio from URLs. Use local fonts, vendored scripts and procedural audio. Sources: `AGENTS.md`, `discussion/scene3/001-claude-lead.md`.

## Differences and decisions for the lead

| Issue in built files | Suggested single rule for new work | Evidence |
|---|---|---|
| Scene 2 main declares only `local('Segoe UI Variable')` and uses a different face alias/fallback from scene 1 and both sonar scenes. | Use the `SceneSans` three-step `local()` declaration above everywhere new; preserve the established sizes. | `film/scene2/main/index.html.tpl` vs `film/scene1/index.html.tpl`, `film/scene2/sonar/shared/sonar.css`, `film/scene3/sonar/shared/sonar.css` |
| The 28px app insert radius agrees, but scene 2 uses `0 12px 58px #000c` / `#ffffff22` outline while SOS uses `0 30px 80px rgba(0,0,0,.55)` / `rgba(255,255,255,.06)`. | For future phone inserts use the scene 2 main shadow and outline, matching the longer existing app section; keep radius 28px. | `film/scene2/main/index.html.tpl` `.screen`; `film/scene3/sonar/shared/sos.html.tpl` `#phone` |
| Scene 1's supporting text is `#C1C8D2`; relay callout's second line is brighter `#DCE4EC`. | Use `#C1C8D2` on backed panels and `#DCE4EC` over live footage, where the stronger contrast is useful. These are context-specific roles, not interchangeable values. | `film/scene1/index.html.tpl` `--ink-2`; `film/scene2/sonar/shared/relay.html.tpl` `#txt .l2` |
| Slot placeholder type is 28px in scene 2 and 26px in SOS. These temporary cards are not for release. | Do not carry either size into final UI; replace both with real app material. | `film/scene2/main/index.html.tpl` `.placeholder`; `film/scene3/sonar/shared/sos.html.tpl` `#phone .placeholder` |
| The title card and spoken captions have no built size/weight standard yet. | Use the proposed title sizes above only as a first frame to review; decide caption styling against the finished phone and sonar frames. | `discussion/scene3/001-claude-lead.md`; no title composition under `film/scene3/`; `brief/film-brief.md` item 57 |

