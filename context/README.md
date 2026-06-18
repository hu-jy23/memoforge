# Context Assembly

This directory defines deterministic prefix assembly for MemoForge.

`prefix_manifest.json` is the source of truth. It lists which stable files enter each main agent's immutable prefix, in order.

Use:

```bash
python3 tools/compile_project_context.py --profile planner --check
python3 tools/compile_project_context.py --profile coder --output workspace/prefix/coder.md
python3 tools/validate_harness.py
```

The compiler does not decide task-specific context. It only assembles launch-time root context. Task-specific files remain explicit `context_refs` in Planner spawn prompts.
