# Skills Scripts

Deterministic helpers for the skills store.

Current helper:

```bash
python3 agents/memory/store/skills/scripts/validate_skills.py
python3 agents/memory/store/skills/scripts/query_skills.py "learning rate"
```

`validate_skills.py` checks support scaffolding, single-file skills, package skills, required frontmatter, required sections, and promotion evidence counts.

`query_skills.py` searches promoted skills and potential skill candidates in `learning/`.
