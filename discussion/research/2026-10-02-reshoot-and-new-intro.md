# Scene 1 reshoot + new intro plan (2 Oct 2026, written by Claude in Vivek's chat)

Read this together with `2026-10-02-research.md` in this folder.

## Status of the team
- codex-f1 (Yash's PC) is gone for good. Anything still assigned to it needs a new owner.
- The other machines come back once Vivek sets up Tailscale today. Until then, don't queue anything to them.

## What was shot this morning (South Campus, sunrise, ~6:30-9:00 IST)
North Campus was too noisy for scene 1. South Campus is quieter and looks better. Vivek will put the files in the usual `footage_root/Video` + `footage_root/Audio` layout with descriptive names.

1. Vachana's long intro (the original script): 2 takes, each in 2 parts (same split as before).
2. Vachana's short intro: 1 take. Script:
   "I'm Vachana from team chmod 777. For ISRO's problem SIH26173, we built iTantra. Speak, and your message travels phone to phone, no network needed. Let's see it work."
   Shot in front of a set of stairs.
3. The plant sequence, near the stairs:
   - Front take: she walks down the stairs, stops at a marked spot in front of a plant, looks around confused, takes her phone out, unlocks it, turns on airplane mode, presses push-to-talk.
   - Over-the-shoulder take: same action repeated from "takes her phone out", camera behind her shoulder.
   - Phone screen recording made on her phone during the take (direct sunlight made the real screen unreadable on camera).
4. Several ~10 s wide shots of the empty campus.
5. Chest-height walking shot along the campus (camera walking forward).

Check with Vivek whether 10 s of silence (room tone) was recorded at the talking spot. If not, use gaps between words for the noise profile.

## Known problems and decisions
- **App text is baked in.** The demo build's push-to-talk shows pre-set transcription. Never show the screen after she releases push-to-talk in the intro.
- **Screen unreadable in sunlight.** The real screen content gets laid over the phone screen in the edit.
- **Screen recorder overlay icon.** The phone's screen recorder left a floating icon. Vivek's preferred fix: re-record the screen over USB on his PC (simulated taps, like the earlier app recordings), timed frame by frame to the over-shoulder take, so there's no icon. Use this morning's screen recording only as a timing reference / backup. If USB re-recording isn't possible, paint or blur the icon out (it's in a fixed spot).
- **Location change.** The rest of the film is North Campus. The existing glass-panel → full-screen title card ("How the app works") between scene 1 and scene 2 hides the change.

## The new intro (about 30 s, replaces the 56 s talking intro)
Based on the research (option A, "Silent campus"). Vivek and the boss decide together whether parts of the long intro (e.g. "How a message travels") are still used.

| Time | Shot | Sound / text |
|---|---|---|
| 0-3 s | Wide empty campus at sunrise | Ambience only |
| 3-6 s | Chest-height walk along the empty path | Footsteps / ambience |
| 6-10 s | Front: she walks down the stairs, stops at the plant, looks around. Nobody. | Ambience |
| 10-12 s | Front: she takes her phone out (cut the password entry) | |
| 12-14 s | Over shoulder: she turns on airplane mode (screen overlaid) | Text: "No internet. No network. No Wi-Fi." |
| 14-18 s | Over shoulder: she presses and holds push-to-talk, looks out at the empty campus. Cut before any baked-in transcription appears. | Low hum may start |
| 18-28 s | Short intro to camera in front of the stairs, glass panel (PS ID, one-line promise) | Her short-intro line |
| 28-30 s | "Let's see it work." → panel grows into the title card | → scene 2 |

Carry over from the scene 1 v3 notes: the original gentle v1 grade (cooler feel) and the strongest noise removal that still sounds natural. The top panel needs a new position for the new background.
