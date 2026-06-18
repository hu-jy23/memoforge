# Wiki Schema and Conventions

This file is read by the Memory Agent and the Starter Agent before touching any wiki content. Follow these conventions exactly — consistency is what makes the wiki queryable across agent boundaries.

## Directory structure

```
wiki/
  CLAUDE.md          # This file — schema reference
  index.md           # Master directory: one line per page
  log.md             # Append-only operation log
  data/               # Schema notes, freshness policy, provenance conventions
  queries/            # Generated or curated cross-reference indices
  scripts/            # Query and validation helpers
  concepts/          # Domain terminology, hardware abstractions, model architecture facts
  api/               # API signatures, parameter semantics, known behavioral quirks
  errors/            # Known error patterns and their resolutions
  config/            # Environment setup, install notes, runtime flags, path conventions
  workflows/         # Multi-step procedures and proven patterns
```

Each subdirectory maps to a memory category. When creating a new page, choose the most specific matching category. Use `concepts/` as the default if no other category fits.

## Page format

Every wiki page is a Markdown file with a YAML frontmatter block followed by the body.

### Frontmatter

```yaml
---
title: Human-readable page title
category: concepts | api | errors | config | workflows
sources:
  - short description of source (e.g. "MindFormers docs v2.1 §3.4", "observed in task fix-attn-01")
last_updated: YYYY-MM-DD
confidence: high | medium | low
---
```

`confidence` semantics:
- `high` — confirmed by official docs or 2+ independent task observations
- `medium` — observed once, or inferred from behavior
- `low` — tentative; contradicts another source, or derived from indirect evidence

Optional KDA-inspired metadata:

```yaml
freshness:
  checked_at: YYYY-MM-DD
  source_cutoff: YYYY-MM-DD
  version_scope: "MindFormers 0.8.x-1.x"
provenance:
  evidence_refs:
    - workspace/evidence/task-id/test.log
  task_refs:
    - task-id
```

Use optional metadata when a page depends on fast-moving docs, a version-sensitive API, or task evidence. Do not add empty metadata blocks.

### Body conventions

- **First paragraph**: one-sentence definition or summary of the page topic. This sentence is used verbatim in `index.md`.
- **Sections**: use `##` headings for major sections, `###` for subsections.
- **Code blocks**: always specify language tag (` ```python `, ` ```bash `, ` ```text `).
- **Cross-references**: use wikilink syntax `[[page-name]]` (page-name = filename without `.md`, relative to `wiki/`). Example: `[[api/mindformers_attention]]`.
- **Do not fabricate**: if a fact is uncertain, mark it with `> **Note (low confidence):**` blockquote before the claim.

### Contradiction handling

When a new observation contradicts an existing page:

1. Lower `confidence` to `low` (or `medium` if the contradiction is partial).
2. Add a `## Superseded / Conflicting Information` section at the bottom:
   ```
   ## Superseded / Conflicting Information

   As of YYYY-MM-DD (task_id: `{task_id}`): prior claim "[quoted old claim]" appears incorrect. New observation: [new fact]. Source: [source].
   ```
3. Append a contradiction entry to `log.md`:
   ```
   ## [YYYY-MM-DD] contradiction | page={page-name} task_id={task_id} — [one-line description]
   ```

## index.md format

`index.md` is a flat list of all wiki pages, grouped by category. Each page gets exactly one line:

```
- [[category/page-name]] — One-sentence summary (mirrors the page's first-paragraph sentence).
```

Group entries under category headings:

```markdown
## Concepts
- [[concepts/npu-memory-model]] — ...

## API
- [[api/mindformers_trainer]] — ...

## Errors
- [[errors/ascend-oom]] — ...

## Config
- [[config/mindspore-install]] — ...

## Workflows
- [[workflows/finetune-pipeline]] — ...
```

When adding a new page: insert its entry under the correct category heading, maintaining alphabetical order within each group.

When removing a page (rare): remove its line and append a `## [date] deleted` entry to `log.md`.

## log.md format

`log.md` is an **append-only** file. Never edit or delete existing lines. Each entry is a level-2 heading followed by a single line:

```
## [YYYY-MM-DD] {operation} | {description}
```

Operation tokens (use exactly these strings):

| Token | Meaning |
|-------|---------|
| `init` | Wiki or a major subsystem was initialized |
| `write-back` | Memory Agent completed a write-back cycle |
| `create` | New wiki page created |
| `update` | Existing wiki page updated |
| `delete` | Wiki page deleted |
| `skill-promoted` | A pattern was promoted to `store/skills/` |
| `contradiction` | A contradiction between sources was detected |
| `gap` | A query found no matching wiki page |
| `orphan` | An orphan page was detected |

Full entry examples:

```
## [2026-05-17] init | wiki initialized by Starter Agent
## [2026-05-18] create | page=errors/ascend-oom task_id=fix-oom-01
## [2026-05-18] write-back | task_id=fix-oom-01 status=fail steps=1,2,5
## [2026-05-19] skill-promoted | skill=ascend-memory-flush trigger="OOM on Ascend 910"
## [2026-05-19] contradiction | page=api/mindformers_trainer task_id=train-01 — param lr_scale removed in v2.1
## [2026-05-20] gap | query="npu kernel fusion config" — no page found
```

## Wikilink convention

- Syntax: `[[category/page-name]]` — always include category prefix.
- The link text is the filename without `.md`, relative to `wiki/`.
- When referencing a page outside its own category, always use the full `category/page-name` form.
- Renderers (human readers, agents) resolve wikilinks by looking up `wiki/{category}/{page-name}.md`.
- Broken wikilinks (target does not exist) should be flagged in `log.md` as `orphan` entries when discovered.

## Quality rules

1. **Cite sources** — every frontmatter `sources` list must be non-empty. Inline claims that come from a specific task should note the task_id.
2. **Cross-reference** — if a page mentions a concept that has its own wiki page, link it with `[[...]]`.
3. **No orphan pages** — every page must appear in `index.md`. After creating a page, immediately add its `index.md` entry.
4. **No stale summaries** — when updating a page's first paragraph, also update its line in `index.md`.
5. **Contradiction transparency** — never silently overwrite a claim. Always follow the contradiction handling procedure above.
6. **One fact per page** — prefer narrow focused pages over broad catch-all pages. Split if a page exceeds ~150 lines.

## Query and validation helpers

- `scripts/query_wiki.py` performs lightweight keyword search across wiki pages.
- `scripts/validate_wiki.py` checks required frontmatter fields, index references, and orphan pages.
- `queries/` may contain generated or curated cross-reference indices, such as by API, workflow, error, config, or version.
- `data/` stores schema notes, freshness policy, provenance conventions, aliases, and future controlled vocabulary.

Run validation after Starter Agent generation, manual wiki edits, consolidation, or large write-back batches.
