# Production stack (decided)

Keep this stack small. Add a tool only when a specific shot really needs it, and the lead foreman agrees.

| Piece | Job |
|---|---|
| **HyperFrames** (npm `hyperframes`, CLI `npx hyperframes`) | Main engine for the whole film. Each film section is one HyperFrames composition holding real footage, screen recordings and graphics together, which is what makes the shared-object transitions possible (panel → phone, packet → Yash's notification, red pulse → Vivek's notification). Also used for `snapshot` (frame checks), `beats` (music cuts), `grade-compare` (grade choice), and `render`. Needs Chrome/Chromium on the machine. |
| **Three.js inside HyperFrames** | Only for the two sonar campus scenes (relay packet and red SOS pulse). Everything else is plain HTML/CSS/SVG animated with GSAP. |
| **FFmpeg** | Before HyperFrames: sync clean audio to camera clips, trim, crop screen recordings, HDR→SDR conversion, and the colour grade on camera clips. After HyperFrames: join the rendered sections, final audio mix (music ducked under dialogue and TTS), loudness levelling, final encode. |
| **Python** | faster-whisper transcription with word timings (drives captions and graphic cues). Campus geometry: NIE building outlines from OpenStreetMap, lined up with a satellite screenshot and turned into points and contours for the sonar scenes. Audio pairing and sync checks. |

Not used unless the lead foreman finds a concrete shot that needs it: Remotion, Blender, Runway or other generative video, After Effects, Resolve, Premiere, Descript.

Graphics explain what the camera can't see (distance, relaying, encryption, nearby-device search). Real UI footage carries every app moment (notifications, Accept/Decline, Logs, SOS selection, PTT, Hands-free, TTS). Never recreate the app in graphics when a real recording exists.
