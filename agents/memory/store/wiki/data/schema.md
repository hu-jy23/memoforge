# Wiki Schema Notes

Required frontmatter fields for every page:

- `title`
- `category`
- `sources`
- `last_updated`
- `confidence`

Allowed categories:

- `concepts`
- `api`
- `errors`
- `config`
- `workflows`

Optional metadata:

```yaml
freshness:
  checked_at: YYYY-MM-DD
  source_cutoff: YYYY-MM-DD
  version_scope: "..."
provenance:
  evidence_refs:
    - workspace/evidence/task-id/file.log
  task_refs:
    - task-id
```

Use optional metadata only when it adds real traceability.
