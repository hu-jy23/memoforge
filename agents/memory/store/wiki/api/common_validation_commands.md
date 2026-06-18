---
title: Common Validation Commands
category: api
sources: ["AGENTS.md — common commands"]
last_updated: 2026-05-17
confidence: high
---

Syntax and structure validation commands for development and testing.

**Python syntax check:**
```bash
python -m py_compile <file.py>
```

**Parse and validate one YAML config:**
```bash
python - <<'PY'
import yaml
from pathlib import Path
p = Path('<config.yaml>')
yaml.safe_load(p.read_text(encoding='utf-8'))
print('yaml_ok', p)
PY
```

**Run WandB monitor unit tests:**
```bash
python debug/wandb_monitor/phase0_unit_test.py
```

**Test remote monitor offline (against sample logs):**
```bash
python tools/monitoring/stream_modelarts_log_to_wandb.py \
  --log_dir <local-or-obs-log-dir> \
  --storage_backend auto \
  --mode offline \
  --once
```

**Run remote monitor live against OBS logs:**
```bash
python tools/monitoring/stream_modelarts_log_to_wandb.py \
  --log_dir obs://research-my/hujy/Exps/Logs_26/04/25/ \
  --storage_backend mox \
  --project pacman-remote-monitor \
  --mode online \
  --output_dir ./wandb_remote_monitor/<run-name>
```