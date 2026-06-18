---
title: MindFormerConfig — YAML/Dict Configuration Class
category: api
sources: ["mindformers.tools.MindFormerConfig.html"]
last_updated: 2026-05-17
confidence: high
---

`MindFormerConfig` is a `dict` subclass that loads MindFormers configuration from YAML files or plain dicts and exposes values via attribute (dot) access.

## Class Signature

```python
class mindformers.tools.MindFormerConfig(*args, **kwargs)
```

`args` and `kwargs` accept either a YAML file path (str) or a configuration dict. Both positional and keyword styles are supported.

## Construction Patterns

```python
from mindformers.tools import MindFormerConfig

# From a YAML file path
cfg = MindFormerConfig('./run_llama.yaml')
print(cfg.model)          # dot-access works like attribute access

# From an inline dict
cfg = MindFormerConfig(**dict(model=dict(model_config=dict(type='LlamaConfig'))))
print(cfg.model)          # {'model_config': {'type': 'LlamaConfig'}}
```

## Methods

### `merge_from_dict(options: dict)`

Merges additional key-value pairs into the existing config. Keys use **dot-notation** to address nested fields.

```python
options = {'model.arch': 'LlamaForCausalLM'}
cfg.merge_from_dict(options)
# Result: cfg.model == {'model_config': {'type': 'LlamaConfig'}, 'arch': 'LlamaForCausalLM'}
```

**Pitfall:** the dot-notation key `'model.arch'` inserts into the *existing* `model` dict; it does not replace the whole `model` key. Passing `{'model': {'arch': 'X'}}` would overwrite the entire `model` dict.

## Usage Notes

- Because `MindFormerConfig` is a `dict`, it can be passed anywhere a dict is expected (e.g. `get_instance_from_cfg`).
- Nested values are also accessible as attributes recursively.
- Standard `dict` methods (`update`, `keys`, `items`) remain available.

## See Also

- [[api/mindformer-register]] — instantiating objects from a `MindFormerConfig` dict via `get_instance_from_cfg`
- [[config/yaml-config-fields]] — YAML field conventions