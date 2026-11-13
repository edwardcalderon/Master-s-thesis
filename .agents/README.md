# Project task workflow

This folder is the English-only working ledger for the CEX/DEX thesis repository.
Only the web app UI and final thesis PDF pair are required in English and Spanish.

## Statuses

- **TODO** — work not yet started and queued for later.
- **IN PROGRESS** — started work, including the current focus.
- **DONE** — acceptance criteria are met and the result is present in the repository.
- **BLOCKED** — work cannot proceed until a named dependency is resolved.

Mark the current priority with **CURRENT FOCUS** in the index; that task must be in
progress. Keep exactly one current focus. Every task needs an ID, owner, concrete
outcome, acceptance criteria, and dependencies. Update this ledger whenever status or
scope changes. Do not mark work DONE merely because a document describes it.

## Task folders

The status folders live under `tasks/`:

- `tasks/todo/` — queued work that has not started.
- `tasks/in-progress/` — started work; one may be marked CURRENT FOCUS.
- `tasks/done/` — completed work and its completion evidence.

Each task folder is named by its stable ID and contains `TASK.md`. `TASKS.md` is the
overview; the task file is the detailed record. Keep status in both locations
synchronized. To change a status, move the whole task folder to its new status folder,
update `TASK.md`, and then update the overview. A task moves to DONE only when its
acceptance criteria are met. Add a `tasks/blocked/` folder if a task actually becomes
blocked; include the blocking dependency in its record.

## Working loop

1. Read `TASKS.md`, open the task marked CURRENT FOCUS, and continue that task.
2. Work in a small, reviewable change that preserves unrelated working-tree edits.
3. Record the affected paths and evidence in the task entry. Do not claim tests or
   builds passed unless they were actually run.
4. When the current focus is done or blocked, record that evidence and assign the
   focus to an eligible in-progress task, or move a TODO task into progress first.
5. Follow `VERSIONING.md` for release and manuscript revisions. Task-status changes
   alone do not advance either version.

This is a repository-local tracker, not a separate issue system. The thesis MVP stays
the top priority; optional tooling such as plagiarism preflight must not displace
reproducible hypothesis experiments.
