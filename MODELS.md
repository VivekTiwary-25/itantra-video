# MODELS — allocation guide for the foremen

Checked against the published docs on 29 Sept 2026. Before relying on any exact string, confirm it on each machine with `codex --help`, `codex exec --help`, `claude --help`, or a tiny test call, since versions can differ between machines.

## Claude Code

| Use | Model | Effort | How |
|---|---|---|---|
| Lead foreman (vivek-pc) | `opus` | `high` by default. Go up to `xhigh` for scene planning and batch reviews. | `claude --model opus --effort high --permission-mode auto`. Interactive, so Vivek can talk to it and the status line can report usage. |
| Second foreman (yojitth-pc) | `opus` | `high` | Listener runs `claude -p --model opus --effort high --permission-mode auto --resume claude-second "<prompt>"` (create the session first with `-n claude-second`). An interactive session that polls in a loop is also fine, if that tests better. |
| Sonnet helpers (inside the lead's session) | `sonnet` | `medium`–`high` | Subagents started by the lead. Good for FFmpeg jobs, file wrangling, first drafts of HTML scenes from a precise spec. |
| One-time setup builder (vivek-pc) | `sonnet` | `high` | `claude --model sonnet --effort high` |

Claude Code effort values: `low`, `medium`, `high`, `xhigh`, `max` (availability depends on the model).

## Codex CLI

| Model | ID | Use it for |
|---|---|---|
| GPT-6 Sol | `gpt-6-sol` | The default for real work: HyperFrames scenes, the Three.js sonar, audio sync scripts, campus geometry, anything with judgment inside a clear spec. |
| GPT-6 Luna | `gpt-6-luna` | Clear, repeatable jobs: unzipping and manifests, format conversion, frame extraction, caption file formatting, batch FFmpeg runs. Cheapest. |
| GPT-6 Astra | `gpt-6-astra` | **NEVER.** Banned by Vivek. The listener refuses it. |
| GPT-5.5 | `gpt-5.5` | Avoid. It retires 14 Oct 2026. |

Effort for Sol: `low` / `medium` / `high` / `xhigh` for normal work. `max` and `ultra` only when the lead has a specific reason (for example a stuck sonar shader), and only after testing that the value is accepted on that machine. Some setups reject `ultra` outside the ChatGPT app.

Command the listener builds:

```
codex exec -m <model> -c model_reasoning_effort='"<effort>"' --sandbox workspace-write --cd <repo_root> -o results/<id>/last-message.md "<worker prompt>"
```

Check on each machine: that `--sandbox workspace-write` lets Codex *read* `footage_root` (outside the repo) and *write* `local/renders/`. On Windows, confirm how the sandbox behaves. If reads outside the workspace are blocked, add the footage folder as a writable/readable root, or run with a wider sandbox on that machine only, and write down which one was chosen in `machines/<machine>/capabilities.json`.

## How the lead should allocate

1. **Judgment stays with Opus**: take choice, cut points, hold lengths, whether a look is right, final review. Never delegate these.
2. **Clear spec → cheapest capable worker**: Luna for mechanical work, Sol medium for normal builds, Sol high/xhigh for the hard builds (sonar, transitions).
3. **Spread the load**: prefer friends' Codex for work that doesn't need final renders, so vivek-pc stays free for renders and the lead's own usage.
4. **Watch usage**: at 70%+ of the lead's 5-hour window, push more building to Codex, give helpers only small tasks, and keep Opus for decisions and reviews. At 90%+, stop starting new work that needs Opus and tell Vivek when the window resets.
5. **Use the second foreman** for: a second opinion before showing Vivek a look, a fresh-eyes review of each finished batch, and running whole sections in parallel once a section's plan is agreed with Vivek.
6. Log every allocation, with model, effort and roughly how heavy the task was, in `log/usage.md`, so estimates get better as the project goes on.
