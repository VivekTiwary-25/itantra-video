# Film v4 nitpick fixes (claude-lead, 4 Oct 22:30): Vivek's decisions on `FINAL/nitpick_report.txt`

Source: the team-notes review of `FINAL/iTantra_SIH26173_chmod777_1080p_REVIEW.mp4` (3:21.9). Vivek's decisions:
1. 0:06 cut (intro): a 0.35 s cross-dissolve inside her natural pause (~6.5-6.95 s), and the name card morphs into the phone panel (no swap).
2. Status bars: the shared home-screen screenshot is cleaned once (the lead did it: every `local/private-in/*/home.png` on vivek-pc and utkarsh-pc now has the status bar painted out in the app background colour #07111c). Every raw app recording with a visible status bar gets a MASK on the phone layer: a solid strip in the app's own background colour over the status bar area (not a blur, not a zoom or crop), the same look as Vachana's s2a recording: Yash's recording in s2a, Vachana's SOS recording and Vivek's recording in s3. The hotspot "devices" pill and the icons must never show. (The red notification banner of the real Android notification is NOT part of the status bar: keep it; only the top status strip is masked.)
3. 2:29 (s3 sonar): both rings centred on Vachana only; no ring on any other dot (remove ring 2's re-sourcing).
4. 2:30 (s3 sonar): the Accept chip in OUR graphic turns green when accepted. Green is the one palette exception, used only for this Accept. Never touch the real app recording.
5. Idle time: s3 2:50.8-2:53.3: trim ~2 s of the idle stretch in Vivek's recording before Send and re-fit the Send sound. Also trim idle stretches from s3's other near-still app screens (2:34-2:44: notification, Logs, his SOS message, play-audio screen) where nothing changes for > 0.8 s, keeping every tap and the Accept clearly visible. Never speed up; only cut idle frames, with a 3-frame dissolve if a cut would jump. s4: the phone at 2:56 keeps a slow turntable spin instead of stopping. Leave intended holds alone (cards, map holds, title cards).
6. Narration: new takes come from a teammate for N1-N7d plus three new lines (in `film/common/narration_v4.json`, with exact text):
   - N0 over the "Normal" card (s2a, at its start): "First, a normal message. It's private, just for someone you trust." The card holds as long as N0 + 0.4 s.
   - N8 over the "Works now / Coming next" card: "Here's what works today, and what we're building next."
   - N9 over the closing card: "iTantra. Speak. Send. Be heard."
   - While narration plays over the relay clips (s2b, N2f), hide their baked-in captions ("Her phone passes the message on..." etc.) so they don't collide with the narration captions.
   - Every narrated beat stretches to its take + 0.4 s (reads `duration` from the manifest at build). This also holds each scene 4 number label at least 2.5 s.
   - Stand-in wavs exist for every line (silence for new lines) so production builds run now; the real takes replace them automatically (render runner on vivek-pc runs `film/narration/prep_v4.py`).
7. Rendering on utkarsh-pc (yash-pc fallback). Final: 1080p master ONLY (Vivek, 22:40: no 1440p upscale), into `D:\projects\SIH\Presentation\FINAL\` with a README (the lead does this).
