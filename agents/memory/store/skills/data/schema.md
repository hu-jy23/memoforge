# Skills Schema Notes

Skills are evidence-promoted procedural memory. A skill may be a single Markdown file or a package directory.

## Single-file skill

Required frontmatter:

- `title`
- `trigger`
- `domain`
- `first_seen`
- `promoted_from`
- `promoted_date`
- `confidence`

Required sections:

- `Trigger condition`
- `Steps`
- `Why it works`
- `Known limitations`
- `Related wiki pages`

## Package skill

Required structure:

```text
skills/{skill-slug}/
  SKILL.md
  README.md
  references/
  scripts/
  data/
  queries/
```

`SKILL.md` follows the same schema as a single-file skill. Package subdirectories are optional until used, but if present they must support the trigger contract rather than becoming unrelated notes.

## Promotion invariant

`promoted_from` must cite at least two successful task IDs. Candidate skills with one task remain in `learning/` as `Potential skill: yes`.
