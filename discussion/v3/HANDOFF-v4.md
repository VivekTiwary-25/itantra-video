# Film v4 handoff (claude-lead, 4 Oct ~17:45 IST)

For whoever leads while claude-lead is out of usage (until its weekly reset at 19:30 IST). claude-lead takes back over at 19:30 and reads `discussion/v3/` + `results/` for what happened. Specs: `discussion/v3/001-claude-lead.md` (base), `005-claude-lead.md` (Vivek's v4 notes; wins where they differ).

## Who leads
- 1st: claude-lead. 2nd: **codex-vivek** (task F0055, conditional). **claude-second must NOT be used as lead and gets no new tasks: Vivek said don't exhaust Yojith's session at any cost.**
- Never use Yojith's Codex. Never render on Yojith's laptop. Never GPT-6 Astra.

## Vivek's rules (all briefs)
- QUIET MODE: no progress pings. Ping Vivek (ntfy, one short line, no paths) ONLY if (a) something is broken and two fix attempts failed, or (b) everything is done and only his narration recordings are missing, or (c) all three leads are unavailable.
- Decide design/taste within the brief; never wait for approval. Look at stills at full size and at 480 px wide before accepting; ask "would a judge go oh?".
- Live camera video never freezes or holds. App recordings are never zoomed/cropped/sped up. Narration and dialogue are never cut mid-word or time-stretched.
- Relays never show content; SOS never travels the relay chain; Vivek never auto-accepts; no invented numbers/claims; on-screen text only from spec 001 section 3 and 005 section T. Blue = Normal, red = SOS accent, gold only on Bluetooth.
- No footage, deck files, app media, home.png or model files in git; no absolute paths; no files > 20 MB.
- Failed task: two tries, then skip and note it.

## Done (accepted)
- Intro v4: F0046 + polish F0053 (long take, one cut, fixed morphing panel, badge ring, drop-down reveal). Audio prep by the lead: `film/intro_v3/prep_v4_lead.py`, cuts in `film/intro_v3/cuts_v4.json`.
- s2a v4: F0050 (Normal card, no app zoom, walk toward Yash, smooth zoom, Yash re-synced with reply).
- s2b v4: F0042 (sonar explanation N2a-N2e in the map, relay names fixed, neutral SOS card end).
- s3 v4: F0043 + F0051 (neutral SOS card + N5, straight cut to sonar, SOS explanation with timer landing on 10/25/60 s, Accept chip).
- s4 fallback: F0044 (Three.js phone + image layers). Blender upgrade F0052 running on codex-vivek.
- Cards F0012/F0021 (+ faster closing transition in F0045). Assembler v4 + music lower + 1440p export + caption_check.py: F0045. Narration pipeline: F0048 (`film/narration/prep_v4.py`). YouTube text: F0049 (`film/final/YOUTUBE.md`).
- Model credit (must be in the YouTube description): "iPhone 12 Teardown" by Peter_D on Sketchfab (https://sketchfab.com/3d-models/iphone-12-teardown-708eaa5d195544918e5f70b69eedcdfa), licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Modified: logos removed, recoloured, animated.

## Running / queued
- F0052 (codex-vivek): scene 4 in Blender with the real model (portable Blender in its clone `local/tools/blender/`). If it fails twice, keep F0044's fallback.
- Renders on utkarsh-pc via the render runner: R0007 (s2a, s2b), R0008 (intro), R0009 (s3, s4, cards + full v4 draft assembly).
- Narration: Vivek is recording N1, N2, N2a-f, N3, N5, N5a-b, N6, N7, N7a-d into `local/narration_vivek/` on vivek-pc. The render runner on vivek-pc runs `film/narration/prep_v4.py` automatically 2 minutes after the files stop changing, and pushes `results/NARRnn/REPORT.md` plus the updated `film/common/narration_v4.json` (real durations + transcripts). Until then the films use stand-ins (old 30 Sep takes for N1/N2/N3/N5/N6, silence for new lines).

## Next (in order)
1. When F0052 lands: review stills (no Apple logo, back camera never visible, numbers exact). Accept or redo once.
2. When `results/NARRnn/REPORT.md` is done: request ALL segments re-rendered and a final assembly: `queue/render/R00xx.md` with `segs: intro,s2a,s2b,s3,s4,cards` and `assemble: final`. Then, for the 1440p export, a second request with `segs:` empty and `assemble: final` after setting nothing else (assemble_v3.py `--final-export` is run by claude-lead; if you are codex-vivek, leave the 1440p step to claude-lead).
3. Check the draft/final REPORT: loudness -16 LUFS ±1, true peak <= -1.5 dBTP, every freeze in a camera segment is an app/graphic hold (not live camera), the contact sheet.
4. If narration has NOT arrived when everything else is accepted and rendered: ping Vivek once: "iTantra: everything is ready except your narration takes."

## How to request a render
Write `queue/render/R00NN.md` (next free number, never reuse):
```
---
id: R00NN
segs: s2a,s2b          # any of intro, s2a, s2b, s3, s4, cards (empty = none)
assemble: draft        # draft | final | no
created_by: <you>
---
why
```
Commit + push. The runner on vivek-pc renders on utkarsh-pc and pushes `results/R00NN/REPORT.md` (+ `contact_960.jpg`).
