# SETUP SPEC — build the multi-machine video production system

> **Layout change (Vivek, 29 Sept 2026):** this project is its own private repo, `VivekTiwary-25/itantra-video`, branch `main`, cloned normally. It is NOT a worktree of the iTantra app repo. Wherever this spec says "worktree", "branch `video-production`" or "SIH repo", read "the itantra-video repo, branch `main`". Step 0 is already done. Friends are invited to this repo only.

**Who runs this:** Claude Code, Sonnet, effort high, on vivek-pc (Windows).
**Goal:** a working git-based task system across 4 machines, proven by round-trip tests. You are NOT editing the film. You are building the plumbing and proving it works.
**Time cap:** about 2 hours of your work. If a piece won't work, don't spend long on it. Write down what's blocked and tell Vivek.

Read first: `PROTOCOL.md`, `MODELS.md`, `brief/decisions.md`. They are the source of truth. If this spec and PROTOCOL.md disagree, PROTOCOL.md wins.

Talk to Vivek in plain, simple language, with a short TLDR at the end of each message and anything he must do at the very end. Ask before any step that can't be undone (force-push, deleting branches, touching the iTantra app worktrees).

---

## Step 0 — Find the repo and make the worktree
1. Find Vivek's private SIH repo on this PC (ask him for the path if you can't find it). Check `git remote -v` and `git worktree list`.
2. Create a new branch `video-production` from the default branch, and a worktree for it at `sih/presentation/video` (adjust to the real layout, and confirm the path with Vivek before creating it). Do not touch any existing iTantra worktree.
3. Push the branch to origin.

## Step 1 — Lay down the files
1. Copy this pack into the worktree root: `PROTOCOL.md`, `MODELS.md`, `brief/*`, `prompts/*`.
2. Create the folders from PROTOCOL.md §2, with a `.gitkeep` where needed.
3. `.gitignore`: `local/`, `machine.local.json`, all video/audio/archive types (`*.mp4 *.mov *.mkv *.m4a *.wav *.aac *.mp3 *.flac *.zip *.7z`), but allow `results/*/preview/*.mp4` (the listener still enforces 10 MB).
4. `machines/registry.json` with the six workers from PROTOCOL.md §1 and the four machine names (`vivek-pc`, `yash-pc`, `utkarsh-pc`, `yojitth-pc`). Vivek may rename them; the names must match everywhere.
5. `AGENTS.md` (Codex reads this automatically) and `CLAUDE.md` (Claude reads this automatically). Both say, briefly: read PROTOCOL.md and brief/decisions.md first; you are a worker; do exactly the task file you were given; write only inside its `writes:`; finish with REPORT.md; never use GPT-6 Astra; never commit footage or files over 20 MB; follow brief/style.md once it exists. The Claude version also adds: "If you are claude-lead or claude-second, your role prompt overrides the worker parts of this file."

## Step 2 — Tools (Python 3.11+, stdlib only where possible, must work on Windows)

**`tools/doctor.py`** — writes `machines/<machine>/capabilities.json`. It reports:
- The versions of git, python, node, npm, ffmpeg, ffprobe, `npx hyperframes --version`, codex, and claude.
- Whether Chrome or Edge is present, since HyperFrames needs one.
- GPU name and VRAM (`nvidia-smi` if present), CPU cores, RAM, and free disk space on the drives holding the repo and the footage.
- Anything missing is listed under `"missing"`.
- It installs nothing by itself. It prints the install commands for Vivek or the machine owner to approve.

**`tools/manifest.py`** — scans `footage_root`, auto-extracting any `.zip` it finds into a sibling folder first (never deleting the zip). It writes `machines/<machine>/footage-manifest.json` with, for every media file: the relative path, size, duration and streams (from ffprobe), whether it's HDR (color transfer = smpte2084 or arib-std-b67), and sha256. It also writes a summary: file count and total duration.

**`tools/listener.py`** — the core. Behaviour:
- It reads `machine.local.json`, and refuses to start if that file is missing or its machine name isn't in the registry.
- Every 30 s, with a small random jitter, it runs `git pull --rebase`. For each of this machine's workers, it looks for `queue/<worker>/*.md` with no `results/<id>/STARTED.json`, taking them in ID order and respecting `depends_on` (a dependency must have a REPORT with `status: done` and a review saying `accepted`).
- It runs one task at a time per worker. Before starting, it writes `STARTED.json` (machine, worker, time, model, effort, pid), then commits and pushes.
- It **refuses** any model containing `astra` (case-insensitive), writing REPORT.md with `status: refused`.
- It launches the CLI (use `shutil.which`, because Windows `.cmd` shims need their full path):
  - Codex workers: `codex exec -m <model> -c model_reasoning_effort="<effort>" --sandbox workspace-write --cd <repo_root> -o results/<id>/last-message.md "<prompt>"`
  - `claude-second`: `claude -p --model <model> --effort <effort> --permission-mode auto --resume claude-second "<prompt>"` (create the named session on the first run with `-n claude-second`). Verify the exact flag combination works with `claude --help` and a test run. If `--resume` and `-p` don't combine as expected, fall back to a fresh session each time plus a `local/second-foreman-notes.md` memory file that the prompt tells it to read and update.
  - `<prompt>` = "You are worker <worker> on machine <machine>. Your machine config is machine.local.json. Read AGENTS.md (or CLAUDE.md), PROTOCOL.md and brief/decisions.md, then do the task in queue/<worker>/<id>.md exactly. Finish by writing results/<id>/REPORT.md."
  - Env vars passed: `FOOTAGE_ROOT`, `RENDERS_DIR`, `MACHINE`, `WORKER`, `TASK_ID`.
- It kills the task at `timeout_min`.
- After exit:
  - If REPORT.md is missing, it writes one with `status: failed` and the last 50 lines of output.
  - It scans the output for rate-limit or quota errors. If found, it sets `rate_limited_until` in the heartbeat (from the error text if given, otherwise now + 30 min) and pauses that worker until then.
  - It checks everything under `results/<id>/`: files over 20 MB are moved to `local/renders/<id>/` and the move is noted in REPORT.md. Preview mp4s over 10 MB get the same treatment.
  - It commits `results/<id>/` with the message `result <id> <status> (<worker>@<machine>)`, then pushes with up to 5 retries (`pull --rebase`, then push).
- Every 5 min it writes `machines/<machine>/heartbeat.json`, commits and pushes. Those commits touch only that file.
- It logs to `local/logs/listener-<date>.log`.
- It runs until Ctrl+C. Also provide `tools/start-listener.cmd`, which runs it with the right Python.
- If `codex exec --json` output includes rate-limit or usage percentages, record the latest values in the heartbeat. Check this by running one test call with `--json` and reading the events.

**`tools/statusline_usage.py`** — only on vivek-pc (and yojitth-pc if the second foreman runs interactively). It is a Claude Code status-line command: it reads the status-line JSON from stdin, writes `rate_limits` and `context_window` to `local/claude-usage.json`, and prints a one-line status (model, 5h %, 7d %, context %). Register it in the worktree's `.claude/settings.json` under `statusLine`. The JSON field names are `rate_limits.five_hour.used_percentage` and `rate_limits.seven_day.used_percentage`, and they appear only after the first response in a session.

## Step 3 — Set up vivek-pc
1. Write `machine.local.json` for vivek-pc (ask Vivek for the footage folder path).
2. Run `doctor.py`. Help Vivek install anything missing (ffmpeg, node, hyperframes), with his approval.
3. Run `manifest.py`, including unzipping the footage.
4. Start the listener for `codex-vivek` in its own terminal.
5. Remind Vivek to set Windows power settings so the PC doesn't sleep while listeners run.

## Step 4 — Friend machines
Friends run `prompts/4-friend-machine-bootstrap.md` themselves in their own Codex (yash, utkarsh) or Claude Code (yojitth). Your job:
1. Make sure the repo invite exists for each friend (Vivek does the GitHub collaborator invite; tell him exactly where).
2. Fill in the repo URL, branch and machine name in a copy of the bootstrap prompt for each friend (`prompts/4-...-yash.md`, etc.), so Vivek can just send it to each friend.
3. Watch for each machine's `capabilities.json` and `footage-manifest.json` to appear in git.

## Step 5 — Round-trip tests (all must pass)
Write these tasks as `claude-lead` would (IDs `X001`…), then watch for the results:

| Test | Task | Pass when |
|---|---|---|
| X001–X003 | For codex-vivek, codex-f1, codex-f2 on `gpt-6-luna` / `low`: write `results/<id>/hello.json` with the machine name, footage file count and total duration read from the local footage, the first line of `ffmpeg -version`, and a 1-second 360p ffmpeg test pattern rendered to `local/renders/` (report it as `RENDERS:<file name>`, never an absolute path, because this repo is public). | All three REPORTs `done`. Footage counts match across machines. |
| X004 | codex-f1, `gpt-6-sol` / `medium`: a 3-second HyperFrames composition (text fading in on dark), with a `snapshot` PNG at 1.5 s committed as a preview. | PNG is present and looks right when you open it. |
| X005 | Same as X004 but `model: gpt-6-astra`. | The listener refuses it, with `status: refused`. |
| X006 | claude-second, consult: open `discussion/setup-test/001-claude-lead.md` asking "Name one risk in this setup." | `002-claude-second.md` appears with a sensible answer. |
| X007 | Write `reviews/X001.md` = redo with a note ("add CPU core count"), then task `X008` with `redo_of: X001`. | The redo comes back with the core count. |
| X009 | Stop utkarsh's listener (ask Vivek to have utkarsh press Ctrl+C), queue a task for codex-f2, wait for a stale heartbeat. | You detect the stale machine and would reassign. Write down how you detected it. |

Also check that the footage manifests match across all four machines (same files, sizes and hashes). List any differences for Vivek.

## Step 6 — Hand over
Write `log/setup-report.md` covering: what works, what's blocked, the exact CLI flags that worked on each machine, the sandbox choice per machine, how usage can be read on each machine, and any manifest differences. Then tell Vivek in plain words that setup is done or what's blocking it, and that the next step is starting the lead foreman with `prompts/2-lead-foreman-opus.md`.

Do NOT start any film work.
