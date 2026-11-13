# Task workspace

Task folders are grouped by their current status. The stable task ID stays the same
when a folder moves. See [the task index](../TASKS.md) before changing folders.

```text
tasks/
├── todo/         # queued, not started
├── in-progress/  # started; one may be the current focus
└── done/         # acceptance criteria met, with evidence recorded
```

Each task folder contains one `TASK.md` with its owner, status, goal, acceptance
criteria, dependencies, progress notes, and next action. Folder location and the status
in `TASK.md` and `TASKS.md` must agree. `TASKS.md` marks the one current focus; focus is
not a separate status. All internal task records are English-only.
