---
title: PreTrainedModel and PretrainedConfig base classes
category: api
sources: ["mindformers.models.PreTrainedModel.html", "mindformers.models.PretrainedConfig.html"]
last_updated: 2026-05-17
confidence: high
---

Base classes for all pretrained models and configurations in MindFormers.

## PreTrainedModel

Base class for all pretrained models. Handles model configuration storage, loading/saving, weight management, and common transformations.

**Key methods:**
- `from_pretrained(pretrained_model_name_or_dir, **kwargs)` — Load model from local path (currently single-machine only). Path must contain `.ckpt` weights and `.yaml` config.
- `save_pretrained(save_directory, save_name='mindspore_model', **kwargs)` — Save model weights and config (single-machine only).
- `can_generate()` — Returns bool indicating if model supports `.generate()` method for sequence generation.
- `post_init()` — Executed after model initialization when all required modules are ready.

**Example:**
```python
from mindformers import AutoModel
import mindspore as ms
ms.set_context(mode=0)
network = AutoModel.from_pretrained('glm3_6b')
network.save_pretrained('./checkpoint_save')
```

## PretrainedConfig

Base class for all model configurations. Handles common configuration parameters and config file I/O.

**Key parameters:**
- `name_or_path` (str) — String passed to `from_pretrained()`. Default: `""`.
- `checkpoint_name_or_path` (str) — Checkpoint file path/name. Default: `None`.
- `mindformers_version` (str) — MindSpore Transformers version. Default: `""`.

**Key methods:**
- `from_dict(config_dict, **kwargs)` — Instantiate config from dictionary.
- `to_dict()` — Export config as dictionary.

**Critical:** Loading config file does NOT load model weights — only configures architecture.

**Example:**
```python
from mindformers.models import LlamaConfig
config = LlamaConfig(num_layers=2, seq_length=1024)
print(config.num_layers)  # 2
```

Cross-reference: [[api/chatglm2]], [[api/llama]], [[api/tokenizers]]