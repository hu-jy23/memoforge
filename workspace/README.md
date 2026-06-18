# workspace/

Ephemeral runtime artifacts for the current task cycle. Safe to delete between cycles. Do not store anything here that needs to persist — use `agents/memory/store/` for that.

Long-horizon goal state is also persistent. Store it in `goals/active/`, not in `workspace/`.

## Standard files

| Path | Written by | Contents |
|---|---|---|
| `task_contract.md` | Coder (on Planner instruction) | Objective, constraints, validation command, promotion criteria |
| `plan.json` | Coder (on Planner instruction) | Task decomposition: subtasks, dependencies, context_refs |
| `candidates.jsonl` | Coder + Verifier | Append-only candidate implementation and validation ledger |
| `patch/{task_id}/` | Coder | Output patch files for the named task |
| `coder_summary.md` | Coder | Brief of what changed and why |
| `evidence/{task_id}/` | Verifier | Logs, command output, benchmark/profile summaries, manual inspection notes |
| `verify_result.json` | Verifier | Structured validation verdict with evidence refs |
| `promotion_decision.md` | Verifier | Candidate acceptance and memory-promotion recommendation |

## Protocol validation

Run this after Verifier writes the standard files:

```bash
python3 tools/validate_task_artifacts.py
```

Run this after Memory Agent write-back:

```bash
python3 tools/validate_task_artifacts.py --require-learning
```

Run an isolated protocol smoke test:

```bash
python3 tools/run_task_cycle_smoke.py
```

## Notes

- Files here are overwritten each task cycle. Do not treat them as history.
- `patch/` subdirectories are keyed by `task_id` so concurrent tasks do not collide.
- `evidence/` is still ephemeral. Memory Agent should cite useful evidence in `learning/` before the workspace is cleared.
- Persistent memory (wiki, skills, learnings, preferences) lives in `agents/memory/store/` — never here.
