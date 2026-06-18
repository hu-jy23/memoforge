# Session Context Architecture

This document defines the short-term context model for MemoForge. It is orthogonal to persistent project memory.

## Three Context Regions

### Immutable Prefix

The immutable prefix is the stable context assembled at session launch.

Typical contents:

- agent role prompt
- tool specifications
- fixed few-shot examples, if any
- deterministic project status and routing context
- selected project-memory indexes

Rules:

- Keep it stable inside a session.
- Keep it small enough to route into deeper files.
- Do not inject full wiki, notes, learning, or skills by default.

Human analogy: prior knowledge before the conversation starts.

### Append-only Log

The append-only log is the trace accumulated during a session.

Typical contents:

- user requests
- assistant messages
- tool calls
- tool results
- accepted summaries of prior actions

Rules:

- Append in order.
- Do not reorder old entries.
- Compact only through explicit summaries that preserve evidence references.

Human analogy: posterior context formed during the conversation.

### Volatile Scratch

Volatile scratch is temporary reasoning state.

Typical contents:

- local hypotheses
- draft plans
- intermediate notes
- failed partial thoughts

Rules:

- Do not persist by default.
- Promote only through explicit artifacts: plan, candidate ledger, evidence, learning, notes, wiki, or skills.
- Treat scratch as unverified until it is tied to evidence.

Human analogy: working thoughts in the agent's head.

## Relationship To Project Memory

Persistent project memory is cross-task:

- wiki: stable long-term facts
- notes: mid-term thematic observations
- learning: per-task evidence-backed records
- skills: validated procedural memory

Session context is per-session:

- immutable prefix
- append-only log
- volatile scratch

The harness should define both. Project memory answers what the system has learned across tasks. Session context controls what enters the current model call and how it evolves.

## Implementation Guidance

- `context/prefix_manifest.json` is the deterministic source list for immutable prefix assembly.
- `tools/compile_project_context.py` compiles profile-specific prefixes and validates referenced files.
- `CLAUDE.md` and `PROJECT_STATUS.md` are source files for the immutable prefix.
- `workspace/` files are task-cycle artifacts and may be referenced from the append-only log.
- Temporary exploration should stay in scratch unless it becomes a named artifact.
- Memory Agent is the only writer to persistent memory; scratch cannot bypass write-back.

## Profile Boundaries

The prefix compiler supports separate profiles for each main agent:

- `planner`: role contract plus stable project status and protocol docs. It does not include direct memory-store files.
- `coder`: Coder prompt plus stable protocol docs, wiki index, and skill format.
- `verifier`: Verifier prompt plus stable protocol docs, wiki index, and learning format.
- `memory`: Memory prompt plus stable protocol docs and persistent memory schema docs.

Task-specific files are not compiled into the immutable prefix. They remain explicit `context_refs` in the append-only task flow.
