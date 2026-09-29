# iTantra video production system — start here

## What's in this pack
- `SETUP_SPEC.md`: instructions for the setup builder (Sonnet).
- `PROTOCOL.md`: the rulebook every agent follows. Covers folders, task files, who writes what, the Astra ban, and failure handling.
- `MODELS.md`: which models to use for what, the exact command-line options, and the usage rules.
- `brief/`: the film brief, the plan for the three app builds, the production stack, and everything we've decided so far.
- `prompts/`: one startup prompt for each agent.

## Order of steps

1. **GitHub invites.** Invite all three friends as collaborators on the private `VivekTiwary-25/itantra-video` repo (NOT the iTantra app repo). Each friend accepts.
2. **Setup builder on your PC.** Unzip this pack, open Claude Code in that folder with `claude --model sonnet --effort high`, and paste `prompts/1-setup-builder-sonnet.md`. It sets up the repo, the tools and your listener, then writes a filled-in bootstrap prompt for each friend.
3. **Friends' machines.** Send each friend their filled-in bootstrap prompt:
   - yash and utkarsh paste it into Codex.
   - yojitth pastes it into Claude Code.
   Each machine then unzips its footage, checks its tools and starts its listener.
4. **Second foreman.** On yojitth's PC, start `claude-second` with `prompts/3-second-foreman-opus.md`. The setup builder will say exactly when.
5. **Tests.** The setup builder runs the round-trip tests and writes `log/setup-report.md`.
6. **Lead foreman.** In the video repo folder on your PC, open `claude --model opus --effort high --permission-mode auto` and paste `prompts/2-lead-foreman-opus.md`. It checks in with you before starting any film work.

**Keep every PC awake** (Windows power settings: never sleep while plugged in), and leave the listener terminals open.

## Things only you can provide
- Nothing repo-related: the repo is `VivekTiwary-25/itantra-video`, cloned at `D:projectssihPresentationideo`.
- Where the footage zips are on each machine.
- The machine names, if you want to change `vivek-pc`, `yash-pc`, `utkarsh-pc`, `yojitth-pc` (they must match everywhere).
- For the film later: the team ID, the exact problem-statement text, music (if any), and the deadline.
