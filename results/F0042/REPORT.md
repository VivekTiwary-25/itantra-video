---
status: done
---

## Made

- Rebuilt scene 2b with N2, five map explanation beats, the three relay clips with N2f, sonar_b with N3, and a neutral full glass SOS card. Each N2a–N2e beat reads its duration from `film/common/narration_v4.json` and lasts that duration plus 0.4 s. The current placeholder timeline is 51.9 s.
- Drew the explanation inside the sonar map at the established pin positions: Vachana's exact message, a sealed capsule and ~1.2 KB readout, encrypted Bluetooth route, wait clock and moving dot, and the 1–6 hop counter. The repeated map pulse fades to zero at its loop boundary.
- Corrected the relay labels in this composition to Trisha (relay 1), Utkarsh (relay 2), and Vaishnavi (relay 3). The existing relay renders have no baked name label to cover.
- Wrote the neutral SOS markup into `film/scene2/v3b/timeline.json` `end_state.card_html`. The card uses red only on the word “SOS.”
- Built 12 full-size 1920 px stills, 12 matching 480 px stills, and `results/F0042/preview/sheet-480.jpg`. No full-length render was made.

## Preview review

- `00-push` — hero: full centered Yash phone and complete message; reads at 480 px: yes; judge “oh”: the phone-to-sonar entry is clear.
- `01-opening` — hero: revealed campus and Vachana/Yash pins; reads at 480 px: pin names are small but legible; judge “oh”: the map reveal has scale.
- `02-N2a` — hero: her exact message grows from Vachana's pin; reads at 480 px: yes; judge “oh”: the speech-to-text link is immediate.
- `03-N2b` — hero: locked blue capsule, Google Tink and ~1.2 KB; reads at 480 px: yes; judge “oh”: the sealed packet is clear.
- `04-N2c` — hero: dotted blue route and closed locks at relay dots; reads at 480 px: yes; judge “oh”: the hop path is visible without showing content.
- `05-N2d` — hero: capsule on a relay pin with clock ring and moving dot; reads at 480 px: yes; judge “oh”: wait-and-carry action is clear.
- `06-N2e` — hero: hop counter at 6 beside the route; reads at 480 px: yes; judge “oh”: the tested six-hop claim lands.
- `07-relay1` — hero: moving relay shot with Trisha pill; reads at 480 px: yes; judge “oh”: the map becomes a real person.
- `08-relay2` — hero: Utkarsh relay shot; reads at 480 px: yes; judge “oh”: the second relay confirms the chain.
- `09-relay3` — hero: Vaishnavi relay shot; reads at 480 px: yes; judge “oh”: the third real relay completes the sequence.
- `10-arrival` — hero: blue arrival at Yash's pin; reads at 480 px: pin names are legible; judge “oh”: the route resolves.
- `11-sos` — hero: neutral full glass SOS card with a small red title accent; reads at 480 px: yes; judge “oh”: clean mode change.

## Checks and handoff notes

- `node film/scene2/v3b/build.js --preview` passed `hyperframes.cmd check` and produced the stills above. The build stages silent previews for N2–N3 because all eight v4 narration takes are still placeholders. When the real files and transcripts arrive, rebuilding updates beat lengths, audio and captions from the narration JSON.
- Scene 3 still has the older red card in its own files. Its next task must use this scene's `end_state.card_html` for frame 0; scene 3 was outside F0042's write paths.
- `film/final/v3_segments.json` still records the former 32.4 s scene length and needs refreshing during final assembly; that file was outside F0042's write paths.
