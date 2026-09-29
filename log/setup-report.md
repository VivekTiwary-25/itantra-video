# Setup report (IN PROGRESS, written by the setup builder, 29 Sept 2026)

Status: **vivek-pc plumbing built and tested offline. Not yet pushed, no friend machines yet, no live round-trip tests yet.** See "Blocked / waiting" below.

## Layout (agreed with Vivek)
- Repo: `VivekTiwary-25/itantra-video`, branch `main`, a normal clone (NOT a worktree of the iTantra app repo, so no orphan branch was needed). Friends are invited to this repo only.
- Footage (never in git) sits in a separate `footage` folder next to the repo folder: the two Drive zips plus the unzipped `sih video clip\` and `sih audio clips\` folders. Each machine sets its own path as `footage_root` in `machine.local.json`.
- The original pack is kept in a `_pack-source` folder next to the repo folder (safe to delete once the repo is pushed).
- The folder above the repo is not itself a git repo. Left alone.

## Footage facts (vivek-pc manifest: `machines/vivek-pc/footage-manifest.json`)
- 16 media files: 10 video, 6 audio. About 7.1 minutes in total. `normalpart2.mp4` alone is 202 s (416 MB) of that.
- Audio is deliberately missing for `normalpart2` to `normalpart5` (Vivek: any voice there is narration added later). `normalpart6` audio was added later and is the file `Normalpart6.mp3` (capital N) in the audio zip. **Match names ignoring case.** The manifest's `pairs` section does this.
- Not HDR: every clip is H.264, 8-bit `yuv420p`, `bt709`, 1920x1080, about 30 fps variable frame rate. No HDR-to-SDR conversion is needed before grading. The video files also carry their own camera audio, which can help when syncing the clean audio.
- **Audio and video lengths do not match**, so syncing needs offsets, not a straight overlay:
  | clip | video s | clean audio s |
  |---|---|---|
  | normalpart1 | 10.83 | 11.74 |
  | normalpart6 | 12.65 | 12.01 |
  | sospart1 | 10.64 | 5.50 |
  | sospart2 | 10.70 | 16.63 |
  | vachna part1 | 19.67 | 20.67 |
  | vachna part2 | 37.12 | 37.62 |
- The audio zip in the footage folder was re-downloaded during setup (it now includes `Normalpart6.mp3`). Other machines must use that newer zip. Check zip hashes in the manifests' `archives` section.

## What works (tested)
- `tools/doctor.py`: writes `capabilities.json`. Installs nothing.
- `tools/manifest.py`: unzips (keeping the zips, keeping the paths inside the zips so relative paths are the same on every machine), runs ffprobe, HDR check, sha256, pairs video with audio.
- `tools/listener.py`: tested offline against a fake worker (no real AI, no GitHub): good run; crash with no REPORT (failed report with last 50 lines); rate-limit text (parsed "try again in 2 hours 15 minutes", paused the worker); timeout kill; Astra refusal (`status: refused`, nothing run); files over 20 MB and preview mp4 over 10 MB moved to `local/renders/<id>/` with a note in REPORT.md; dependency gate (waits for REPORT `done` AND review `accepted`); recovery of a task left running by a crashed listener; only one listener per machine (lock file). Prompts go in through stdin, so Windows quoting cannot break them.
- `tools/status.py`: shows every machine's heartbeat age and flags STALE (older than 15 min) or STOPPED. This is how a silent machine is detected (test X009).
- `tools/statusline_usage.py`: tested with sample JSON. Registered in `.claude/settings.json`. **Not yet seen with a real Claude Code session**: `local/claude-usage.json` should appear after the first response in the lead's session. If it doesn't, use `/usage`.
- Small PROTOCOL.md addition: exact front-matter formats for REPORT.md (`status:`) and reviews (`verdict:`), because the listener reads them.

## CLI flags checked on vivek-pc (codex-cli 0.159.0, Claude Code 2.1.284)
- Codex: `codex exec -m gpt-6-luna -c model_reasoning_effort="low" --sandbox workspace-write --cd <repo> --json -o <file> -` works (prompt read from stdin with `-`). `gpt-6-luna` and effort `low` are accepted. `--json` events give token usage only (`turn.completed.usage`), **no rate-limit percentages**, so Codex limits are handled reactively (rate-limit error text pauses the worker). The listener still records any `rate_limit` field if a later version adds one.
- Claude: `claude -p --model sonnet --effort low --permission-mode auto -n <name>` creates a named session, and `claude -p ... --resume <name>` continues it (it remembered a secret word). Prompt via stdin works. So `claude-second` needs no fallback memory file. Not yet tested with `--model opus` (needs yojitth's machine or a decision to spend Opus usage).
- `codex` resolves to `codex.CMD` via `shutil.which`; that works from Python.

## BLOCKED / waiting
1. ~~Codex sandbox on Windows (vivek-pc)~~ **RESOLVED 29 Sept.** It was broken (`helper_unknown_error`, and `--sandbox workspace-write` could not start a shell). The cause was not admin rights: Codex's setup step validates every file under its own `runtimes/cua_node` folder, and that folder held 7 abandoned `.staging-*` directories from failed installs on 5 and 9 Sept (about 1.2 GB), two with 331-character paths the check cannot open. With Vivek's OK they were moved (a reversible rename) to a `codex-staging-parked` folder in his user profile; the real runtime folder was left alone. After that the normal `workspace-write` sandbox works. Verified with the real listener and real Codex (`gpt-6-luna`, low): **X001 passed** (read all 16 footage files outside the repo, 425.072 s total, ran ffmpeg, wrote the test pattern to `local/renders`), and a boundary task confirmed writes to the repo and `local/renders` work while writes to the folder above the repo and to `footage_root` are denied. **Sandbox choice for vivek-pc: `workspace-write`.** If another machine shows `helper_unknown_error`, look for the same stale `.staging-*` folders first (`codex doctor` and the newest `~/.codex/.sandbox/sandbox.<date>.log` name the file that fails).
   - Fallback (built and tested, not needed on vivek-pc): if a machine's sandbox cannot be fixed and its owner approves `codex_sandbox: danger-full-access`, list every other git repo on that PC in `guard_repos` in `machine.local.json`. The listener snapshots each one (`git status --porcelain -uall`, a hash of tracked changes, HEAD) before and after every task. If anything differs it adds a SAFETY WARNING to REPORT.md, saves the details in `local/guard/<id>.txt` (kept off git because this repo is public), and pauses that worker with `local/paused-<worker>.flag` until the owner deletes the file. Limit: it cannot see edits to files that were already untracked before the task, and it will false-alarm if the owner edits a guarded repo while a task runs. The rule is in every friend bootstrap prompt.
2. **HyperFrames** is installed on vivek-pc (0.8.92, global npm). `hyperframes doctor`: Chrome, FFmpeg and FFprobe found. Not installed (optional): whisper-cpp, Kokoro, MusicGen, Docker not running. HyperFrames telemetry is switched off on vivek-pc (`hyperframes telemetry disable`), and the listener sets `HYPERFRAMES_NO_TELEMETRY=1` for every task it launches; the friend prompts have the same step. A local proof passed: a 3-second composition (text fading in on dark), `hyperframes check` clean, `hyperframes snapshot --at 0.2,1.5,2.8 --no-end` gave the expected frames (blank at 0.2 s, fully visible at 1.5 s). Notes: the starter page loads GSAP from a CDN and fonts from Google Fonts, so renders need internet.
3. **Real X004** (codex-f1 on yash-pc), the friend machines, X001 to X009 live tests, and the cross-machine manifest comparison: not started. Friends have not been invited or have not accepted yet, and the lead must be started by Vivek.

## Per-machine facts
| machine | sandbox choice | how to read usage |
|---|---|---|
| vivek-pc | `workspace-write` (verified) | Claude: status line writes `local/claude-usage.json` (untested live); fallback `/usage`. Codex: no numbers in `--json`; fallback `/status` in Codex, or wait for a rate-limit error. |
| yash-pc, utkarsh-pc, yojitth-pc | not checked yet | not checked yet |

Vivek's PC: Windows 11, 12 cores, 23.7 GB RAM, RTX 2050 (4 GB), 47.8 GB free on D:, 15.9 GB free on C:.

## Manifest differences across machines
Not compared yet (only vivek-pc exists so far).

## Renames and banner (Vivek, 29 Sept 2026)
- Machines renamed: friend1-pc -> `yash-pc`, friend2-pc -> `utkarsh-pc`, friend3-pc -> `yojitth-pc` (worker IDs unchanged). Friend prompts: `prompts/4-friend-machine-bootstrap-yash.md`, `-utkarsh.md`, `-yojitth.md`. Each tells the friend to set their own GitHub no-reply email in git config for this repo before their first commit.
- `tools/swarm_status.py` prints the swarm banner from real files only (registry, heartbeats, `local/claude-usage.json`). ONLINE means a heartbeat under 10 minutes old. The lead has no listener, so it counts as ONLINE when the status-line file was refreshed in the last 10 minutes. The lead runs `python tools/swarm_status.py --as-lead` (in its prompt), which first records `machines/vivek-pc/lead-heartbeat.json`, so the lead always shows ONLINE when it prints the banner; without the flag nothing is written, so nobody else can fake the lead. The status-line file `local/claude-usage.json` also counts as a live signal. The status line itself is not yet seen live. Tested here with made-up heartbeats (all online, mixed, no data).
- The repo is public from 29 Sept 2026, after a history scrub (one clean commit, authored with the GitHub no-reply address).
