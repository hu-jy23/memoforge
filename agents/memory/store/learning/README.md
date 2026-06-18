# Learning Store

Layer 5 of the 5-layer memory system — `.learning` write-back entries.

**What goes here**: one file per task cycle, recording what happened, what evidence supports the outcome, and whether the outcome suggests notes/wiki/skill promotion. This is the persistent evidence-backed learning layer — wiki updates and skill promotions are derived from it.

**Who writes here**: Memory Agent only — during write-back, step 1 (always executed).

**Who reads here**: Memory Agent (to check prior occurrences before promoting a skill, and when the Planner queries for past failures similar to a current failure). Planner may pass specific learning files as `context_refs` to Coder during recovery.

---

## File naming

One file per task cycle: `{task_id}.md`

If a task is retried (Coder re-spawned after Verifier fail), do not create a new file — append a new dated section to the existing `{task_id}.md`.

---

## Entry format

```markdown
## {task_id} | {YYYY-MM-DD} | {pass|partial|fail}

**Summary**: One paragraph. What did the task attempt? What was the approach? What happened?

**Task contract**: Cite `workspace/task_contract.md` and summarize the objective / validation command.

**Candidate evidence**: Cite candidate IDs from `workspace/candidates.jsonl` and evidence files under `workspace/evidence/{task_id}/`.

**Outcome**: pass, partial, or fail.
If fail — paste `findings` and `suggested_fix` from `verify_result.json` verbatim here.

**Promotion decision**: Cite `workspace/promotion_decision.md`. State whether the result should update notes, wiki, or skills.

**Domain facts**: Bullet list of concrete domain-specific observations made during this task.
- Fact 1 (e.g., "MindFormers v2.1 Trainer no longer accepts `lr_scale` param")
- Fact 2 (e.g., "Ascend 910B raises `CANN RuntimeError: 707003` when batch_size > 32 with bf16")

**Potential skill**: yes | no
If yes — one sentence describing the pattern (this is used by Memory Agent when scanning for skill promotion eligibility).
```

---

## Retry convention

When a task is retried, append a new section to the same file:

```markdown
---

## {task_id} | {YYYY-MM-DD} | retry-{n} | {pass|partial|fail}

(same format as above)
```

Use `retry-1`, `retry-2`, etc. for subsequent attempts.

---

## Searching for prior patterns

When Memory Agent scans for skill promotion eligibility (step 3 of write-back), it reads all `.md` files in this directory and looks for entries with `Potential skill: yes` that describe a similar pattern. "Similar" means: same domain subsystem, same trigger condition, same type of fix. Use judgment — exact string match is not required.

Do not promote from learning alone. A skill promotion also needs cited validation evidence and a promotion decision that accepts the candidate or explicitly recommends skill consideration.
