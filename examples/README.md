# Examples

This directory contains optional demonstration artifacts. They are not required
to run MemoForge.

## `custom-callback-norm-lr-01/`

An audited task-cycle example copied from the research workspace.

It demonstrates the task artifact protocol:

```text
task_contract.md
  -> plan.json
  -> candidates.jsonl
  -> patch/
  -> evidence/
  -> verify_result.json
  -> promotion_decision.md
```

Why keep it in the public release:

- It shows what a completed task cycle looks like.
- It gives readers a concrete artifact chain instead of only abstract docs.
- It can be used as a reference when implementing a new task cycle.

Why it is optional:

- It is domain-specific.
- It is not loaded by the harness runtime.
- It can be deleted without breaking the core framework.
