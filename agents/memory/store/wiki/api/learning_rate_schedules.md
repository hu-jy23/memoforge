---
title: Learning Rate Schedules
category: api
sources: ["mindformers.core.ConstantWarmUpLR.html", "mindformers.core.ConstantWithCoolDownLR.html", "mindformers.core.CosineAnnealingLR.html", "mindformers.core.CosineAnnealingWarmRestarts.html", "mindformers.core.CosineWithRestartsAndWarmUpLR.html", "mindformers.core.CosineWithWarmUpLR.html", "mindformers.core.LinearWithWarmUpLR.html", "mindformers.core.PolynomialWithWarmUpLR.html"]
last_updated: 2026-05-17
confidence: high
---

Learning rate schedulers for MindFormers training. Each implements a specific schedule strategy to balance training stability and convergence speed.

## Common Pattern

All schedules take `global_step` (int) as input and return a learning rate (float). They're passed to the optimizer's `learning_rate` parameter.

## Schedules

### LinearWithWarmUpLR

Linear warmup followed by linear decay.

```python
class LinearWithWarmUpLR(
    learning_rate,           # Target LR after warmup
    total_steps,             # Total training steps
    warmup_steps=None,       # Number of warmup steps
    warmup_lr_init=0.0,      # Initial LR at step 0
    warmup_ratio=None        # Warmup as fraction of total_steps
)
```

Formula:
- Warmup: η_t = η_warmup + t × (η_base - η_warmup) / warmup_steps
- Decay: η_t = η_base - t × (η_base - η_end) / (total_steps - warmup_steps)

Use when: Simple, stable training. Default for most LLM fine-tuning.

### CosineWithWarmUpLR

Linear warmup followed by cosine annealing decay.

```python
class CosineWithWarmUpLR(
    learning_rate,           # Target LR after warmup
    warmup_steps=0,
    total_steps=None,
    num_cycles=0.5,          # Fractional cosine periods (0.5 = half period)
    lr_end=0.0,              # Final LR
    warmup_lr_init=0.0,
    warmup_ratio=None,
    decay_steps=None,
    decay_ratio=None
)
```

Use when: Smoother convergence in later training stages. Common in transformer pretraining.

### CosineAnnealingLR

Pure cosine annealing, no warmup.

```python
class CosineAnnealingLR(
    base_lr,                 # Maximum LR
    t_max,                   # Period length (steps)
    eta_min=0.0              # Minimum LR
)
```

Use when: Warmup handled elsewhere. Simple periodic schedule.

### CosineAnnealingWarmRestarts

Cosine annealing with periodic warm restarts (SGDR pattern).

```python
class CosineAnnealingWarmRestarts(
    base_lr,                 # Maximum LR
    t_0,                     # First restart period
    t_mult=1,                # Multiplier for next restart period
    eta_min=0.0
)
```

At each restart, LR jumps back to base_lr. Restart periods grow by t_mult.

Use when: Exploring multiple local minima. Helps escape shallow minima.

### CosineWithRestartsAndWarmUpLR

Warmup + cosine decay with periodic restarts.

```python
class CosineWithRestartsAndWarmUpLR(
    learning_rate,
    warmup_steps=None,
    total_steps=None,
    num_cycles=1.0,          # Number of cosine periods
    lr_end=0.0,
    warmup_lr_init=0.0,
    warmup_ratio=None,
    decay_steps=None
)
```

Use when: DeepSeek-style scheduling. Multiple restart cycles in single training run.

### ConstantWarmUpLR

Linear warmup to a constant learning rate (no decay).

```python
class ConstantWarmUpLR(
    learning_rate,
    warmup_steps=None,
    warmup_lr_init=0.0,
    warmup_ratio=None,
    total_steps=None
)
```

Use when: Constant LR after warmup. Useful for fine-tuning with fixed LR.

### ConstantWithCoolDownLR

Piecewise schedule: warmup → hold → cosine decay → final constant (DeepSeek-V3 style).

```python
class ConstantWithCoolDownLR(
    learning_rate,           # Held during keep phase
    warmup_steps=None,
    warmup_lr_init=0.0,
    keep_steps=0,            # Steps at constant LR after warmup
    decay_steps=None,        # Cosine decay duration
    decay_ratio=None,
    total_steps=None,
    num_cycles=0.5,
    lr_end1=0.0,             # LR after decay phase
    final_steps=0,           # Steps at lr_end2
    lr_end2=None             # Final constant LR (=lr_end1 if None)
)
```

Use when: Complex schedule with multiple phases. Modern LLM training (DeepSeek-V3).

### PolynomialWithWarmUpLR

Linear warmup followed by polynomial decay.

```python
class PolynomialWithWarmUpLR(
    learning_rate,
    total_steps,
    warmup_steps=None,
    lr_end=1e-7,
    power=1.0,               # Polynomial exponent
    warmup_lr_init=0.0,
    warmup_ratio=None,
    decay_steps=None
)
```

Formula (decay): η_t = η_end + (η_start - η_end) × (1 - (t - warmup_steps) / decay_steps)^power

Use when: Gradual late-training decay. power > 1 = faster early decay.

## Usage with Optimizer

```python
from mindformers.core import LinearWithWarmUpLR, AdamW

schedule = LinearWithWarmUpLR(
    learning_rate=1e-4,
    total_steps=10000,
    warmup_steps=1000
)

optim = AdamW(params=net.trainable_params(), learning_rate=schedule)
```

## Notes

- Use `warmup_steps` (absolute) OR `warmup_ratio` (fraction), not both
- Use `decay_steps` (absolute) OR `decay_ratio` (fraction), not both
- All schedules are callable: `lr = schedule(ms.Tensor(step))`
- [[api/optimizer_adamw]] can accept any schedule via `learning_rate` parameter
- [[api/learning_rate_wise_layer]] wraps schedules with per-layer scaling