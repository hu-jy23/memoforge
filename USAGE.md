# MemoForge Usage

## 1. Validate The Release

```bash
python3 tools/validate_harness.py
```

## 2. Build Agent Prefixes

```bash
python3 tools/compile_project_context.py --profile planner --output workspace/prefix/planner.md
python3 tools/compile_project_context.py --profile coder --output workspace/prefix/coder.md
python3 tools/compile_project_context.py --profile verifier --output workspace/prefix/verifier.md
python3 tools/compile_project_context.py --profile memory --output workspace/prefix/memory.md
```

The source list is deterministic and defined in:

```text
context/prefix_manifest.json
```

## 3. Launch Model Agents

Use the relevant directory prompt as the agent context:

| Agent | Prompt |
|---|---|
| Planner | `CLAUDE.md` |
| Coder | `agents/coder/CLAUDE.md` |
| Verifier | `agents/verifier/CLAUDE.md` |
| Memory Agent | `agents/memory/CLAUDE.md` |

The Planner is the user-facing entry point.

## 4. Run A Task Cycle

The expected task artifact chain is:

```text
workspace/task_contract.md
workspace/plan.json
workspace/candidates.jsonl
workspace/evidence/{task_id}/
workspace/verify_result.json
workspace/promotion_decision.md
agents/memory/store/learning/{task_id}.md
```

Validate the artifact chain:

```bash
python3 tools/validate_task_artifacts.py
python3 tools/validate_task_artifacts.py --require-learning
```

## 5. Bootstrap A New Domain Wiki

Install dependency:

```bash
pip install -r requirements.txt
```

Run the starter builder:

```bash
cd starter
python3 builder.py --sources /path/to/domain/docs --dry-run
python3 builder.py --sources /path/to/domain/docs
```

The builder writes pages under:

```text
agents/memory/store/wiki/
```

## 6. Optional Goal Control

Use `/goal ...` only when the user explicitly wants persistent long-horizon goal state.

The design document is:

```text
docs/goal_harness.md
```

Goal artifacts live under:

```text
goals/active/
```

