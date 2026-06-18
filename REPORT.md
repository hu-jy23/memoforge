# MemoForge: A Memory-Centered Agent Harness for Long-Horizon Software Development

## Abstract

Large language model coding agents are increasingly capable of writing and modifying software, but their behavior remains fragile in long-horizon engineering tasks. They often lose project context, lack explicit completion criteria, under-document failed attempts, and turn useful experience into unstructured chat history. MemoForge is a memory-centered agent harness designed to make agentic software development more aligned, auditable, and accumulative. It combines four main agents, deterministic context injection, a human-memory-inspired project memory, evidence-backed task artifacts, and reserved runtime extension points. The current release demonstrates a complete harness structure with Planner, Coder, Verifier, and Memory Agent roles; wiki, notes, learning, and skills memory stores; task contracts, candidate ledgers, evidence directories, and promotion decisions; plus validators that check prefix compilation, memory schemas, runtime manifests, and task-cycle artifacts.

## 1. Introduction

Modern coding agents such as Codex and Claude Code can complete many short programming tasks, especially in mainstream software stacks. Real engineering work often has a different shape: the agent must understand project-specific documentation, preserve task intent across multiple turns, verify behavior with domain-specific commands, and write back lessons so future tasks become easier.

MemoForge starts from a simple observation: human developers do not rely on a single context window. They use long-term knowledge, mid-term notes, short-term working context, explicit plans, validation routines, and memory consolidation. The project turns this observation into a public harness structure for AI-assisted software development.

The goal is not to replace a coding model. The goal is to provide a substrate around the model so its behavior becomes easier to align, inspect, validate, and improve over time.

## 2. Related Work

### 2.1 Agentic Coding Systems

Contemporary coding agents provide tool use, terminal interaction, file editing, and iterative debugging. These systems are effective when the task can be solved from local code context and model priors. MemoForge focuses on the surrounding harness: role boundaries, project memory, task artifacts, validation evidence, and long-horizon state.

### 2.2 LLM Wiki And Structured Project Memory

The LLM Wiki idea treats project knowledge as a human-readable Markdown knowledge base that agents can query and maintain. MemoForge adopts this principle for long-term memory. Wiki pages are not raw document dumps; they are structured knowledge units with schema, freshness metadata, provenance, query scripts, and validators.

### 2.3 Kernel Design Agents And Evidence-Based Promotion

Kernel Design Agents inspired the use of explicit task contracts, candidates, benchmark evidence, and promotion decisions. MemoForge generalizes this pattern beyond kernel writing. A candidate is not accepted because it exists; it is accepted when evidence satisfies the task contract. A learning record is not promoted because it is interesting; it is promoted when repeated evidence supports it.

### 2.4 Reasonix-Style Runtime Context

Reasonix inspired the short-term session-context model: immutable prefix, append-only log, and volatile scratch. MemoForge treats these as runtime context layers orthogonal to long-term project memory.

### 2.5 Codex Goals And Long-Horizon Control

Codex `/goal` motivates persistent long-horizon control. MemoForge keeps `/goal` as an optional explicit command: user-triggered, persistent, and auditable. It is separate from Planner's default self-alignment behavior.

## 3. Our Harness

### 3.1 Overview

MemoForge consists of four main agents:

- **Planner**: user-facing orchestrator and task-cycle owner.
- **Coder**: candidate implementation owner.
- **Verifier**: validation, evidence, and promotion-decision owner.
- **Memory Agent**: sole writer to persistent project memory.

The agents communicate through structured artifacts rather than informal chat alone.

```text
Planner -> Coder -> Verifier -> Memory Agent
               \-> task artifacts <-/
```

### 3.2 Self-Alignment Starter

Planner begins each interaction with self-alignment. For simple requests, this can be compact and implicit in the handoff. For complex requests, Planner performs MultiAlignment:

- ask missing details,
- confirm shared understanding,
- identify implicit defaults,
- assemble required sources,
- request user double check before execution.

The protocol is documented in `docs/alignment_starter_protocol.md`.

### 3.3 Optional Goal Harness

`/goal` is an optional slash-command-style controller for long-horizon work. It is only triggered when the user explicitly invokes it. A goal can maintain persistent state, a goal contract, progress, blockers, and audit decisions.

The protocol is documented in `docs/goal_harness.md`.

### 3.4 Human-Memory-Inspired Project Memory

MemoForge maps human memory behavior into four project-memory stores:

| Memory Store | Role |
|---|---|
| `wiki/` | stable long-term knowledge |
| `notes/` | mid-term observations and reflections |
| `learning/` | evidence-backed task learning records |
| `skills/` | validated procedural memory |

The Memory Agent owns writes to these stores. Planner does not directly access persistent memory.

### 3.5 Deterministic Prefix Injection

The immutable prefix is built from a manifest:

```text
context/prefix_manifest.json
```

The compiler:

```text
tools/compile_project_context.py
```

assembles per-agent context profiles and records source hashes. This makes launch context stable and inspectable.

### 3.6 Task Artifact Protocol

Each non-trivial development task should leave a trace:

```text
task_contract.md
  -> candidates.jsonl
  -> evidence/
  -> verify_result.json
  -> promotion_decision.md
  -> learning record
```

This makes task completion auditable. It also creates the evidence needed for notes, wiki updates, and skill promotion.

### 3.7 Runtime Extension Points

MemoForge reserves runtime positions for:

- lightweight subagents inside main-agent boundaries,
- tool-call repair,
- lifecycle hooks,
- slash commands.

These positions are registered in `runtime/extension_manifest.json` and validated by `tools/validate_runtime_extensions.py`.

## 4. Experiments And Results

### 4.1 Structural Validation

The public release includes a validation command:

```bash
python3 tools/validate_harness.py
```

This checks:

- prefix manifest JSON,
- runtime manifest JSON,
- deterministic prefix compilation,
- Python syntax compilation,
- wiki schema,
- skills schema,
- skills query path,
- runtime extensions,
- goal/alignment integration,
- isolated task-cycle smoke test.

### 4.2 Demo Task Cycle

The release includes one example task cycle:

```text
examples/custom-callback-norm-lr-01/
```

It demonstrates:

- a task contract,
- a candidate ledger,
- implementation patch artifacts,
- evidence logs,
- verification result,
- promotion decision.

The example shows how an agent output becomes a traceable engineering artifact rather than a single unstructured response.

### 4.3 Current Measured Outputs

At release time, the harness contains:

- four main-agent prompt profiles,
- deterministic prefix compilation,
- a project wiki and memory store,
- schema/query/validation scripts for wiki and skills,
- one evidence-backed learning record,
- one task-cycle smoke test,
- one public demo task cycle.

## 5. Limitations

The current release is a research prototype. The runtime hook system and tool-call repair layer are reserved design positions rather than complete runtime adapters. The skill store has schema and validation support, but larger-scale skill promotion requires more repeated task evidence. Evaluation is currently structural and artifact-based; future work should add more domain tasks and compare agent behavior with and without the harness.

## 6. Conclusion

MemoForge presents an agent harness for software development that emphasizes alignment, memory, evidence, and promotion. Its core contribution is to organize agentic coding as an auditable development process: user intent is aligned, context is injected deterministically, agents are separated by responsibility, task outcomes are verified with evidence, and useful experience can be promoted into persistent memory. This turns one-off agent interactions into a reusable substrate for long-horizon engineering work.

