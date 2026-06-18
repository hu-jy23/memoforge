# Skills Freshness Policy

Use freshness metadata when a skill depends on version-sensitive behavior: framework APIs, hardware runtime, compiler flags, distributed training layout, or undocumented output structure.

Recommended optional frontmatter:

```yaml
freshness:
  checked_at: YYYY-MM-DD
  source_cutoff: YYYY-MM-DD
  version_scope: "..."
```

If freshness metadata is absent, treat `promoted_date`, `promoted_from`, and linked wiki pages as the only recency signals.

Refresh or demote a skill when:

- a linked wiki page is superseded
- a validation task contradicts the trigger or steps
- the version scope no longer matches the target environment
