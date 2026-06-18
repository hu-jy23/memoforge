# Provenance Policy

Every wiki page must have `sources`.

Use provenance metadata when a claim is derived from task-cycle evidence:

```yaml
provenance:
  evidence_refs:
    - workspace/evidence/task-id/test.log
  task_refs:
    - task-id
```

Do not cite ephemeral evidence as the only support for `confidence: high` unless it is backed by 2+ independent task observations or an official source.
