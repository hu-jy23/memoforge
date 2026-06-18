---
title: LoraModel — LoRA Wrapper for Base Models
category: api
sources: ["mindformers.pet.models.LoraModel.html"]
last_updated: 2026-05-17
confidence: high
---

Wraps a pre-trained base model with LoRA adapters for parameter-efficient fine-tuning.

## Constructor

```python
class mindformers.pet.models.LoraModel(config, base_model)
```

| Parameter | Type | Purpose |
|-----------|------|---------|
| `config` | LoraConfig | LoRA configuration object (see [[config/lora_config]]) |
| `base_model` | PreTrainedModel | The model to fine-tune (e.g., LlamaForCausalLM) |

## Behavior

- Scans the base model for layers matching `config.target_modules` regex
- Replaces matched layers with LoRA-wrapped versions (LoRADense)
- Applies dropout to LoRA outputs
- Freezes base model weights; only LoRA matrices are trainable
- Input/output signatures match the original base model (transparent wrapper)

## Example

```python
import mindspore as ms
from mindformers.pet import LoraModel, LoraConfig
from mindformers.models import LlamaConfig, LlamaForCausalLM

ms.set_context(mode=0)
config = LlamaConfig(num_layers=2)
lora_config = LoraConfig(target_modules='.*wq|.*wk|.*wv|.*wo')

base_model = LlamaForCausalLM(config)
lora_model = LoraModel(lora_config, base_model)

# lora_model.lora_model now contains the wrapped architecture
# with LoRADense layers in attention blocks
print(lora_model.lora_model)
```

## Key Properties

- **Input:** Same as base model (tensors matching its input signature)
- **Output:** Same as base model (predictions are unchanged in shape/type)
- **Trainable parameters:** Only LoRA A and B matrices + any unfrozen layers specified in `freeze_exclude`
- **Inference:** Can use either LoRA weights alone (adapter) or merge LoRA back into base weights

References: [[config/lora_config]], [[concepts/lora_pet_overview]]