# Skills Store

Layer 4 of the 5-layer memory system — Procedural Memory.

**What goes here**: reusable, domain-specific problem-solving patterns that have been validated by 2+ successful task outcomes. A skill is a recipe: given trigger condition X, do steps Y, achieving outcome Z.

**Who writes here**: Memory Agent only — during write-back, step 3 (skill promotion).

**Who reads here**: Coder and Verifier read skill files directly (no Memory Agent intermediary needed for reads). Planner may instruct agents to check `store/skills/` as a `context_ref`.

---

## File naming

`{skill-slug}.md` — use lowercase hyphenated slugs that describe the trigger or the technique, e.g.:

- `ascend-oom-incremental-offload.md`
- `mindformers-checkpoint-resume.md`
- `npu-dtype-cast-before-matmul.md`

---

## Skill file format

```markdown
---
title: Human-readable skill name
trigger: One sentence — the situation where this skill applies.
domain: mindspore | ascend | mindformers | general
first_seen: task_id of first successful occurrence
promoted_from: [task_id_1, task_id_2, ...]  # must have ≥2 entries
promoted_date: YYYY-MM-DD
confidence: high | medium
---

## Trigger condition

Describe precisely when to apply this skill. Be specific enough that an agent can decide "yes, this applies" or "no, it doesn't."

## Steps

Numbered, executable steps. Include code snippets with language tags where relevant.

1. Step one.
2. Step two.
   ```python
   # example
   ```

## Why it works

One paragraph explaining the domain-specific reason this pattern is effective. This is the memory — without it, the skill is just a recipe that might be misapplied.

## Known limitations

- Condition under which this skill does NOT apply.
- Edge cases or version constraints.

## Related wiki pages

- [[category/page-name]]
```

---

## Skill package format

Some skills should be packages, not single files. Use this structure when the skill needs references, scripts, validators, fixtures, or generated indices:

```text
skills/{skill-slug}/
  SKILL.md
  references/
  scripts/
  data/
  queries/
  README.md
```

Package rules:

- `SKILL.md` is still the entry point and trigger contract.
- `references/` stores deeper procedural or conceptual docs.
- `scripts/` stores deterministic helpers or validators.
- `data/` stores schema, aliases, freshness metadata, or source registries.
- `queries/` stores generated or curated indices.

Use package skills for high-value recurring workflows where a single prompt would become too long or too fragile.

---

## Schema, freshness, provenance, and validation

Support files:

- `data/schema.md`: required single-file and package formats
- `data/freshness.md`: version-scope and recency policy
- `data/provenance.md`: evidence requirements for promotion
- `queries/README.md`: planned navigation indices
- `scripts/validate_skills.py`: deterministic store validator
- `scripts/query_skills.py`: keyword search across promoted skills and potential skill candidates

Run:

```bash
python3 agents/memory/store/skills/scripts/validate_skills.py
python3 agents/memory/store/skills/scripts/query_skills.py "global norm" --source all
```

The validator accepts an empty skills store, but any promoted skill must satisfy the schema and cite at least two task IDs in `promoted_from`.

---

## Promotion criteria (for Memory Agent)

Before writing a skill file, verify all three:

1. **2+ successful occurrences**: search `store/learning/` for prior `.learning` entries with `Potential skill: yes` on similar patterns.
2. **Domain-specific**: the pattern requires knowledge that is specific to the target domain — it would not be obvious to an agent reasoning from general programming knowledge alone.
3. **Clear trigger**: the trigger condition can be stated in one sentence, unambiguously.

If only one occurrence has been observed, mark `Potential skill: yes` in the `.learning` entry and do not create the file yet.
