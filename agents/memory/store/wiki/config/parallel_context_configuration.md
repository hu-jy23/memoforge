---
title: Parallel and Context Configuration Rules
category: config
sources: ["AGENTS.md — config rules"]
last_updated: 2026-05-17
confidence: high
---

MindSpore auto-parallel configuration is injected through the `parallel` block in training configs.

**How it flows:** Config field `parallel` → passed through `build_context` → `context.set_auto_parallel_context(**parallel_config)` → MindSpore runtime.

**Valid field names:** Only add fields to `parallel.parallel_optimizer_config` that MindSpore's `set_auto_parallel_context()` actually accepts. Field naming mistakes are common:
- ✓ `parallel.parallel_optimizer_config.gradient_accumulation_shard` — valid in current qwen3 configs
- ✗ `parallel.grad_accumulation_shard` — INVALID, will be silently ignored or error at runtime

**Validation:** Do not trust YAML parsing alone. Before adding any `parallel.*` field, trace the runtime path to the actual MindSpore API call in the codebase (typically in a context builder or trainer constructor). Test against the known-good baseline.

**Callbacks:** Callback-specific configuration belongs under the callback item in the `callbacks` array, not at the top level. Qwen3 baseline currently uses `MFLossMonitor`, `CheckpointMointor`, and `ObsMonitor`. Experiment callbacks like `LayerStatsMonitor` belong in layer-stats variants only.