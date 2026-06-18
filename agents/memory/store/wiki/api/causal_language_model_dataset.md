---
title: CausalLanguageModelDataset
category: api
sources: ["mindformers.dataset.CausalLanguageModelDataset.html"]
last_updated: 2026-05-17
confidence: high
---

CausalLanguageModelDataset constructs pretraining data pipelines for causal language models, handling tokenized sequences, EOD tokens, and dynamic batching on Ascend hardware.

## Overview

```python
from mindformers.dataset import CausalLanguageModelDataset

dataset = CausalLanguageModelDataset(
    data_loader={
        "type": "MindDataset",  # or "TFRecordDataset"
        "dataset_dir": "/path/to/mindrecord/",  # recursive scan
        "shuffle": True
    },
    input_columns=["input_ids", "attention_mask"],
    output_columns=["input_ids", "attention_mask"],  # required if eod_reset=True
    batch_size=8,
    drop_remainder=True,
    num_parallel_workers=8,
    eod_reset=False,
    eod_token_id=None
)
```

## Data Loader Configuration

The `data_loader` parameter must be a dict or callable instance:

| Key | Type | Required | Notes |
|-----|------|----------|-------|
| `type` | str | Yes | `"MindDataset"` or `"TFRecordDataset"` only. |
| `dataset_dir` | str | If type ∈ {MindDataset, TFRecordDataset} | Directory path. Recursively scans for `.mindrecord` or `.tfrecord` files. |
| `dataset_files` | list[str] | If no `dataset_dir` | Explicit file paths. Lower priority than `dataset_dir`. |
| `shuffle` | bool | Optional | Whether to shuffle the dataset. |

**Constraint:** Exactly one of `dataset_dir` or `dataset_files` must be specified for MindDataset/TFRecordDataset types; `dataset_dir` takes priority.

## Critical Parameters

### `eod_reset` and `eod_token_id`

- **`eod_reset`** (bool): If `True`, the dataset resets after encountering an EOD (end-of-document) token. Used for document-level batching in pretraining.
- **`eod_token_id`** (int): The vocabulary ID of the EOD token. Only applies when `eod_reset=True`.

**Device Distribution Constraint (ValueError if violated):**  
When `eod_reset=True` and the dataset is not fully imported, `batch_size` **must** be an integer multiple of the device count:

```python
# ✓ Valid on 8-device Ascend cluster
dataset = CausalLanguageModelDataset(
    batch_size=64,  # 64 % 8 == 0
    eod_reset=True,
    eod_token_id=2
)

# ✗ Invalid: 50 % 8 != 0 → raises ValueError
dataset = CausalLanguageModelDataset(
    batch_size=50,
    eod_reset=True
)
```

### Data Type Conversion

All output columns are **automatically converted to int32** type. Ensure input data is int-compatible; int64 → int32 downcast may lose precision.

### Batching Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `batch_size` | 8 | Per-worker batch size. |
| `drop_remainder` | True | Drop final batch if smaller than `batch_size`. Must align with `eod_reset` logic. |
| `repeat` | 1 | Number of times to repeat the dataset. |

### Parallelization

| Parameter | Default | Notes |
|-----------|---------|-------|
| `num_parallel_workers` | 8 | Worker threads/processes for data mapping. |
| `python_multiprocessing` | False | Use Python multiprocessing for acceleration if `True`. |
| `prefetch_size` | 1 | Pipeline queue size per operation. Higher = more memory, better throughput. |
| `numa_enable` | False | NUMA binding for server-class Ascend systems. |
| `seed` | 0 | Random seed for shuffling. |

### Autotuning and Profiling

- **`auto_tune`** (bool): Enable automatic optimization of pipeline parameters.
- **`autotune_per_step`** (int, default 10): Re-tune frequency (steps).
- **`filepath_prefix`** (str, default `'./autotune'`): Directory for autotuning logs.
- **`profile`** (bool): Collect profiling metrics.
- **`token_monitor`** (bool): Enable token count monitoring per batch.
- **`token_monitor_config`** (dict): Token monitor settings; if `None`, use defaults.

## Common Pitfalls

1. **EOD with multi-device:** `eod_reset=True` without `batch_size % num_devices == 0` → **ValueError**.
2. **Missing data loader:** Omit both `dataset_dir` and `dataset_files` → **ValueError**.
3. **Data type overflow:** int64 input with large values → int32 downcast loses precision.
4. **Missing output_columns:** Required when `eod_reset=True`; omitting raises error.
5. **Wrong data_loader type:** Specifying undefined loader type (not MindDataset or TFRecordDataset) → **ValueError**.

## Example

```python
from mindformers.dataset import CausalLanguageModelDataset

data_loader = {
    "type": "MindDataset",
    "dataset_dir": "/data/pretrain/mindrecord/",
    "shuffle": True
}

dataset = CausalLanguageModelDataset(
    data_loader=data_loader,
    input_columns=["input_ids", "attention_mask"],
    batch_size=32,
    drop_remainder=True,
    num_parallel_workers=8,
    seed=42
)

for batch in dataset.create_dict_iterator():
    input_ids = batch["input_ids"]  # (32, seq_len), int32
    attention_mask = batch["attention_mask"]  # (32, seq_len), int32
```

## See Also

- [[api/keyword_gen_dataset]] — Keyword/headline generation datasets.
- [[api/multi_turn_dataset]] — Multi-turn dialogue datasets.