# Acting-lead handoff for film v3 (claude-lead to claude-second)

Use only when claude-lead is near its usage limit. claude-second is acting lead until 13:40 IST, then claude-lead takes back over and reads `discussion/v3/` for what changed.

## Goal and rules
- Goal: `RENDERS:full_film_v3.mp4`, ~3:10, spec `discussion/v3/001-claude-lead.md` (text in its section 3 is final; any new on-screen text goes through the humanizer rules: no em dashes, no new claims or numbers).
- Vivek decides nothing mid-run: the acting lead makes design calls within the brief and pings Vivek (ntfy) only for "draft ready" or "truly blocked".
- Workers: codex-vivek (vivek-pc), codex-f1 (yash-pc), codex-f2 (utkarsh-pc, Codex rate-limited until 13:41, its laptop still renders), claude-second (you). Never use Yojith's Codex. Never render on Yojith's laptop.

## How to run the swarm as acting lead
- Task files: write `queue/<worker>/<id>.md` (or `queue/lane-video/<id>.md` with `worker: any`, `cli: codex`) with the PROTOCOL.md section 3 front matter; IDs prefixed `S` (S0101, S0102, ...). Reviews: `reviews/<id>.md` with `verdict: accepted|redo|dropped`. Redo = new ID with `redo_of`.
- Review every result from its preview stills at phone size (scale to 480 px wide). Two failed tries of the same job: skip it and note it.
- Keep the Codex workers busy: there should always be 1-2 ready pool tasks.

## State at handoff
See the latest lines of the lead's progress notes, summarised in the task that hands you this note. Open review/fix tasks are listed there.

## Renders and assembly
Renders are started by claude-lead over SSH on utkarsh-pc (a separate render clone). If claude-lead is away, do not try to render; prepare everything (fixed compositions, accepted reviews, updated `film/final/v3_segments.json`) so the lead can render and assemble the moment it is back.
