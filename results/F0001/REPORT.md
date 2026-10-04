---
status: done
---
# F0001: idle watcher

## Made
- `tools/idle_watcher.py` (Python 3.12, stdlib only)
- `tools/install-idle-watcher.ps1`
- `results/F0001/sample-status.md`: a single pass on this clone.

## Install command for the lead (on vivek-pc)
Run it from the lead folder. The watch clone goes beside it.

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools\install-idle-watcher.ps1 -Repo . -Clone ..\itantra-watch
```

What the command does:
- Clones the lead folder's `origin` URL into `..\itantra-watch` if that folder is missing.
- Creates `local\watcher-active`.
- Registers the hidden Scheduled Task `itantra-idle-watcher` for the current user. It triggers at logon, has no time limit, and restarts 3 times, 1 minute apart. It runs `pythonw.exe` from next to `python` on PATH with `--loop --clone <clone> --out <Repo>\local\worker-status.md --active-flag <Repo>\local\watcher-active`.
- Starts the task.

`-ExecutionPolicy Bypass` only applies to that one process; it does not change the machine's policy. If the policy already allows local scripts, drop it.

Other commands:
- **Remove:** `powershell -NoProfile -ExecutionPolicy Bypass -File tools\install-idle-watcher.ps1 -Uninstall`
- **Check ntfy:** `python tools\idle_watcher.py --test-ping`. It reads the `Ntfy Topic` variable from the environment, then from `HKCU\Environment`. If neither is set, it logs and sends nothing.

## Behaviour
- **Each pass** (every 120 s by default):
  - `git pull --ff-only -q` on the clone. A pull error is logged and the old state is kept.
  - Reads the registry, the heartbeats (one per machine, mapped to workers through the registry), every `queue/*` folder, STARTED/REPORT files and reviews.
- **Ready** follows PROTOCOL §4: no STARTED and no REPORT, not dropped, and every dependency has REPORT done plus review accepted.
- **Running** means STARTED without REPORT.
- **Pool tasks** respect `cli:`, `machine:` and `worker:`, the same as `listener.runnable()`.
- **Workers listed:** those with `queue: true`, except `codex-yojitth`.
- **Alerts:**
  - idle for more than 10 min while the active flag exists, or while a task this worker could take is ready
  - machine heartbeat older than 15 min (or missing)
- **Pings:** one per alert episode, repeated after 30 min if the alert is still true. Topic and message reach PowerShell only through the child's environment (`T`, `B`).
- **Files:**
  - Output is written atomically.
  - State goes to `<out>.state.json`; on first run, "since" is the heartbeat time.
  - Every exception goes to `<out>.log`, which rotates once at 1 MB, so the loop never crashes.
- **Extra flag:** `--no-pull`, for testing on a working clone. I used it so I would not pull inside my listener's clone.

## Tested
- **This clone:** a single pass with `--no-ntfy --no-pull` produced `sample-status.md`. It is correct against the queue: the pool count is 1 for claude-second and 6 for the codex workers, because five of the six ready video tasks are `cli: codex`.
- **Fake clone under `local/tmp`:**
  - an idle worker with an own task gave an idle alert
  - two old heartbeats gave stale alerts
  - a dependency became ready once its review was set to accepted
  - a claude-only pool task was not counted for codex workers
  - codex-yojitth was skipped
  - a second pass inside 30 min sent no repeat ping
- **Installer:** both scripts pass a syntax check, and `-Uninstall` runs.
- **Not tested here:** a real ntfy send (there is no internet in the sandbox) and registering the Scheduled Task. The lead does both on vivek-pc.
