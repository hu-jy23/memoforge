---
title: AdamW Optimizer
category: api
sources: ["mindformers.core.AdamW.html"]
last_updated: 2026-05-17
confidence: high
---

AdamW optimizer with weight decay support for stable training on Ascend NPUs, with advanced features like fused operations and optimizer state swapping.

## Class Signature

```python
class AdamW(
    params,
    learning_rate=1e-3,
    betas=(0.9, 0.999),
    eps=1e-8,
    weight_decay=0.0,
    use_fused=False,
    amsgrad=False,
    maximize=False,
    swap=False
)
```

## Parameters

- **params** (Union[list[Parameter], list[dict]]) — Parameter groups or parameter list. When using dicts, keys can be:
  - `"params"` (required): List of Parameters in this group
  - `"lr"` (optional): Learning rate for this group. Falls back to optimizer's `learning_rate` if not set. Supports both fixed and dynamic LR schedules
  - `"weight_decay"` (optional): Weight decay for this group. Falls back to optimizer's `weight_decay`. Can be a constant or Cell (for dynamic decay)
  - `"order_params"` (optional): Parameter ordering for performance. If set, other keys in that dict are ignored

- **learning_rate** (Union[float, int, Tensor, Iterable, LearningRateSchedule]) — Default: 1e-3
  - float/int: Fixed learning rate (must be ≥ 0)
  - Tensor: Scalar (fixed) or 1-D vector (dynamic, step i uses element i)
  - Iterable: Dynamic, step i uses element i
  - LearningRateSchedule: Called with step count during training

- **betas** (tuple(float)) — Momentum decay rates for moment estimates. Each in (0.0, 1.0). Default: (0.9, 0.999)

- **eps** (float) — Denominator epsilon for numerical stability. Must be > 0. Default: 1e-8

- **weight_decay** (Union[float, int, Cell]) — L2 penalty strength. Default: 0.0
  - float/int: Fixed decay (≥ 0)
  - Cell: Dynamic decay, called with step count

- **use_fused** (bool) — Enable fused operators for performance. Default: False

- **amsgrad** (bool) — Use AMSGrad variant (keeps max of historical squared gradients instead of exponential average). Improves convergence in some cases. Only works with `use_fused=True`. Default: False

- **maximize** (bool) — Maximize objective instead of minimize (for reward optimization). Only works with `use_fused=True`. Default: False

- **swap** (bool) — Enable optimizer state swapping: offload momentum/velocity to CPU instead of keeping on NPU. Requires environment variable `MS_DEV_RUNTIME_CONF="switch_inline:False"`. Default: False

## Usage Example

```python
import mindspore as ms
from mindformers import AutoModel
from mindformers.core.optim import AdamW

# Single learning rate for all parameters
optim = AdamW(params=net.trainable_params(), learning_rate=0.001)

# Parameter groups with different learning rates and decay
layernorm_params = [p for p in net.trainable_params() if 'norm' in p.name]
other_params = [p for p in net.trainable_params() if 'norm' not in p.name]

group_params = [
    {'params': layernorm_params, 'weight_decay': 0.01},
    {'params': other_params, 'lr': 0.01},
    {'order_params': net.trainable_params()}  # sets parameter order
]
optim = AdamW(group_params, learning_rate=0.1, weight_decay=0.0)
```

## Common Errors

- **ValueError: betas[0], betas[1] not in (0.0, 1.0)** — Momentum decay rates must be strictly between 0 and 1 (exclusive)
- **ValueError: eps <= 0** — Epsilon must be positive
- **ValueError: weight_decay < 0** — Weight decay cannot be negative
- **TypeError: learning_rate not int/float/Tensor/Iterable/LearningRateSchedule** — Use supported LR types only

## Notes

- [[config/training_config]] describes where to configure AdamW in training YAML
- Dynamic learning rate and weight decay via Tensor/Cell are useful with [[api/learning_rate_schedules]]
- Parameter grouping with different `lr` and `weight_decay` per group is critical for stable large-model training