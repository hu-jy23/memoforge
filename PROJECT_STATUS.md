# MemoForge Project Status

## Purpose

MemoForge is a research-grade agent harness. It tests how a complex engineering environment can be compiled into a usable agent substrate: root context, task artifacts, wiki, notes, learning records, skills, verification evidence, and controlled multi-agent roles.

The current direction is broader than the original domain-specific framing: MemoForge is a general long-horizon agent harness with domain memory as a configurable layer.

## Current Architecture

The harness keeps four main agents:

- Planner: user-facing router and task-cycle owner.
- Coder: patch author and candidate recorder.
- Verifier: validation owner and evidence recorder.
- Memory Agent: sole writer to persistent project memory.

Lightweight subagents may be used inside any main agent for local exploration, parallel reads, validation fan-out, or memory consolidation. They are local helpers, not new top-level roles.

Every Planner interaction starts with Alignment Starter. Explicit `/goal ...` commands add persistent goal control. These are Planner capabilities and starter protocols, not new top-level agents.

## Project Memory

Project memory is the full persistent store, not a single file:

- `agents/memory/store/wiki/`: stable long-term domain and repo memory.
- `agents/memory/store/notes/`: mid-term thematic observations awaiting consolidation.
- `agents/memory/store/learning/`: evidence-backed per-task learning records.
- `agents/memory/store/skills/`: validated procedural memory promoted from repeated successful evidence.
- `agents/memory/store/preferences.md`: user preference memory.

Long-horizon goal state lives in `goals/active/`. It is persistent project state, but it is not memory-store content. Use it for the current aligned plan, goal contract, status, and progress log.

## Deterministic Prefix Policy

At session launch, the stable root context is assembled from `context/prefix_manifest.json` using `tools/compile_project_context.py`.

The intended stable ordered set is:

1. `CLAUDE.md`: role contract and hard boundaries.
2. `PROJECT_STATUS.md`: current project status and memory routing.
3. `docs/alignment_starter_protocol.md`: MultiAlignment starter protocol.
4. `docs/goal_harness.md`: `/goal` long-horizon controller.
5. `docs/session_context_architecture.md`: short-term context discipline.
6. `docs/task_artifact_protocol.md`: task-cycle artifact contract.
7. `docs/runtime_extension_points.md`: subagent, hook, and tool-call repair extension points.
8. `runtime/extension_manifest.json`: machine-checkable runtime extension registry.
9. `agents/memory/store/wiki/index.md`: wiki directory only, loaded by agents that are allowed to read memory.

The root context should route into deeper memory rather than inline the whole store. Full wiki pages, notes, learning files, and skills are loaded only when task-relevant.

Compiler usage:

```bash
python3 tools/compile_project_context.py --profile planner --check
python3 tools/compile_project_context.py --profile coder --output workspace/prefix/coder.md
```

Profiles:

- `planner`: excludes direct memory-store reads to preserve Planner's memory boundary.
- `coder`: includes wiki index and skill format for direct read access.
- `verifier`: includes wiki index and learning format for validation context.
- `memory`: includes write-back, wiki, notes, learning, and skill conventions.

## Task Artifact Gate

The task artifact protocol is executable through `tools/validate_task_artifacts.py`.

Use it before reporting a completed task cycle:

```bash
python3 tools/validate_task_artifacts.py
python3 tools/validate_task_artifacts.py --require-learning
```

The first command checks the Coder/Verifier workspace handoff. The second command also checks that Memory Agent wrote an evidence-backed learning record citing the task contract, candidate ledger, evidence, verification result, and promotion decision.

## Structural Validation

Run the harness structural checks:

```bash
python3 tools/validate_harness.py
python3 tools/validate_harness.py --include-workspace
```

The default command checks deterministic prefix compilation, wiki schema, skills schema, and runtime extension manifest. `--include-workspace` also checks the current ephemeral task artifact chain and evidence-backed learning record.

Task-cycle smoke:

```bash
python3 tools/run_task_cycle_smoke.py
```

This creates an isolated temporary task cycle, runs a real validation command, and proves the artifact protocol can validate Coder, Verifier, evidence, promotion, and learning handoff without relying on the current `workspace/` contents.

## Active Design Commitments

- Keep the four-main-agent design.
- Add Alignment Starter before every Planner task: compact alignment for clear requests, persisted plan alignment for complex work.
- Treat `/goal` as a user-triggered pluggable Planner command for persistent long-horizon control.
- Treat `.learning` as an evidence-backed record, not a loose event log.
- Use task contracts, candidate ledgers, evidence directories, and promotion decisions to make learning auditable.
- Evolve wiki and skills toward KDA-style knowledge packages with schema, query tools, validation, freshness metadata, and provenance.
- Treat Reasonix-style immutable prefix, append-only log, and volatile scratch as session-time context architecture.
- Keep hooks and tool-call repair as pluggable runtime positions through `runtime/extension_manifest.json`. Do not add complex hook machinery until a concrete need appears.

## Current Non-goals

- Do not revive early abstract organization experiments as the main architecture.
- Do not add more top-level agent roles.
- Do not make `PROJECT_STATUS.md` carry domain facts that belong in wiki, notes, learning, or skills.
- Do not put long-horizon goal state only in `workspace/`, because `workspace/` is ephemeral.
