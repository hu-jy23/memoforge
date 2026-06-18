---
title: MultiTurnDataset
category: api
sources: ["mindformers.dataset.MultiTurnDataset.html"]
last_updated: 2026-05-17
confidence: high
---

MultiTurnDataset constructs dialogue training pipelines for multi-turn conversation models, handling dialogue history, response targets, and loss masking for dialogue-specific training.

## Overview

```python
from mindformers import MultiTurnDataset
from mindformers.tools.register import MindFormerConfig

config = MindFormerConfig(
    data_loader={
        "type": "ToolAlpacaDataLoader",
        "dataset_dir": "/path/to/dialogue.jsonl",
        "shuffle": True
    },
    tokenizer={
        "type": "ChatGLM3Tokenizer",
        "vocab_file": "/path/to/tokenizer.model"
    },
    max_seq_length=2048,
    batch_size=1,
    drop_remainder=True,
    num_parallel_workers=8
)

dataset = MultiTurnDataset(config)
```

## Configuration

MultiTurnDataset requires a **`dataset_config` dict** (not optional) containing all pipeline parameters. This differs from other dataset classes which accept individual keyword arguments.

### Required Keys in `dataset_config`

| Key | Type | Required | Notes |
|-----|------|----------|-------|
| `data_loader` | dict | Yes | Data loader configuration (see below). |
| `tokenizer` | dict\|Callable | Yes | Tokenizer instance or config dict. |
| `max_seq_length` | int | Yes | Maximum sequence length (includes history + response). |
| `batch_size` | int | Yes | Per-worker batch size. |

### Optional Keys in `dataset_config`

| Key | Type | Default | Notes |
|-----|------|---------|-------|
| `drop_remainder` | bool | (not specified) | Drop final batch if smaller than `batch_size`. |
| `num_parallel_workers` | int | (not specified) | Worker threads/processes. |
| `python_multiprocessing` | bool | (not specified) | Use Python multiprocessing. |
| `repeat` | int | (not specified) | Dataset repeat count. |
| `seed` | int | (not specified) | Random seed. |
| `prefetch_size` | int | (not specified) | Pipeline queue size. |
| `numa_enable` | bool | (not specified) | NUMA binding. |

## Data Loader Configuration

The `data_loader` dict in `dataset_config` must contain:

| Key | Type | Required | Notes |
|-----|------|----------|-------|
| `type` | str | Yes | Data loader class, e.g., `"ToolAlpacaDataLoader"`. |
| `dataset_dir` | str | Yes | Path to JSONL or other dialogue format file. |
| `shuffle` | bool | Yes | Whether to shuffle the dataset. |

> **Note:** Ensure `dataset_dir` path exists; omitting raises **ValueError**.

## Tokenizer Configuration

The `tokenizer` dict must contain:

```python
tokenizer = {
    "type": "ChatGLM3Tokenizer",  # or "AutoTokenizer", etc.
    "vocab_file": "/path/to/tokenizer.model"
}
```

## Output Columns

The dataset generates exactly two output columns (both int32):

| Column | Type | Content |
|--------|------|---------|
| `input_ids` | int32 | Concatenated dialogue history + response tokens. |
| `labels` | int32 | Response tokens for loss computation; history typically masked. |

> **Constraint:** Token count and loss mask count must be equal; mismatch raises **ValueError**.

## Critical Constraints

### Python Version

- **Minimum Python 3.9** required. Running on Python < 3.9 raises **ValueError**.

### Sequence Alignment

- **ValueError:** Mismatch between token count and loss mask count for prediction tokens.
- **ValueError:** Mismatch between input token count and label count.

These indicate data loading or tokenization errors; debug the dialogue data format and tokenizer.

### Dataset Path Validation

- **ValueError:** Missing `dataset_dir` in `data_loader` config or path does not exist.

## Example

```python
from mindformers import MultiTurnDataset
from mindformers.tools.register import MindFormerConfig

config_dict = {
    "data_loader": {
        "type": "ToolAlpacaDataLoader",
        "dataset_dir": "/data/dialogue/tool_alpaca.jsonl",
        "shuffle": True
    },
    "tokenizer": {
        "type": "ChatGLM3Tokenizer",
        "vocab_file": "/models/tokenizer.model"
    },
    "max_seq_length": 2048,
    "batch_size": 1,
    "drop_remainder": True,
    "num_parallel_workers": 8,
    "python_multiprocessing": False,
    "repeat": 1,
    "seed": 0,
    "prefetch_size": 1,
    "numa_enable": False
}

# Validate config
from mindformers.dataset import check_dataset_config
config = MindFormerConfig(**config_dict)
check_dataset_config(config)

# Build dataset
dataset = MultiTurnDataset(config)

for batch in dataset.create_dict_iterator():
    input_ids = batch["input_ids"]  # (batch_size, max_seq_length), int32
    labels = batch["labels"]  # (batch_size, max_seq_length), int32
    # Training step...
```

## Common Pitfalls

1. **Config dict vs kwargs:** MultiTurnDataset accepts **only** a `dataset_config` dict, not individual keyword arguments.
2. **Missing `data_loader` or `tokenizer`:** Both are mandatory in config; omitting raises **ValueError**.
3. **Python < 3.9:** Running on older Python → **ValueError**.
4. **Dialogue format:** JSONL format must match loader expectations (e.g., ToolAlpacaDataLoader expects specific field names). Invalid format → **ValueError**.
5. **Sequence mismatch:** Inconsistent tokenization or malformed dialogue data → **ValueError** on token/label mismatch.

## See Also

- [[api/causal_language_model_dataset]] — Pretraining datasets.
- [[api/keyword_gen_dataset]] — Conditional generation datasets.
- [[config/mindformers_tokenizer_config]] — Tokenizer configuration schema.