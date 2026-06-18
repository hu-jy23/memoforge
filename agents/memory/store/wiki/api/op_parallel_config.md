---
title: OpParallelConfig — Operator-Level Parallelism Configuration
category: api
sources: ["mindformers.modules.OpParallelConfig"]
last_updated: 2026-05-17
confidence: high
---

Configuration class for setting operator-level parallelism modes in MindFormers distributed training.

## Constructor Signature

```python
OpParallelConfig(
    data_parallel=1,
    model_parallel=1,
    use_seq_parallel=False,
    context_parallel=1,
    select_recompute=False,
    context_parallel_algo='colossalai_cp'
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_parallel` | int | 1 | Quantity of data parallelism devices. |
| `model_parallel` | int | 1 | Quantity of model parallelism devices. |
| `use_seq_parallel` | bool | False | Whether to enable sequence parallelism. |
| `context_parallel` | int | 1 | Quantity of context parallelism devices. |
| `select_recompute` | bool | False | Whether to enable selective recomputation. |
| `context_parallel_algo` | str | `'colossalai_cp'` | Context parallelism algorithm. Valid values: `"colossalai_cp"` (default) or `"ulysses_cp"`. |

## Returns

Instance of `OpParallelConfig`.

## Example Usage

```python
from mindformers.modules import OpParallelConfig

# Basic configuration
config = OpParallelConfig(data_parallel=1, model_parallel=1)
print(config)
# Output: [ParallelConfig] _data_parallel:1 _model_parallel:1 _context_parallel:1 
#         use_seq_parallel:False select_recompute:False 
#         context_parallel_algo:ContextParallelAlgo.colossalai_cp
```

## Key Implementation Detail

When `context_parallel_algo='colossalai_cp'` is used, the internal representation uses `ContextParallelAlgo.colossalai_cp` enum. Ensure parameter names match exactly — case-sensitive.