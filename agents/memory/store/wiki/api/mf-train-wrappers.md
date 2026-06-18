---
title: MFTrainOneStepCell and MFPipelineWithLossScaleCell — Training Step Wrappers
category: api
sources: ["mindformers.wrapper.MFTrainOneStepCell.html", "mindformers.wrapper.MFPipelineWithLossScaleCell.html"]
last_updated: 2026-05-17
confidence: high
---

MindFormers provides two training-step wrappers that replace MindSpore's bare `TrainOneStepCell`: `MFTrainOneStepCell` for standard data-parallel/single-device training, and `MFPipelineWithLossScaleCell` for pipeline-parallel training. Both handle loss scaling, gradient clipping, and norm logging in one cell.

## MFTrainOneStepCell

```python
class mindformers.wrapper.MFTrainOneStepCell(
    network,
    optimizer,
    use_clip_grad=False,        # NOTE: default is False (differs from Pipeline wrapper)
    max_grad_norm=1.0,
    scale_sense=1.0,
    local_norm=False,
    calculate_per_token_loss=False,
    global_norm_spike_threshold=1.0,
    use_skip_data_by_global_norm=False,
    print_separate_loss=False,
    **kwargs
)
```

### Parameters

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `network` | `Cell` | — | Training network; **single output only** |
| `optimizer` | `Cell` | — | Parameter update optimizer |
| `use_clip_grad` | `bool` | `False` | Enable gradient clipping |
| `max_grad_norm` | `float` | `1.0` | Clip threshold (used only when `use_clip_grad=True`) |
| `scale_sense` | `int\|float\|Tensor\|Cell` | `1.0` | Loss scale. `Cell` → device-side update; `Tensor` → host-side (modify via `set_sense_scale`). Shape must be `()` or `(1,)` |
| `local_norm` | `bool` | `False` | Compute per-group gradient norms |
| `calculate_per_token_loss` | `bool` | `False` | Normalize loss by token count |
| `global_norm_spike_threshold` | `float` | `1.0` | Threshold for data-skip on norm spike |
| `use_skip_data_by_global_norm` | `bool` | `False` | Skip batch when global norm exceeds threshold |
| `print_separate_loss` | `bool` | `False` | Print loss components separately |

### Output Tuple

Returns **5 tensors** normally, **7 tensors** when `local_norm=True`:

| Index | Name | Shape | Condition |
|---|---|---|---|
| 0 | `loss` | scalar | always |
| 1 | `overflow` | bool | always |
| 2 | `loss_scale` | `()` or `(1,)` | always |
| 3 | `learning_rate` | — | always |
| 4 | `global_norm` | scalar or `None` | always; `None` if `use_clip_grad=False` |
| 5 | `local_norm` | grouped tensor | only if `local_norm=True` |
| 6 | `size` | grouped tensor | only if `local_norm=True` |

### Errors

| Exception | Trigger |
|---|---|
| `TypeError` | `scale_sense` is not a `Cell` or `Tensor` |
| `ValueError` | `scale_sense` shape is not `(1,)` or `()` |

### Minimal Example

```python
from mindformers.models.llama import LlamaConfig, LlamaForCausalLM
from mindformers.wrapper import MFTrainOneStepCell
from mindformers.core.optim import AdamW
import mindspore as ms
import numpy as np

ms.set_context(mode=ms.GRAPH_MODE)

config = LlamaConfig(num_layers=2)
net = LlamaForCausalLM(config=config)
net.set_train(True)
optimizer = AdamW(net.trainable_params())

mft = MFTrainOneStepCell(net, optimizer)
inputs = ms.Tensor(np.ones([1, 2049]), ms.int32)
loss, overflow, loss_scale, lr, global_norm = mft(inputs)
```

---

## MFPipelineWithLossScaleCell

```python
class mindformers.wrapper.MFPipelineWithLossScaleCell(
    network,
    optimizer,
    use_clip_grad=True,         # NOTE: default is True (differs from MFTrainOneStepCell)
    max_grad_norm=1.0,
    scale_sense=1.0,
    micro_batch_num=1,
    local_norm=False,
    calculate_per_token_loss=False,
    global_norm_spike_threshold=1.0,
    use_skip_data_by_global_norm=False,
    print_separate_loss=False,
    **kwargs
)
```

### Additional Parameters vs MFTrainOneStepCell

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `micro_batch_num` | `int` | `1` | Number of pipeline micro-batches |

### Parallel Mode Requirement

**This wrapper only works in pipeline-parallel configurations.** MindSpore's parallel mode must be one of:
- `ParallelMode.SEMI_AUTO_PARALLEL`
- `ParallelMode.AUTO_PARALLEL`

Using `STAND_ALONE` or `DATA_PARALLEL` raises `ValueError`.

### Output Tuple

Same 5/7-tensor layout as `MFTrainOneStepCell`. When `local_norm=True`, outputs 7 tensors.

### Errors

| Exception | Trigger |
|---|---|
| `TypeError` | `scale_sense` is not a `Cell` or `Tensor` |
| `ValueError` | `scale_sense` shape is not `(1,)` or `()` |
| `ValueError` | parallel mode is not `SEMI_AUTO_PARALLEL` or `AUTO_PARALLEL` |

---

## Key Differences Between the Two Wrappers

| Aspect | `MFTrainOneStepCell` | `MFPipelineWithLossScaleCell` |
|---|---|---|
| `use_clip_grad` default | `False` | `True` |
| Pipeline micro-batches | not supported | `micro_batch_num` param |
| Parallel mode constraint | none | must be semi/auto parallel |
| Use case | single-device or data-parallel | pipeline parallel |

## See Also

- [[api/mindformer-register]] — registering custom wrappers under `MindFormerModuleType.WRAPPER`
- [[concepts/parallel-training-modes]] — MindSpore parallel mode configuration