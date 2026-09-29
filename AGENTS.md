# AGENTS.md (Codex workers)

You are a worker in the iTantra demo-film production system.

1. Read `PROTOCOL.md` and `brief/decisions.md` first. Read `brief/style.md` once it exists.
2. Do exactly the task file you were given (`queue/<worker>/<id>.md`). Nothing more.
3. Write only inside the paths listed in the task's `writes:`. Default: `results/<id>/`.
4. Finish by writing `results/<id>/REPORT.md` (status: done | failed | refused, what you made, notes).
5. Never use GPT-6 Astra.
6. Never commit footage, audio sources, or any file over 20 MB. Big outputs go to `local/renders/`; refer to them in REPORT.md as `RENDERS:<relative path>` (never an absolute path: this repo is public).
7. Footage is referred to as `FOOTAGE:Video/<name>` or `FOOTAGE:Audio/<name>` (original file names) and resolved with `$FOOTAGE_ROOT`. Never put absolute paths in committed files.
8. If the task is unclear or impossible, finish with `status: failed` and explain. Do not guess at taste decisions.
9. Never touch the iTantra app repo or any other repo.
