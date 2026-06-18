# Task Artifact Protocol

This protocol defines the evidence chain for a MemoForge task cycle.

## Goal

A task is complete only when the harness can answer four questions:

- What was the task contract?
- Which candidates were tried?
- What evidence supports the result?
- What should be promoted into project memory?

## Runtime Files

All runtime files live in `workspace/` and are safe to delete between task cycles.

| Path | Writer | Purpose |
|---|---|---|
| `workspace/task_contract.md` | Coder on Planner instruction | Formal task objective, constraints, validation command, and promotion criteria |
| `workspace/plan.json` | Coder on Planner instruction | Subtasks, dependencies, and context refs |
| `workspace/candidates.jsonl` | Coder and Verifier append entries | Candidate implementation ledger |
| `workspace/patch/{task_id}/` | Coder | Patch files for the named candidate/task |
| `workspace/coder_summary.md` | Coder | What changed, why, sources used, open questions |
| `workspace/evidence/{task_id}/` | Verifier | Logs, command output, benchmark/profile summaries, screenshots, or other proof |
| `workspace/verify_result.json` | Verifier | Structured validation verdict |
| `workspace/promotion_decision.md` | Verifier | Candidate acceptance and memory-promotion recommendation |

## Executable Gate

Run the protocol validator after Verifier writes `verify_result.json` and `promotion_decision.md`:

```bash
python3 tools/validate_task_artifacts.py --require-learning
```

Use `--require-learning` after Memory Agent write-back. Omit it when validating the pre-write-back workspace state.

The validator checks:

- required artifact files exist
- `task_contract.md` and `promotion_decision.md` contain required sections
- `plan.json` is valid JSON and has consistent subtask dependencies
- `candidates.jsonl` is parseable JSONL with valid role/status values
- candidate artifact and evidence refs exist
- `verify_result.json` cites a candidate and concrete evidence
- pass verdicts have matching Verifier pass ledger entries
- learning records cite the task contract, candidate ledger, evidence, verify result, and promotion decision when `--require-learning` is set

For an isolated end-to-end protocol smoke test, run:

```bash
python3 tools/run_task_cycle_smoke.py
```

The smoke test builds a temporary task cycle from scratch, runs a real syntax validation command, writes candidate/evidence/verification/promotion/learning artifacts, and validates them with `tools/validate_task_artifacts.py --require-learning`.

## Artifact Semantics

### task_contract.md

Defines what success means.

Required sections:

- Objective
- Inputs / outputs
- Constraints
- Validation command
- Evaluation command, if separate
- Promotion criteria
- Out-of-scope items

### candidates.jsonl

Append-only ledger. One JSON object per event.

Required fields:

```json
{"candidate_id":"...","task_id":"...","parent_id":null,"role":"coder|verifier","status":"proposed|implemented|pass|fail|partial|rejected|promoted","summary":"...","artifact_refs":["..."],"evidence_refs":["..."],"timestamp":"YYYY-MM-DD"}
```

The Coder records proposed and implemented candidates. The Verifier records validation outcomes.

### evidence/{task_id}/

Stores proof, not conclusions.

Examples:

- `commands.log`
- `pytest.log`
- `benchmark.csv`
- `profile-summary.md`
- `manual-inspection.md`

Evidence should be referenced from `verify_result.json`, `promotion_decision.md`, and the final learning entry.

### promotion_decision.md

States what to do with the result.

Required sections:

- Candidate decision: accept, revise, reject
- Evidence summary
- Memory write-back recommendation
- Skill promotion recommendation
- Wiki / notes update recommendation
- Residual risks

## Relationship To Learning

`agents/memory/store/learning/{task_id}.md` is the persistent learning record derived from these workspace artifacts.

The learning entry should cite:

- `workspace/task_contract.md`
- relevant `workspace/candidates.jsonl` candidate IDs
- `workspace/evidence/{task_id}/`
- `workspace/verify_result.json`
- `workspace/promotion_decision.md`

This turns `.learning` from an event log into an evidence-backed learning record.

## Promotion Rule

No fact, pattern, or skill should be promoted solely because the task completed. Promotion requires:

- a clear trigger condition
- validation evidence
- domain-specific value
- a destination layer: notes, wiki, or skills

Single observations go to notes as `Observed Once`. Repeated or independently verified observations may become `Confirmed` notes or wiki updates. Repeated successful procedural patterns may become skills.
