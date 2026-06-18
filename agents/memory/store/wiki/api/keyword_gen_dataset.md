---
title: KeyWordGenDataset
category: api
sources: ["mindformers.dataset.KeyWordGenDataset.html"]
last_updated: 2026-05-17
confidence: high
---

KeyWordGenDataset handles conditional sequence generation tasks (e.g., headline/keyword generation from source text) with phase-dependent output columns and tokenizer integration.

## Overview

```python
from mindformers.dataset import KeyWordGenDataset

dataset = KeyWordGenDataset(
    data_loader={
        "type": "MindDataset",
        "dataset_dir": "/path/to/data/",
        "phase": "train",  # or "eval"
        "shuffle": True,
        "origin_columns": ["content", "summary"]  # [source, target]
    },
    tokenizer={"type": "AutoTokenizer", "pretrained_model_name_or_path": "glm_6b"},
    input_columns=["input_ids", "labels", "position_ids", "attention_mask"],
    batch_size=8,
    phase="train",
    max_source_length=512,
    max_target_length=64
)
```

## Data Loader Configuration

| Key | Type | Required | Notes |
|-----|------|----------|-------|
| `type` | str | Yes | `"MindDataset"` only. |
| `dataset_dir` | str | Yes if no `dataset_files` | Directory path. Recursively scans for `.mindrecord` files. |
| `dataset_files` | list[str] | Yes if no `dataset_dir` | Explicit `.mindrecord` file paths. Lower priority than `dataset_dir`. |
| `phase` | str | Yes (in dict) | `"train"` or `"eval"`. Determines output columns. |
| `shuffle` | bool | Yes | Whether to shuffle the dataset. |
| `origin_columns` | list[str] | Yes | Two-element list: `[source_column_name, target_column_name]`. Maps to source and target text in the data file. |
| `version` | int or str | Optional, default 1 | Mapping function version: `1` or `2`. |

## Output Columns by Phase

### Phase: `"train"`
Output columns: `[input_ids, labels, position_ids, attention_mask]` (all int32)
- `input_ids`: Concatenated source + target tokens with separation markers.
- `labels`: Target tokens for loss computation; source portion typically masked.
- `position_ids`: Token position indices.
- `attention_mask`: Masking for padding and causality.

### Phase: `"eval"`
Output columns: `[input_ids, labels]` (both int32)
- Simplified output for evaluation (no position_ids or attention_mask).

## Critical Parameters

### Tokenizer Configuration

The `tokenizer` parameter must be a dict or callable instance:
```python
tokenizer = {
    "type": "ChatGLM3Tokenizer",
    "vocab_file": "/path/to/tokenizer.model"
}
# or
tokenizer = {
    "type": "AutoTokenizer",
    "pretrained_model_name_or_path": "glm_6b"
}
```

### Sequence Length Control

| Parameter | Type | Notes |
|-----------|------|-------|
| `max_source_length` | int | Maximum length of source (input) sequences. Sequences longer than this are truncated. |
| `max_target_length` | int | Maximum length of target (output) sequences. Sequences longer than this are truncated. |

### Loss Masking

- **`ignore_pad_token_for_loss`** (bool, default `True`): If `True`, padding tokens do not contribute to loss computation. Recommended for variable-length sequences.

### Version-Specific Behavior

| Version | Description | Use Case |
|---------|-------------|----------|
| `1` | Standard mapping function. | Most use cases. |
| `2` | Alternate mapping variant (exact differences not specified in docs). | Experimentation; consult model card. |

> **Note (low confidence):** Exact differences between v1 and v2 mapping functions not documented in source. Check corresponding model card (e.g., GLM-4 model card on Gitee).

### Batching and Parallelization

| Parameter | Default | Notes |
|-----------|---------|-------|
| `batch_size` | 8 | Per-worker batch size. |
| `drop_remainder` | True | Drop final batch if smaller than `batch_size`. |
| `num_parallel_workers` | 8 | Worker threads/processes. |
| `repeat` | 1 | Dataset repeat count. |
| `prefetch_size` | 1 | Pipeline queue size. |
| `numa_enable` | False | NUMA binding. |
| `seed` | 0 | Random seed. |

### Autotuning and Profiling

- **`auto_tune`** (bool, default `False`): Enable automatic pipeline optimization.
- **`autotune_per_step`** (int, default 10): Re-tune frequency.
- **`filepath_prefix`** (str, default `'./autotune'`): Autotuning log directory.
- **`profile`** (bool, default `False`): Collect profiling metrics.

## Common Pitfalls

1. **Missing `origin_columns`:** Required in `data_loader` dict; omitting raises **ValueError**.
2. **Wrong phase value:** Must be `"train"` or `"eval"`. Other values → error.
3. **Mismatch input/output columns:** Output columns differ by phase; ensure code handles both.
4. **Tokenizer not initialized:** Passing `None` or invalid tokenizer config → runtime error.
5. **Sequence length mismatch:** Setting `max_source_length` or `max_target_length` to 0 or very small values → empty batches.
6. **Data type:** All output columns automatically int32; overflow possible for very long sequences.

## Example

```python
from mindformers.dataset import KeyWordGenDataset
from mindformers import AutoTokenizer

data_loader = {
    "type": "MindDataset",
    "dataset_dir": "/data/ad_gen/",
    "phase": "train",
    "shuffle": True,
    "origin_columns": ["content", "summary"],
    "version": 1
}

tokenizer = AutoTokenizer.from_pretrained("glm_6b")

dataset = KeyWordGenDataset(
    data_loader=data_loader,
    tokenizer=tokenizer,
    input_columns=["input_ids", "labels", "position_ids", "attention_mask"],
    batch_size=16,
    max_source_length=512,
    max_target_length=64,
    ignore_pad_token_for_loss=True,
    phase="train"
)

for batch in dataset.create_dict_iterator():
    input_ids = batch["input_ids"]  # (16, seq_len), int32
    labels = batch["labels"]  # (16, seq_len), int32
    # Training step...
```

## See Also

- [[api/causal_language_model_dataset]] — Causal pretraining datasets.
- [[api/multi_turn_dataset]] — Multi-turn dialogue datasets.