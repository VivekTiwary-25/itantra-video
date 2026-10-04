# Acting-lead hand-back (claude-second, F0028, 10:45-10:58 IST)

Short stint: claude-lead came back at 10:55 (004). Everything below is pushed.

## Decided / done
- **Exploded view out of the film:** removed the `exploded` entry from `film/final/v3_segments.json` (s3 → cards). The `_note` records Vivek's hold. Restore the entry from git history when the new teardown is ready.
- **F0025:** `reviews/F0025.md` = dropped (there was already a review file; I overwrote it with the same verdict).
- **F0026 (mine):** accepted, flagged as a self-review in the review file. Please re-check if you want. Module only; s2a is not wired yet (see S0101).
- **F0020 (s2a fixes): accepted** after the 480 px phone sheet review:
  - the sent-state frame sits under the flying card
  - the banner and Logs punch-ins are readable
  - `Sped up 26×` is bottom left
  - split captions are inside the camera panel
  - end state unchanged (11.690 s, 735/40/450/1000)
  - no live hold seen
- **Queued S0101 → codex-f1** (`depends_on` F0020, F0026, both accepted): wire the live overhead videos into s2a. Started at 10:57.
  - One constraint I found: `normalpart2` ends at 202.38 s and the walk ramp already uses source to 202.15. So the task says to overlap the overhead's first 0.88 s with the walk's tail (second clip of `walk.mp4`, media-start = walk duration - 0.88), not to extend the walk.
  - That makes s2a about 0.88 s shorter. `end_state` must stay 11.690 s / same rect.
  - Yash's clip runs under the dissolve from source 0, then his live shot continues at 0.98 with speech and caption moved 0.98 s earlier.
- **Render request `queue/render/R0001.md`:** `segs: s2a`, `assemble: draft`, to render the accepted F0020 s2a and see whether s2b/s3 pictures exist and what QC says. The runner had started it (STARTED.json) at 10:58; no REPORT yet.

## Open (for claude-lead)
1. **R0001 result:**
   - Check that s2b and s3 pictures existed. The draft names list them as slates if not.
   - Look at the QC freezes in camera segments. The overhead will still show held stills until S0101 lands.
   - After S0101 is accepted, s2a needs a re-render, plus `v3_segments.json` s2a `expected_duration` (44.154 → new value) and TTS fallback updated from its REPORT.
2. **F0023 (intro) was still running at hand-back.** In review, check that its last frame matches s2a's frame 0 card exactly.
3. No ntfy sent to Vivek (no full draft yet).
