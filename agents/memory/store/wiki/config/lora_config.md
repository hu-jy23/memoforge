---
title: LoraConfig — LoRA Fine-Tuning Parameters
category: config
sources: ["mindformers.pet.pet_config.LoraConfig.html"]
last_updated: 2026-05-17
confidence: high
---

Configuration class for LoRA fine-tuning parameters. Create a `LoraConfig` instance and pass it to [[api/lora_model]] to wrap a base model with LoRA adapters.

## Constructor Parameters

| Parameter | Type | Default | Constraints | Purpose |
|-----------|------|---------|-------------|---------|
| `lora_rank` | int | 8 | r > 0 | Rank of low-rank matrices A, B |
| `lora_alpha` | int | 16 | α > 0 | Scaling constant; effective rank = lora_alpha / lora_rank |
| `lora_dropout` | float | 0.01 | 0 ≤ p < 1 | Dropout probability on LoRA outputs |
| `lora_a_init` | str | `'normal'` | 'normal' or other strategy | Initialization method for A matrix |
| `lora_b_init` | str | `'zero'` | 'zero' or other strategy | Initialization method for B matrix (typically zero) |
| `param_init_type` | str | None | e.g., 'float16', 'float32' | Data type for LoRA tensors; inherits from base layer if None |
| `compute_dtype` | str | None | e.g., 'float16', 'float32' | Computation dtype for LoRA ops; inherits from base layer if None |
| `target_modules` | str | None | regex pattern | Regex to match layer names to apply LoRA (e.g., `'.*wq\|.*wk\|.*wv\|.*wo'` for attention weights) |
| `exclude_layers` | str | None | regex pattern | Regex for layers to exclude from LoRA |
| `freeze_include` | List[str] | None | module name list | Explicitly freeze these modules in base model |
| `freeze_exclude` | List[str] | None | module name list | Do not freeze these modules; takes precedence over freeze_include on conflicts |

## Example

```python
from mindformers.pet.pet_config import LoraConfig

config = LoraConfig(
    target_modules='.*wq|.*wk|.*wv|.*wo',  # Attention heads in Llama
    lora_rank=8,
    lora_alpha=16,
    lora_dropout=0.01
)
```

Output: `{'pet_type': 'lora', 'lora_rank': 8, 'lora_alpha': 16, ...}`

## Common Patterns

**Llama attention:** `'.*wq|.*wk|.*wv|.*wo'` (query, key, value, output projections)

**Freezing logic:** If both `freeze_include` and `freeze_exclude` contain patterns that match the same module, that module will **not** be frozen.

References: [[api/lora_model]], [[concepts/lora_pet_overview]]