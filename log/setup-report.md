# Setup report: FINAL HANDOVER (30 Sept 2026)

**Status: setup is done.** The task system works end to end on all four machines: tasks go out through git, workers run them, results come back, reviews and redos work, and a silent machine is detected. Three small things still need a person (section 10). No film work has been started.

## 1. Machines and workers
| Machine | Owner (GitHub) | Workers | Hardware | CLIs |
|---|---|---|---|---|
| vivek-pc | Vivek (VivekTiwary-25) | `claude-lead` (interactive), `claude-helper` (Sonnet subagents), `codex-vivek` (listener). **Final renders happen here.** | RTX 2050 4 GB, 12 cores, 23.7 GB RAM | Codex 0.159.0, Claude Code 2.1.284, ffmpeg 7.1.1 |
| yash-pc | Yash (MATHUR-Yash) | `codex-f1` | RTX 3050 6 GB, 12 cores, 15.6 GB | Codex 0.159.0, ffmpeg 9.0.2 |
| utkarsh-pc | Utkarsh (utkarshKeshri11sketch) | `codex-f2` | RTX 4050 6 GB, 16 cores, 15.8 GB | Codex 0.159.0, ffmpeg 9.0.2 |
| yojitth-pc | Yojitth (Yojithn) | `claude-second` (second foreman) | no GPU, 18 cores, 15.4 GB | Claude Code 2.1.284, ffmpeg 9.0.2 |

Repo: `VivekTiwary-25/itantra-video`, **public**, branch `main`, a normal clone on each machine. HyperFrames 0.8.92 is on all four (telemetry off). Every machine also has Chrome or Edge.

## 2. Test results
| Test | Result |
|---|---|
| X001 plumbing on vivek-pc | PASSED |
| X002 plumbing on yash-pc | FAILED (honestly): the worker could not see a working ffmpeg. Redo **X012 PASSED** |
| X003 plumbing on utkarsh-pc | PASSED |
| X004 HyperFrames still on yash-pc | FAILED (honestly): sandbox has no internet, GSAP came from a CDN. Redo X010: work was right, record wrong (my blocker bug). Clean re-run **X014 PASSED** |
| X005 Astra refused | PASSED on a real machine: `status: refused`, nothing ran |
| X006 second foreman consult | PASSED: a sensible answer that led to real safeguards |
| X007 + X008 review then redo | PASSED: `reviews/X001.md` said redo, X008 came back with `cpu_cores` and every other key kept |
| X009 silent machine | PASSED (section 8) |
| X011 then X013 sandbox diagnostic on utkarsh-pc | PASSED: ffmpeg, temp folder and HyperFrames healthy after the fix |
| X015 / X016 HyperFrames on utkarsh-pc / vivek-pc | PASSED both (Chrome reachable inside the sandbox) |
| X017 / X018 second foreman remembers its earlier answer | FAILED both, found a real bug (section 7). Fixed in code. **Live proof still pending**: needs yojitth-pc's listener restarted, then a new task (X019) |

Failures were honest reports from workers or bugs of mine, and each one led to a fix that is now in the code or the rules.

## 3. Exact commands that worked
- **Codex worker** (built by the listener): `codex exec -m <model> -c model_reasoning_effort="<effort>" --sandbox workspace-write --cd <repo> --json -o <file> -` with the prompt sent on stdin (no Windows quoting problems). Models used: `gpt-6-luna` (low) and `gpt-6-sol` (medium). `gpt-6-astra` is refused by the listener before anything runs.
- **Second foreman**: `claude -p --model opus --effort high --permission-mode auto --add-dir <footage_root>` plus `--session-id <uuid>` on the first task and `--resume <uuid>` afterwards, prompt on stdin. The ID form was checked against the real CLI on vivek-pc. On yojitth-pc only the older name-based first task (X006) has run live.
- **HyperFrames**: `hyperframes.cmd init project --non-interactive --skip-transcribe`, `hyperframes.cmd check`, `hyperframes.cmd snapshot --at 0.2,1.5 --no-end -o snaps`, with `HYPERFRAMES_NO_TELEMETRY=1` and `HYPERFRAMES_SKIP_SKILLS=1`.
- **Git**: `git pull --rebase --autostash origin main`, `git push origin HEAD` with up to 5 retries. Heartbeats every 5 minutes; `tools/status.py`, `tools/swarm_status.py` and `tools/find_stuck_tasks.py` read them.

## 4. Sandbox choice per machine
`workspace-write` everywhere Codex runs (vivek-pc, yash-pc, utkarsh-pc). Nobody uses `danger-full-access`. The optional `guard_repos` safety net is built and tested but unused. What the sandbox does (checked on vivek-pc): workers can **read** the footage, **write** the repo, `local/renders` and `local/tmp`, cannot write anywhere else, and have **no internet**. The Windows sandbox on vivek-pc was broken at first by stale `.staging-*` folders in Codex's runtimes folder (moved aside, not deleted; the parked copy can be deleted). yash-pc and utkarsh-pc needed ffmpeg copied to a plain folder listed in `path_prepend` (`tools/fix_ffmpeg_path.py`).

## 5. Reading usage
- **Claude lead**: the status line writes `local/claude-usage.json` (works live: the banner shows real 5-hour and 7-day percentages). Fallback: `/usage`.
- **Codex**: `codex exec --json` gives token counts only, no percentages. A real rate-limit error pauses that worker (parsed from Codex error events; tested with fake errors, never yet hit for real). Fallback: `/status` in Codex on that PC.
- **claude-second**: the listener gives no usage numbers. Ask Yojitth's agent to run `/usage` when needed.

## 6. Footage (identical on all four machines)
16 files (10 in `Video/`, 6 in `Audio/`), same paths, sizes and sha256, **425.073 s (7.1 min)**. Layout: `footage_root` holds exactly `Video/` and `Audio/`; clips are `FOOTAGE:Video/<name>` and `FOOTAGE:Audio/<name>`; names match ignoring case (`Audio/Normalpart6.mp3` goes with `Video/normalpart6.mp4`). `python tools/compare_manifests.py` checks this. Facts for the lead:
- Not HDR: every clip is H.264, 8-bit, bt709, 1920x1080, about 30 fps variable frame rate. The video files carry their own camera audio.
- Audio is missing for `normalpart2` to `normalpart5` on purpose (narration will be added later).
- Clean audio and video lengths differ, so syncing needs offsets, not a straight overlay:

| clip | video s | clean audio s |
|---|---|---|
| normalpart1 | 10.83 | 11.74 |
| normalpart6 | 12.65 | 12.01 |
| sospart1 | 10.64 | 5.50 |
| sospart2 | 10.70 | 16.63 |
| vachna part1 | 19.67 | 20.67 |
| vachna part2 | 37.12 | 37.62 |

## 7. What testing taught us (all fixed; the rules are in PROTOCOL.md, AGENTS.md and CLAUDE.md)
- **Workers have no internet.** A composition that loads GSAP, fonts or images from a URL fails. A local GSAP 3.14.2 is in `film/vendor/gsap/`. No URLs while building.
- **Call npm tools as `hyperframes.cmd` / `npx.cmd`.** The `.ps1` shims can be blocked by a machine's execution policy. We did not weaken any execution policy.
- **`TEMP`/`TMP` are set to `<repo>/local/tmp` for every task** (the normal Windows temp folder is blocked in the sandbox). Cleaned after 2 days.
- **ffmpeg visibility:** a worker's PATH differs from the owner's shell. The listener builds the worker PATH like a fresh terminal, re-reads `machine.local.json` each task (so `path_prepend` edits apply at once), and `tools/fix_ffmpeg_path.py` repairs a machine.
- **Failure logs echo our docs**, so rate-limit detection scans only real error events, never tool output or model messages.
- **The repo is public.** Results are redacted (home, repo, footage and renders paths become placeholders, at any backslash nesting). Result files with an email (other than GitHub or Anthropic no-reply) or a token-like string are held back in `local/quarantine/`. Vendored or minified libraries are exempt. A worker's own report is never overwritten unless the report itself is the problem. Both safeguards were caused to misfire once during testing and were fixed; always test safeguards against real worker output.
- **Duplicate session names break `--resume`:** two Claude sessions named `claude-second` make `--resume claude-second` fail. The listener now tracks the session by ID and repairs both errors seen (ambiguous name, "already in use") with one automatic retry. The bootstrap prompts use a throwaway session name.
- **The listener restarts itself** between tasks when a git pull changes the tool code (exit code 75, `start-listener.cmd` loops), and one bad task can no longer stop the listener.

## 8. Silent machines (X009)
utkarsh-pc's listener was stopped and left no "stopped" heartbeat. Timeline from its last heartbeat: the banner showed `OFFLINE last seen 10m ago` at 10 minutes; `tools/status.py` said STALE and `tools/find_stuck_tasks.py` flagged `STUCK X009` at 15 minutes, naming healthy workers of the same kind. The lead reassigns by writing a NEW task with `redo_of: <old id>` for a healthy worker and a `dropped` review for the old one. When the listener returned it simply ran the queued task (X009 done). A silent machine is invisible for the first 10 to 15 minutes by design; do not rely on a `stopped` heartbeat because a killed listener leaves none.

## 9. Tools
`listener.py` (the worker daemon), `doctor.py` (what a machine has; installs nothing), `manifest.py` (footage layout and manifest), `compare_manifests.py`, `status.py`, `swarm_status.py` (the banner; the lead runs it with `--as-lead`), `find_stuck_tasks.py`, `sandbox_check.py` (what a Codex worker really sees), `fix_ffmpeg_path.py`, `statusline_usage.py`, `start-listener.cmd`.

## 10. Open items (each needs a person, none blocks starting the lead)
1. **Restart Vivek's listener once.** It is still the first version, started 29 Sept 23:48, so it lacks every fix. After one restart it updates itself. (`tools\start-listener.cmd`)
2. **Yojitth's agent: run `git pull` and restart the listener once** (same reason). Then queue X019 (redo of X018) to prove the second foreman's session memory live. Until then the second foreman's follow-up tasks will fail.
3. **Yash's agent: set the repo's git identity to his no-reply address** (`245989214+MATHUR-Yash@users.noreply.github.com`, name `MATHUR-Yash`, run inside the repo and check `git log -1 --format=%ae` after the next heartbeat). His newest commit still used his college email. Yash accepted the college email on his older commits.
4. Windows power settings: the PCs must not sleep while listeners run. Not checked.
5. Film info still missing (ask Vivek): team ID for the title card, the exact official problem-statement text, music track (if any), SIH deadline and length limit.

## 11. State of the public repo (privacy)
Checked on 30 Sept over everything pushed to GitHub: no tokens, no Gmail address, no Drive link, no Windows account names except Yash's in 6 old revisions of one file (`results/X002/REPORT.md`, scrubbed at the tip), and Yash's college email on his older commits (his choice). The history was squashed once, before the repo went public, to remove an account name and an email. A local-only branch `pre-public-backup` on vivek-pc still holds those old commits: never push it, delete it when no longer needed. Everyone else uses GitHub no-reply addresses.

## 12. Next step
Start the lead foreman on vivek-pc, in the repo folder: `claude --model opus --effort high --permission-mode auto`, then paste `prompts/2-lead-foreman-opus.md`. Its first action is `git pull` and `python tools/swarm_status.py --as-lead`, shown to Vivek in a code block. Then it asks Vivek for the missing film information and waits for a go for batch 1 (footage inventory and shot list, no editing).
