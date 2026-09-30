# Scene 3 and title rule re-audit — S0006

**Verdict: 3 must-fix items.** This is a read-only audit of source, generated HTML, timeline, and assembly wiring, using the method of T0025. It is not a visual or listening review of a finished render. `brief/style.md` does not exist. The four external app recordings, scene 3 render/stems, and title render are absent on this machine, so their pixels, spoken content, Accept tap, and final sound cannot be verified here. T0025's relay-2 identification was resolved as a false alarm by `reviews/T0025.md` and is not repeated.

| Severity | File and line | Finding | Suggested fix |
|---|---|---|---|
| **must-fix before final export** | `film/scene3/main/index.html:12,17,19-21`; `film/scene3/main/build.py:153-170`; `film/scene3/sonar/sos_in/index.html:68`; `film/scene3/sonar/build.py:149-158` | All four app slots in the generated scene 3 page are visible `APP:` cards; `vachana_response` repeats during `end_hold`. `sos_in` also shows `APP: vachana_sos (last frame: searching)`. These are known draft scaffolds, but the current pages cannot be exported as the film. Without the real `vivek_sos` recording, explicit Accept/Decline, a deliberate Accept tap, and the absence of auto-accept or trusted-contact status cannot be verified. | Supply the four approved app recordings and the searching-state still; rebuild sonar and scene 3 pages; inspect the resulting page/render and confirm Accept is visibly tapped before the SOS opens. Reject any final page containing `APP:` or other setup text. |
| **must-fix** | `film/scene3/main/build.py:267-269,285-288`; `film/final/assemble.py:21,80,225-227` | Scene 3 writes a separate `scene3_music.wav`, but also sums that music into `scene3_mix.wav` and embeds the mix in `scene3_draft.mp4`. The approved rule says SOS music is never baked into a video. Final assembly currently replaces this video's audio with separate stems, so it should not double the music in the assembled film; the scene render itself still violates the rule. | Mux `scene3_draft.mp4` with dialogue/SFX only (or leave it silent) and keep the music in `scene3_music.wav`. Verify the music-only and no-music final exports. |
| **must-fix** | `film/scene3/main/build.py:225-226,233-239,267-269`; `film/scene3/main/timeline.json:67-70` | N5 and N6 have the correct fixed starts (0.3 s and 21.1 s), but both are added directly to `scene3_dialogue_sfx.wav`; no separate narration track/stem is produced. The approved cut calls for narration on its own track. | Write N5/N6 to a separate narration stem at those exact starts, then combine it only at final mix/assembly while retaining the independent stem. |
| **should-fix** | `film/title/build.py:4,7-10`; `film/title/index.html:30` | The title has the correct default `~400 m`, but `DISTANCE` is a hard-coded constant rather than a build parameter. The lead cannot set the value from the final map distance without editing source, and the external map screen is unavailable here for comparison. | Add a validated command-line or configuration parameter with `~400 m` as default; compare it with the final map recording and rebuild the title if needed. |
| **note** | `film/scene3/sonar/shared/sonar.css:3,15-36`; `film/scene3/sonar/shared/sos.html.tpl:58-64`; `film/scene3/sonar/shared/sos.js:10-20,35-70` | The copied stylesheet still defines blue relay/packet classes, but the SOS pages instantiate only Vachana and Vivek points and the SOS code draws red circular waves from one source. The blue relay selectors have no matching scene 3 elements. | No film-rule change is needed; remove unused copied selectors during cleanup if desired. |

## Rule checks with no source-level violation found

- **One-source SOS:** `film/scene3/sonar/shared/sos.js:20-29,35-70` projects all circles from Vachana and reveals only Vivek's point at the arrival. `film/scene3/sonar/shared/sos.html.tpl:58-64` has no relay nodes or packet element. The campus uses cold blue tones (`shared/sonar.js:126-132`), as approved, while its old pulse ring is suppressed by `ringFade: 0` (`shared/sos.js:35-37`).
- **Red:** Scene 3's red literals are assigned to SOS waves, Vivek's arrival point, searching transition, and phone glow (`film/scene3/sonar/shared/sos.html.tpl:14-30,41-53`). The title uses a dark background and teal brand accent (`film/title/index.html:12-23`), with no red accent.
- **Music placement:** `film/scene3/main/build.py:258-268` positions a 12.5 s bed at `sos_in` (18.1–30.6 s), ending before `lab_a`; `film/scene3/sonar/cues.py:58-61` and `sound.py:212-219` duck it under N6. `film/final/assemble.py:19-22,76-92` assigns scene 3 music as a separate assembly input; scene 1 and title have none. The embedded scene 3 mix is the exception identified above.
- **Camera grade and app screens:** `film/scene3/main/build.py:69-79,132-174` grades camera plates and copies app recordings into the page without a grade filter. `film/scene3/sonar/build.py:91-119` grades the camera sides and dive plate, while the app still gets only a crop, scale, and frame rate conversion. This verifies the source path, not the unavailable recordings.
- **Narration timing:** `film/scene3/main/build.py:53-66,229-239,275-277` sets N5 at 0.3 s and N6 one second into `sos_sonar`; generated `film/scene3/main/timeline.json:67-70` confirms 0.3 s and 21.1 s. Their separation is the issue above.
- **Title:** `film/title/index.html:28-33` matches all six approved lines exactly, including “10 languages,” `~400 m`, and “Team ID 148903.” Each of the five main statements fades in separately, with the team line small at the bottom (`index.html:15-23,39-50`). `film/title/make_sfx.py:9-22,26-44` generates only quiet local ticks; no title music or whoosh source is specified.
- **Local resources and disallowed labels:** The scene 3 and title HTML load local JS, CSS, media, and `local()` fonts (`film/scene3/main/index.html:1-3`, `film/scene3/sonar/shared/sos.html.tpl:7-12`, `film/title/index.html:7-9,35`). No composition fetches a CDN. The SVG namespace string in `shared/sos.js:8` is an identifier, not a network request. Sonar `hyperframes.json` files contain remote schema/registry metadata (`film/scene3/sonar/build.py:132-136`), but those are not HTML loads. No visible “demo”, debug, mock, simulation, or verification-code label occurs in the checked pages; the visible `APP:` placeholders are listed above.

## On-screen text inventory

This lists text rendered by the generated pages. Camera footage and external app recordings can contain additional text that this source audit cannot inspect. The source template or builder location is included for each generated string.

| Page / source line | Visible text |
|---|---|
| `film/scene3/main/index.html:12`; builder `build.py:170` | `APP: vachana_sos` |
| `film/scene3/main/index.html:17`; builder `build.py:170` | `APP: vivek_sos` |
| `film/scene3/main/index.html:19`; builder `build.py:170` | `APP: vivek_reply` |
| `film/scene3/main/index.html:20-21`; builder `build.py:170` | `APP: vachana_response` (slot and end hold) |
| `film/scene3/sonar/sos_in/index.html:63-64,68`; template `shared/sos.html.tpl:63-64`, builder `build.py:158` | `Vachana`; `Vivek`; `APP: vachana_sos`; `(last frame: searching)` |
| `film/scene3/sonar/sos_sonar/index.html:63-64`; template `shared/sos.html.tpl:63-64` | `Vachana`; `Vivek` |
| `film/scene3/sonar/sos_dive/index.html:63-64`; template `shared/sos.html.tpl:63-64` | `Vachana`; `Vivek` |
| `film/title/index.html:28`; template `index.html.tpl:28` | We built iTantra so you can reach people over long distances, even with no cell network. |
| `film/title/index.html:29`; template `index.html.tpl:29` | Speak in any of 10 languages, and your message is read aloud on the other side. |
| `film/title/index.html:30`; template `index.html.tpl:30`, `build.py:4,10` | It travels phone to phone, through the people around you, across ~400 m of campus. |
| `film/title/index.html:31`; template `index.html.tpl:31` | No towers. No internet. No new hardware. Just the phones people already carry. |
| `film/title/index.html:32`; template `index.html.tpl:32` | iTantra. Speak. Send. Be heard. |
| `film/title/index.html:33`; template `index.html.tpl:33` | Team chmod 777 · Team ID 148903 · NIE Mysuru |

The fallback `SOS · <segment>` card exists in `film/scene3/main/build.py:181`, but the current generated page uses sonar videos at `index.html:13-15`, so that fallback text is not currently on screen.
