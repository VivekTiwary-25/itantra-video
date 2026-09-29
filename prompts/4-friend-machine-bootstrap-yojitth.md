# Startup prompt — friend machine bootstrap
**Paste into:** Codex on yash-pc and utkarsh-pc (`codex -m gpt-6-sol`, medium effort is fine), or Claude Code on yojitth-pc (`claude --model sonnet --effort high`). Open it in an empty folder where the repo should live.
**Before sending:** fill in the four values in CAPS. The setup builder makes a filled-in copy for each friend.

---

This machine is joining a small git-based production system for an SIH demo film. You'll set it up and start a listener. You won't do any film work yourself.

- Machine name: yojitth-pc 
- Worker on this machine: claude-second 
- Repo: https://github.com/VivekTiwary-25/itantra-video.git, branch `main`
- Footage zips are at: (ask the owner of this PC where they saved the two Google Drive zips: `sih video clip-...zip` and `sih audio clips-...zip`)

Do this, and ask the owner of this PC before installing anything:
1. Check that git can reach the repo (the owner must have accepted the GitHub invite). Clone the branch `main` here.
   Before your first commit, set YOUR OWN GitHub no-reply email for this repo only (not `--global`), so your real email never shows in the repo's history: find it at GitHub > Settings > Emails (tick "Keep my email addresses private"; it looks like `12345678+username@users.noreply.github.com`), then run `git config user.email "<that address>"` and `git config user.name "<your GitHub username>"` inside the repo folder.
2. Read `PROTOCOL.md`, `MODELS.md` and `SETUP_SPEC.md` (Steps 2–3 describe the tools).
3. Create `machine.local.json` in the repo root (it's git-ignored) with this machine's name, worker, repo_root, footage_root (the folder the zips extract into), renders_dir = `<repo_root>\local\renders`, and os.
4. Run `python tools/doctor.py`. Install what's missing, with the owner's OK. Needed: git, Python 3.11+, ffmpeg/ffprobe, Node 22+, and `npm i -g hyperframes` (or use it through npx). Chrome or Edge must exist.
   After HyperFrames is installed, turn off its anonymous usage tracking: run `hyperframes telemetry disable` (or set the environment variable `HYPERFRAMES_NO_TELEMETRY=1`). The listener also sets it for every task it launches.
5. Run `python tools/manifest.py`. It extracts the zips (keeping the originals) and writes the footage manifest.
6. Confirm the worker CLI works non-interactively on this machine:
   - Codex: `codex exec -m gpt-6-luna "print the word ready"`, then confirm that `-c model_reasoning_effort='"low"'` is accepted. Also check that `--sandbox workspace-write` can read files under footage_root. Note the result.
   - Codex on Windows: also run `codex doctor`. If it reports `sandbox provisioning failed` (`helper_unknown_error`), or a `codex exec --sandbox workspace-write` test can't start a shell, TELL THE OWNER and write it in your report. Do not change sandbox settings or run anything as administrator without the owner's OK.
   If the sandbox is broken and the owner explicitly approves the fallback, set `"codex_sandbox": "danger-full-access"` in `machine.local.json` and list every OTHER git repo on this PC that must never change in `"guard_repos": ["<path>", ...]` in the same file. The listener then checks those repos before and after every task, and pauses this worker (with a warning in the report) if anything changed. Never use the fallback without the owner's OK.
   - Claude (yojitth-pc): `claude -p --model opus --effort high -n claude-second "reply with the word ready"`, then check that `claude -p --resume claude-second "reply again"` continues the same session.
7. Commit and push `machines/yojitth-pc/capabilities.json` and `footage-manifest.json`.
8. Start the listener: `tools\start-listener.cmd`. Leave that terminal open.
9. Tell the owner, in plain words: set Windows power settings so this PC doesn't sleep while the listener runs, keep the terminal open, and Ctrl+C stops it.

Never use GPT-6 Astra. Never commit footage. Never touch any other repo.
