---
title: Layer-wise Learning Rate Scaling
category: api
sources: ["mindformers.core.LearningRateWiseLayer.html"]
last_updated: 2026-05-17
confidence: high
---

Apply per-layer learning rate scaling on top of any base learning rate schedule.

## Class Signature

```python
class LearningRateWiseLayer(
    base_lr,       # Base learning rate schedule or scheduler
    lr_scale       # Scalar multiplier for this layer's learning rate
)
```

## Parameters

- **base_lr** (LearningRateSchedule) — Any learning rate schedule (e.g., LinearWithWarmUpLR, CosineWithWarmUpLR). Can also be a float (constant)
- **lr_scale** (float) — Multiplier applied to base_lr. E.g., 0.5 = half learning rate, 2.0 = double learning rate

## Formula

```
η_{t,layer} = η_base(t) × lr_scale
```

where η_base(t) is the learning rate from the base schedule at step t.

## Use Cases

### Deeper Layers Learn More Slowly

Often, lower layers in transformer models (closer to input) need lower learning rates than upper layers (closer to output) to avoid catastrophic forgetting.

```python
from mindformers.core import LinearWithWarmUpLR, LearningRateWiseLayer

# Base schedule
base_schedule = LinearWithWarmUpLR(
    learning_rate=1e-4,
    total_steps=10000,
    warmup_steps=1000
)

# Lower layers (embeddings, early transformer blocks)
embedding_lr = LearningRateWiseLayer(base_schedule, lr_scale=0.1)

# Upper layers (later transformer blocks)
upper_lr = LearningRateWiseLayer(base_schedule, lr_scale=1.0)

# Use in parameter groups
optim = AdamW([
    {'params': embedding_params, 'lr': embedding_lr},
    {'params': upper_params, 'lr': upper_lr}
])
```

### Fine-tuning Pre-trained Models

Freeze or reduce updates to early layers:

```python
pretrained_schedule = LinearWithWarmUpLR(learning_rate=1e-5, ...)
task_schedule = LearningRateWiseLayer(pretrained_schedule, lr_scale=0.01)

# Old layers update very slowly; new classification head updates faster
optim = AdamW([
    {'params': old_params, 'lr': task_schedule},
    {'params': new_head, 'lr': pretrained_schedule}  # 100x faster
])
```

## Example

```python
import mindspore as ms
from mindformers.core import LinearWithWarmUpLR, LearningRateWiseLayer

ms.set_context(mode=ms.GRAPH_MODE)

total_steps = 20
warmup_steps = 10
learning_rate = 0.005

base_lr = LinearWithWarmUpLR(
    learning_rate=learning_rate,
    warmup_steps=warmup_steps,
    total_steps=total_steps
)

# Scale to 0.5 of base LR
scaled_lr = LearningRateWiseLayer(base_lr, 0.5)

print(scaled_lr(ms.Tensor(1)))   # 0.00025 (0.0005 × 0.5)
print(scaled_lr(ms.Tensor(15)))  # 0.00125 (0.0025 × 0.5)
```

## Notes

- Can be stacked with any base schedule: [[api/learning_rate_schedules]]
- Use [[api/optimizer_adamw]] parameter groups for per-layer scheduling
- Common in vision transformers and large language models for stable fine-tuning