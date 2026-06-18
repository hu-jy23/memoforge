---
title: MindFormerRegister and MindFormerModuleType — Registration System
category: api
sources: ["mindformers.tools.register.MindFormerRegister.html", "mindformers.tools.register.MindFormerModuleType.html"]
last_updated: 2026-05-17
confidence: high
---

`MindFormerRegister` is MindFormers' central class registry; `MindFormerModuleType` is the enum of valid registry namespaces. All methods on `MindFormerRegister` are classmethods — never instantiate it.

## MindFormerModuleType Enum Values

| Enum name | String value | Meaning |
|---|---|---|
| `CALLBACK` | `'callback'` | Callback functions |
| `CONFIG` | `'config'` | Config classes |
| `CONTEXT` | `'context'` | Context managers |
| `DATASET` | `'dataset'` | Dataset classes |
| `DATASET_LOADER` | `'dataset_loader'` | Dataset loaders |
| `DATASET_SAMPLER` | `'dataset_sampler'` | Dataset samplers |
| `DATA_HANDLER` | `'data_handler'` | Data processors |
| `ENCODER` | `'encoder'` | Encoders |
| `FEATURE_EXTRACTOR` | `'feature_extractor'` | Feature extractors |
| `LOSS` | `'loss'` | Loss functions |
| `LR` | `'lr'` | LR schedulers |
| `MASK_POLICY` | `'mask_policy'` | Mask policies |
| `METRIC` | `'metric'` | Evaluation metrics |
| `MODELS` | `'models'` | Model classes |
| `OPTIMIZER` | `'optimizer'` | Optimizers |
| `PIPELINE` | `'pipeline'` | Pipeline interfaces |
| `PROCESSOR` | `'processor'` | Processors |
| `TOKENIZER` | `'tokenizer'` | Tokenizers |
| `TOOLS` | `'tools'` | Utility tools |
| `TRAINER` | `'trainer'` | Trainer interfaces |
| `TRANSFORMS` | `'transforms'` | Data transforms |
| `WRAPPER` | `'wrapper'` | Training wrappers |

The string values are what appear in YAML `type:` fields. **Use the enum constants in Python code**, not the raw strings.

## Registering a Class

### Via decorator (preferred)

```python
from mindformers.tools import MindFormerRegister, MindFormerModuleType

@MindFormerRegister.register(MindFormerModuleType.CONFIG)
class MyConfig:
    def __init__(self, param):
        self.param = param
```

### Via method call

```python
MindFormerRegister.register_cls(
    register_class=MyConfig,
    module_type=MindFormerModuleType.CONFIG
)
```

### `register` / `register_cls` parameters

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `module_type` | `MindFormerModuleType` | `TOOLS` | Registry namespace |
| `alias` | `str` | `None` | Alternate lookup name |
| `legacy` | `bool` | `True` | Whether to keep old class in registry |
| `search_names` | `str\|tuple\|list\|set` | `None` | Additional lookup names |

## Querying the Registry

### Check existence

```python
MindFormerRegister.is_exist(
    module_type=MindFormerModuleType.CONFIG,
    class_name="MyConfig"    # omit to check if module_type itself exists
)
# Returns: bool
```

### Retrieve class

```python
cls = MindFormerRegister.get_cls(
    module_type=MindFormerModuleType.CONFIG,
    class_name="MyConfig"
)
# Raises ValueError if module_type or class_name not found
```

### Instantiate by name

```python
instance = MindFormerRegister.get_instance(
    module_type=MindFormerModuleType.CONFIG,
    class_name="MyConfig",   # required (cannot be None)
    param=0                  # kwargs forwarded to __init__
)
```

### Instantiate from config dict

```python
instance = MindFormerRegister.get_instance_from_cfg(
    cfg={'type': 'MyConfig', 'param': 0},   # 'type' key is mandatory
    module_type=MindFormerModuleType.CONFIG,
    default_args=None        # optional dict merged before cfg
)
```

**Critical:** `cfg` **must** contain the key `'type'` (string class name). Missing `'type'` raises `KeyError`. This is the lookup key used in YAML configs.

## Errors

| Exception | Trigger |
|---|---|
| `ValueError` | `class_name=None` in `get_instance` |
| `ValueError` | `class_name` or `module_type` not in registry |
| `TypeError` | `cfg` is not a dict in `get_instance_from_cfg` |
| `KeyError` | `cfg` or `default_args` missing `'type'` key |
| `TypeError` | `default_args` is not a dict or `None` |

## See Also

- [[api/mindformer-config]] — `MindFormerConfig` dict used as `cfg` arg
- [[config/yaml-config-fields]] — how `type:` fields in YAML map to registry lookups