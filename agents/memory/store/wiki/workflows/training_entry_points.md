---
title: MindFormers Training Entry Points and Project Structure
category: workflows
sources: ["AGENTS.md — project structure and entry points"]
last_updated: 2026-05-17
confidence: high
---

The MindFormers codebase is organized around a single training entry point: `run_mindformer.py`.

**Training launch:** Always use `run_mindformer.py` for ModelArts jobs or local training. Shell wrapper scripts in the repository are reference tools only, not training entry points.

**Project directory layout:**
- `run_mindformer.py` — main training script accepting YAML config paths
- `mindformers/` — core framework: trainers, callbacks, wrappers, models, context setup
- `configs/` — YAML training configs. Baseline configs are experiment references
- `configs/qwen3/` — Qwen3 experiment configs
- `configs/qwen3/test/` — small experiment variants for rapid iteration
- `tools/monitoring/` — WandB/SwanLab probes and remote log-to-WandB streaming
- `debug/wandb_monitor/` — local WandB monitor unit tests and fake dataset utilities
- `开发文档/` — experiment plans and engineering notes
- `训练启动总览模板.md`, `启动训练界面.md` — ModelArts launch UI reference

When adding a new training run, copy a known-good baseline config and keep diffs minimal to the intended experimental block. Do not create arbitrary new configs from scratch.