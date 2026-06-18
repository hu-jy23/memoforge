---
title: Remote Monitoring Workflow
category: workflows
sources: ["AGENTS.md — monitoring workflow"]
last_updated: 2026-05-17
confidence: high
---

Remote monitoring watches training jobs running on ModelArts from a development machine that can read OBS and upload to WandB.

**Monitoring setup:** Training logs on OBS are streamed to WandB via `tools/monitoring/stream_modelarts_log_to_wandb.py`. This runs offline on the development machine; training may fail to upload WandB directly, but the remote monitor collects logs asynchronously.

**Log sources:** ModelArts distributed training produces logs from multiple worker types (trainers, evaluators, pipeline stages). The remote monitor must:
- Read logs from OBS via `mox` backend
- Auto-detect which worker is train/eval (for loss and eval metrics)
- Collect layer stats from all pipeline-stage workers if applicable
- Stream metrics to WandB project specified by `--project` flag

**Worker coordination:** For pipeline-parallel qwen3 experiments, loss/eval metrics may come from a later pipeline stage, while layer stats require aggregation across multiple workers. The monitor must not assume a single authoritative worker.

**Failure isolation:** Remote monitor failures must not block training. Use `--mode offline` for initial testing against sample logs before switching to `--mode online` for live WandB uploads.

**Testing:** Test offline parsing once against a sample ModelArts log before enabling online WandB upload:
```bash
python tools/monitoring/stream_modelarts_log_to_wandb.py \
  --log_dir <sample-log-dir> \
  --storage_backend auto \
  --mode offline \
  --once
```