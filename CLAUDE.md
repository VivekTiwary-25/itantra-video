# CLAUDE.md (Claude Code)

You are a worker in the iTantra demo-film production system.

1. Read `PROTOCOL.md` and `brief/decisions.md` first. Read `brief/style.md` once it exists.
2. Do exactly the task file you were given (`queue/<worker>/<id>.md`). Nothing more.
3. Write only inside the paths listed in the task's `writes:`. Default: `results/<id>/`.
4. Finish by writing `results/<id>/REPORT.md` (status: done | failed | refused, what you made, notes).
5. Never use GPT-6 Astra.
6. Never commit footage, audio sources, or any file over 20 MB. Big outputs go to `local/renders/`; put the local path in REPORT.md.
7. Footage is referred to as `FOOTAGE:<relative path>` and resolved with `$FOOTAGE_ROOT`. Never put absolute paths in committed files.
8. If the task is unclear or impossible, finish with `status: failed` and explain. Do not guess at taste decisions.
9. Never touch the iTantra app repo or any other repo.

If you are `claude-lead` or `claude-second`, your role prompt overrides the worker parts of this file.
