# Alignment Starter Protocol

## Purpose

Alignment Starter is the default entry step for every Planner interaction. It aligns user intent, missing assumptions, source needs, and success criteria before execution starts.

It exists because a chat exchange often hides defaults, missing sources, unspoken constraints, and assumed success criteria. The harness must surface these details before Planner decomposes work.

## Trigger

Run Alignment Starter for every user request.

Compact alignment is enough when the request is clear, low-risk, and does not need persistent goal state. In that case, Planner carries the aligned intent into the sub-agent prompt or final answer and proceeds.

Run full persisted Alignment Starter before:

- `/goal create`
- long-horizon work
- project-level design or architecture shifts
- underspecified implementation work
- tasks that require external sources, credentials, datasets, metrics, environment assumptions, or domain-specific validation
- any request where the user appears to rely on implicit defaults

`/goal` starts only when the user explicitly enters a `/goal ...` command. Planner alignment must not silently create, resume, complete, or block a goal.

## Core Rule

The user provides the primary intent and plan content. The agent polishes, expands, questions, checks sources, and asks for double check.

When alignment needs persistent artifacts, the final aligned plan is stored at:

```text
goals/active/plan.md
```

When the aligned work becomes an explicit goal, the goal-level contract derived from that plan is stored at:

```text
goals/active/goal_contract.md
```

## MultiAlignment Loop

MultiAlignment has three required behaviors.

### 1. Question Unknowns

Ask targeted questions about:

- unstated defaults
- omitted configs
- missing source material
- expected outputs
- metrics
- validation commands
- environment assumptions
- credentials or token availability
- scope boundaries
- autonomy boundaries
- risk tolerance

Do not ask broad generic questions when a concrete checklist is possible.

### 2. Propose QA To User

The agent must restate proposed understanding and ask the user to confirm or reject it.

Allowed patterns:

- "So the goal is ... correct?"
- "The expected output is ... correct?"
- "The success criterion is ... correct?"
- "The source list needed for execution is ... complete?"
- "This constraint means ... correct?"
- "This part is intentionally out of scope, correct?"

These confirmations are part of the alignment artifact, not casual chat.

### 3. Source Assembly And Double Check

`goals/active/plan.md` must include a source section with every material needed for execution:

- websites and external docs
- codebase paths
- database names or access notes
- tokens, credentials, or secret references
- markdown files
- links
- datasets
- environment constraints
- metrics
- validation commands
- screenshots, diagrams, or user-provided sketches

After source assembly, ask the user for explicit double check. Execution starts only after the user accepts the plan or explicitly waives the gate.

## Output Artifacts

| Path | Purpose |
|---|---|
| `goals/active/plan.md` | Polished human plan with source section and confirmations |
| `goals/active/alignment_questions.md` | Open questions, answers, unresolved defaults, and QA confirmations |
| `goals/active/goal_contract.md` | Stable objective, scope, constraints, success criteria, and autonomy |
| `goals/active/status.json` | Machine-readable goal state for `/goal status` and `/goal continue` |
| `goals/active/progress.md` | Append-only long-horizon progress log |

## Position In Harness

Alignment Starter is owned by Planner. It is a starter protocol, not a new main agent.

Coder may write the artifacts because Planner does not write project files. Verifier may check source availability or validation commands when requested. Memory Agent may provide project-memory context through normal memory routes.

## Handoff

After user double check for persisted alignment:

```text
User intent
  -> Alignment Starter
  -> goals/active/plan.md
  -> goals/active/goal_contract.md
  -> /goal Controller when explicitly requested
  -> Planner task decomposition
  -> Task Artifact Protocol
```
