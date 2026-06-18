# Skills Provenance Policy

Every promoted skill must cite the task evidence that justified promotion.

Required provenance:

- `first_seen`: first task where the pattern appeared
- `promoted_from`: at least two successful task IDs
- `Related wiki pages`: stable context needed to apply the skill safely

Recommended optional frontmatter:

```yaml
provenance:
  evidence_refs:
    - workspace/evidence/task-id/file.log
  learning_refs:
    - agents/memory/store/learning/task-id.md
```

Do not promote a skill from a single task, a failed candidate, or a pattern that lacks a clear trigger condition.
