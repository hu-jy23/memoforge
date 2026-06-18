# Notes Store

Layer 5b of the memory system — thematic working notes, the staging area between task observations and authoritative wiki.

**What goes here**: domain facts grouped by topic, extracted from task cycles. Flexible, editable, and explicitly confidence-stratified. Notes are the *pre-wiki* — they hold observations that are real but not yet stable enough to commit to wiki.

**Who writes here**: Memory Agent only — during write-back Step 4.

**Who reads here**: Coder and Verifier (after wiki, with lower confidence weight). Memory Agent during query and consolidation modes.

**Relationship to other layers**:

```
learning/{task_id}.md   ← what happened (task-centric, immutable)
notes/{topic}.md        ← what we know (topic-centric, mutable)  ← YOU ARE HERE
wiki/{cat}/{page}.md    ← what is authoritative (slow, deliberate)
```

---

## File naming

One file per domain topic: `{topic-slug}.md`

Use the same naming convention as the corresponding wiki page would use. Examples:
- `mf-train-wrappers.md`
- `parallel-config.md`
- `ascend-device-context.md`
- `lora-finetuning.md`

---

## Page format

No frontmatter required. Use this three-section structure:

```markdown
# notes/{topic-slug}.md
_Last updated: YYYY-MM-DD_

## Confirmed

Facts seen in 2+ independent task cycles. These are consolidation candidates.

- {fact statement}
  Sources: {task_id_1} (YYYY-MM-DD), {task_id_2} (YYYY-MM-DD)

## Observed Once

Facts seen in exactly one task. Real but not yet verified by a second occurrence.

- {fact statement}
  Source: {task_id} (YYYY-MM-DD)

## Uncertain / Conflicting

Observations that contradict each other, or where the source is unclear.

- {fact A} — conflicts with {fact B}
  Sources: {task_id_1}, {task_id_2}
  Status: unresolved — needs more evidence
```

---

## Confidence semantics

| Section | Meaning | Wiki-ready? |
|---|---|---|
| `## Confirmed` | 2+ independent tasks agree | Yes — consolidation candidate |
| `## Observed Once` | Single observation, plausible | Not yet — wait for second confirmation |
| `## Uncertain / Conflicting` | Contradictory evidence | No — needs investigation |

---

## Write rules (for Memory Agent)

1. **On first observation of a fact**: add to `## Observed Once` with source task_id and date.
2. **On second confirmation of same fact**: move it from `## Observed Once` to `## Confirmed`, append the second source. This triggers the consolidation-ready signal.
3. **On contradiction**: move to `## Uncertain / Conflicting`, note both conflicting sources and what they claim.
4. **Never delete `## Observed Once` entries** — they become evidence when a second task confirms them.

---

## Read rules (for Coder and Verifier)

- Prefer wiki over notes. Notes are fresher but less authoritative.
- When acting on a notes fact, treat it as `confidence: medium` regardless of which section it is in.
- When citing notes in `coder_summary.md` or `verify_result.json`, mark it: `[notes/topic — unconfirmed]`.
- If a notes entry contradicts a wiki page, trust the wiki (it has been through consolidation). Flag the contradiction in your summary so Memory Agent can investigate.

---

## Consolidation

The Memory Agent promotes `## Confirmed` entries to wiki during consolidation mode. After promotion, the entry moves to a `## Consolidated` section (or is deleted). `## Observed Once` and `## Uncertain` entries remain until further evidence arrives.

Consolidation is triggered by: user request, Planner prompt, or weekly schedule. It is NOT automatic after every write-back.
