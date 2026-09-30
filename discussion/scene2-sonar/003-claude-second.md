# scene2-sonar: done

From: claude-second

All five segments are final: sonar_a 7.0 s, relay_1/2/3 6.0 s each, and sonar_b 6.0 s, which ends on a still from 5.2 s. They pass `hyperframes check`, and each has an sfx stem; there's also one 31 s music stem. Changes since progress 1:
- In each dive, the point's flare now lands on the person.
- The whoosh peaks with the flare, at 0.65 s.
- The music is quieter in the narration zones (0-3.5 s and 29.0-30.8 s).

**To build:** `python film/scene2/sonar/build.py`, then render each segment folder.

**To review:** `results/T0004/preview/sonar_section_preview_a_540p.mp4` (version a, with music).

**For Vivek's ears:** pings, tick, chime and music taste; I can't hear them.

Details, cue times and my judgement calls are in `results/T0004/REPORT.md`.
