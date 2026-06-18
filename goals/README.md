# goals/

Persistent long-horizon goal state for MemoForge.

Use this directory for `/goal` and Alignment Starter artifacts that must survive multiple task cycles.

## Layout

| Path | Purpose |
|---|---|
| `active/plan.md` | Current aligned plan, primarily authored by the user and polished through MultiAlignment |
| `active/alignment_questions.md` | Unknowns, answers, omitted defaults, and confirmation QA |
| `active/goal_contract.md` | Stable long-horizon goal contract |
| `active/status.json` | Machine-readable goal state |
| `active/progress.md` | Append-only progress log |
| `archive/` | Completed or abandoned goal directories |

## Rules

- Keep goal-level state here, not only in `workspace/`.
- Keep task-cycle artifacts in `workspace/`.
- Do not mark a goal complete without evidence satisfying `active/goal_contract.md`.
- Do not mark a goal blocked unless the blocker is repeated and no meaningful progress is possible without user input or external-state change.
