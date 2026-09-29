# PROTOCOL — how the machines and agents work together

Every agent in this system reads this file before doing anything. Git is the only channel between machines. Every message is a file, every file has exactly one author, and nothing is edited by two machines. That is why there are no merge fights.

## 1. Who's who

| Worker ID | Machine | What runs | Role |
|---|---|---|---|
| `claude-lead` | vivek-pc | Claude Code, Opus, interactive | Lead foreman. Decides, writes tasks, reviews, talks to Vivek. Final say. |
| `claude-helper` | vivek-pc | Sonnet subagents inside the lead's session | Quick local jobs. Does NOT use git queues. |
| `codex-vivek` | vivek-pc | Codex CLI via listener | Worker. Final renders happen here by default. |
| `codex-f1` | yash-pc | Codex CLI via listener | Worker |
| `codex-f2` | utkarsh-pc | Codex CLI via listener | Worker |
| `claude-second` | yojitth-pc | Claude Code, Opus, via listener (or interactive loop) | Second foreman. Consults, reviews with fresh eyes, can run a whole section with its own Sonnet subagents. |

The canonical list lives in `machines/registry.json`. Each machine also has a local, git-ignored `machine.local.json` saying which machine it is and where its paths are:

```json
{
  "machine": "yash-pc",
  "workers": ["codex-f1"],
  "repo_root": "D:\\sih\\presentation\\video",
  "footage_root": "E:\\itantra-footage",
  "renders_dir": "D:\\sih\\presentation\\video\\local\\renders",
  "os": "windows"
}
```

Tasks never contain absolute paths. Footage is referred to as `FOOTAGE:<relative path>` and resolved using `footage_root`. Renders go to `renders_dir`, which lives under `local/` and is git-ignored.

## 2. Folders

```
PROTOCOL.md  AGENTS.md  CLAUDE.md  MODELS.md
brief/                     film brief, three-app plan, stack, decisions, style.md (written by lead)
machines/registry.json     all machines and workers (lead edits)
machines/<machine>/        written ONLY by that machine's listener:
    heartbeat.json         time, idle/busy, current task, rate-limited-until
    capabilities.json      tools and versions, GPU, CPU, RAM, free disk (from tools/doctor.py)
    footage-manifest.json  every footage file: relative path, size, duration, sha256
queue/<worker-id>/<id>.md  task files. Written ONLY by claude-lead (or claude-second for tasks it owns)
results/<id>/              written ONLY by the assigned worker
    STARTED.json           written the moment the worker starts
    REPORT.md              written at the end: status done | failed | refused, what was made, notes
    ...outputs             code, small previews, stills
reviews/<id>.md            verdict from a foreman: accepted | redo (with notes) | dropped
discussion/<topic>/NNN-<author>.md   foreman-to-foreman notes, append-only, one file per message
film/                      the HyperFrames project. Only claude-lead writes here, or a task that explicitly lists film/ paths in `writes:`
tools/                     listener.py, doctor.py, manifest.py, statusline_usage.py, status.py, swarm_status.py (the banner the lead shows Vivek first)
log/                       lead's usage log and batch log
local/                     git-ignored: renders, logs, scratch, machine.local.json
```

## 3. Task file format

```markdown
---
id: T0042
title: Glass panel, still frames v1
worker: codex-f1
model: gpt-6-sol
effort: high
batch: 3
section: intro
needs_footage: false
inputs: [brief/style.md, brief/ps-text.txt]
writes: [results/T0042/]
depends_on: []
timeout_min: 60
created_by: claude-lead
created_at: 2026-09-30T10:00+05:30
redo_of: null
---
## Goal
One or two sentences on what this is and why it matters in the film.

## Details
Exact specs: sizes, timings, colours (always from brief/style.md), fonts, and the files to read.

## Done when
Checkable conditions, e.g. "results/T0042/still-2s.png shows the full problem statement, readable at 1080p".

## Never
Film rules that apply to this task.
```

Rules:
- `worker` decides who does it. Nobody else touches it. Only the lead reassigns, by writing a new task with `redo_of`.
- `writes` is the complete list of paths the worker may change. Default: `results/<id>/` only.
- `model` and `effort` are passed straight to the CLI by the listener.
- A task ID is never reused.

## 4. Life of a task

1. The foreman writes `queue/<worker>/<id>.md`, commits, and pushes.
2. The listener on that worker's machine pulls (every ~30 s) and sees a task with no `results/<id>/STARTED.json`.
3. The listener writes `STARTED.json`, pushes, then launches the worker CLI with the task's model and effort.
4. The worker does the job, writing only inside `writes`, and finishes by writing `REPORT.md`.
5. The listener checks sizes (§6), commits `results/<id>/`, and pushes with retries (`git pull --rebase`, then push; up to 5 tries).
6. The foreman pulls, reviews, and writes `reviews/<id>.md`. If the verdict is redo, it writes a NEW task with `redo_of: <id>` and the notes.

If the worker CLI exits without writing `REPORT.md`, the listener writes one itself with `status: failed`, including the last 50 lines of output.

File formats the listener reads (start each file with a short front-matter block):
- `results/<id>/REPORT.md` begins with `---`, `status: done` (or `failed` / `refused`), `---`, then free text.
- `reviews/<id>.md` begins with `---`, `verdict: accepted` (or `redo` / `dropped`), `---`, then notes. A task with `depends_on` only starts when every dependency has a REPORT `status: done` AND a review `verdict: accepted`.

## 5. Hard rules (the listener enforces the first three)

1. **Never run GPT-6 Astra.** Any task whose model contains "astra" is refused (REPORT status `refused`).
2. **One task at a time per worker.**
3. **No file over 20 MB is committed.** Big outputs stay in `local/renders/`, and REPORT.md gives the local path. Previews that are committed stay small: stills, or clips under 10 MB at 540p.
4. Workers never edit `queue/`, `reviews/`, `discussion/`, `brief/`, `machines/<other machine>/`, or `film/` unless `writes:` says so.
5. Never touch the iTantra app repo or its worktrees.
6. Never commit footage or audio source files. Footage is referenced, never copied into git.
7. All film rules in brief/decisions.md and brief/film-brief.md apply to every output.
8. If a task is unclear or impossible, finish with `status: failed` and explain why in REPORT.md. Do not guess at taste decisions.

## 6. Rendered video

Anything that goes into the actual film is rendered on vivek-pc (by `codex-vivek` or the lead) from code in git. Other machines send code plus small previews. If a heavy render really has to happen elsewhere, the result comes back through a shared Google Drive folder, and REPORT.md says exactly where.

## 7. Heartbeats, usage and failure handling

- Each listener rewrites `machines/<machine>/heartbeat.json` every 5 minutes, with status, current task, and `rate_limited_until` if the CLI reported a rate limit.
- **Claude usage (lead):** a status-line script writes Claude Code's `rate_limits.five_hour.used_percentage` and `rate_limits.seven_day.used_percentage` to `local/claude-usage.json`, and the lead reads that. If it's unavailable, the lead takes control of the screen, runs `/usage`, and reads a screenshot.
- **Codex usage:** if `codex exec --json` events include rate-limit info, the listener records it in the heartbeat. Otherwise it's handled reactively: a rate-limit error puts the worker in `rate_limited_until`, and the lead reallocates. On vivek-pc the lead can also open Codex, run `/status`, and read a screenshot.
- **Machine silent for more than 15 minutes** (stale heartbeat) with a queued task: the lead reassigns that task elsewhere.
- **Task past its `timeout_min`:** the listener kills it and reports `failed`.

## 8. Foreman-to-foreman

- The lead opens `discussion/<topic>/001-claude-lead.md` and queues a task for `claude-second` of type consult or review, pointing at that topic.
- The second foreman replies with `002-claude-second.md`, and so on. Files are never edited, only added.
- The lead decides. If it's a taste question the two foremen disagree on, it goes to Vivek.
- When the lead hands a whole section to the second foreman, the handover task says so. The second foreman may then write its own tasks into worker queues, but only with IDs prefixed `S` (e.g. `S0007`), and only for that section. It still reports back through `results/` and `discussion/`.
