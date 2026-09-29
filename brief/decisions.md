# Decisions so far (29 Sept 2026)

Everything here was agreed with Vivek. Treat it as current until Vivek changes it.

## The film
- The film brief (brief/film-brief.md) is a solid idea, NOT a locked script. The ~4:20 length and the story order are both open.
- Discuss every scene with Vivek before it is built. Never build a scene he hasn't talked through.
- Hard rules from the brief always apply (relays never show message content; SOS never uses the relay chain; Vivek is never a trusted contact and never auto-accepts; no verification codes, debug screens or "demo/mock/simulation" labels; Yash and Vivek are never shown waiting inside iTantra; the montage adds no new claims; restrained, non-trailer sound).
- Footage: camera clips shot on a Samsung S23 Ultra in daylight, plus separately recorded clean audio. Vivek supplies each video with its matching audio file. All dialogue is in English. Footage layout (the same on every machine): `footage_root` contains exactly two folders, `Video/` (the 10 .mp4 clips) and `Audio/` (the 6 .mp3 files), with the original file names and no other folders (the Drive zips may sit beside them but are never used). Clip paths are always `FOOTAGE:Video/<name>` or `FOOTAGE:Audio/<name>`, for example `FOOTAGE:Video/normalpart1.mp4`. Video and audio names are matched ignoring case (`Audio/Normalpart6.mp3` belongs to `Video/normalpart6.mp4`). Machines are compared by these paths plus sha256 (`python tools/compare_manifests.py`), not by how the files arrived.
- Every machine has its own full copy of the footage and audio, at different paths.
- Colour grade: natural and cinematic, applied to camera clips only, never to screen recordings. Vivek approves it from before/after stills first. Check whether the clips are HDR and convert them properly before grading.
- Audio: clean up every voice track (noise, hum, EQ, de-ess, levelling, final loudness). The agents cannot hear, so Vivek judges audio from short samples.
- The app footage comes from three actor-specific demo builds that all look like the same iTantra app (brief/three-app-builds.md).

## How we work
- Work in batches and check each one with Vivek before starting the next. Never do one long unattended run.
  1. Footage inventory and shot list (no editing).
  2. Rough cut with no graphics.
  3. Graphics as still frames.
  4. Graphics in motion and transitions, one section at a time.
  5. Finish: music, sound design, captions, grade, export.
- Vivek wants plain, simple language, and a short TLDR at the end of every message to him. Anything he needs to do or answer goes at the very end, after the TLDR.

## The team
- Lead foreman: Claude Opus on Vivek's PC. Makes the decisions, talks to Vivek, and has the final say.
- Second foreman: Claude Opus on yojitth's PC. Gives second opinions, reviews batches with fresh eyes, and can run a whole section when the lead hands one over. The lead decides when and how to use it.
- Workers: Claude Sonnet helpers (subagents inside the lead's session), Codex on Vivek's PC, Codex on yash's PC, and Codex on utkarsh's PC.
- The lead foreman picks the worker, model and effort for every task, based on how much work is left and how much usage remains.
- GPT-6 Sol is allowed, including for heavy jobs. GPT-6 Astra is NEVER used.
- Usage checks: read it automatically where possible. If it can't be read, take control of Vivek's machine, run /usage (Claude) or /status (Codex), and read a screenshot.
- The repo is its own GitHub repo, `VivekTiwary-25/itantra-video` (branch `main`), a normal clone on each machine. It is NOT part of the iTantra app repo and not a worktree of it. Friends are invited to this repo only, never to the iTantra app repo. Local folder paths live in each machine's git-ignored `machine.local.json`, never in git.
- Footage lives outside the repo (in a separate `footage` folder on each machine, set as `footage_root` in `machine.local.json`) and is never committed.
- Audio: `normalpart2` to `normalpart5` have no separate audio on purpose. Any voice over them is narration added later. The other clips (`normalpart1`, `normalpart6`, `sospart1-2`, `vachna part1-2`) each have a matching audio file. Match file names ignoring case (e.g. `Normalpart6.mp3`).

## Still missing (ask Vivek when needed)
- Team ID for the title card.
- The exact official problem-statement text (copied from the SIH portal).
- Music track, if he has one in mind.
- SIH video deadline and length limit.
