# Vivek directive â€” ramp healthy swarm utilization

This is an operations-only instruction.

Use every healthy available worker whenever useful current work exists. Do not leave a healthy worker idle while independent useful work is waiting.

## Rules

- Check current shared heartbeat/task state before assigning.
- Parallelize aggressively, but keep worker writes non-overlapping.
- Do not duplicate already-running work.
- Do not invent junk work merely to make utilization look high.
- If a worker has persistent Git synchronization failures, exhausts retries, becomes stale, disappears, or repeatedly fails tasks, record the problem and reassign useful work instead of silently waiting.
- A transient push retry that later succeeds is not by itself a failure.
- Keep claude-second as the single acting foreman/integrator for work it delegates.
- Review completed worker results and issue redo/reassignment when needed.
- Do not kill or restart listeners simply to deliver instructions.

## Hard boundary

DO NOT begin, plan, inspect, delegate, or modify Scene 3.

Scene 3 will arrive later as a separate explicit instruction from Vivek.
