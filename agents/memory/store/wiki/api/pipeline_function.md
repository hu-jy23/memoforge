---
title: pipeline() — Inference Pipeline Factory
category: api
sources: ["mindformers.pipeline.html"]
last_updated: 2026-05-17
confidence: high
---

Factory function that constructs an inference pipeline for a supported task and model.

## Function Signature

```python
mindformers.pipeline(
    task=None,
    model=None,
    tokenizer=None,
    image_processor=None,
    audio_processor=None,
    backend='ms',
    **kwargs
) → Pipeline instance
```

## Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `task` | str, optional | None | Task type: 'text_generation', 'image_to_text_generation', 'multi_modal_to_text_generation' |
| `model` | str, PreTrainedModel, Model, or Tuple[str, str], optional | None | Model for the task (can be a model name string or instance) |
| `tokenizer` | PreTrainedTokenizerBase, optional | None | Tokenizer for text processing |
| `image_processor` | BaseImageProcessor, optional | None | Image processor for vision tasks |
| `audio_processor` | BaseAudioProcessor, optional | None | Audio processor for speech tasks |
| `backend` | str, optional | 'ms' | Inference backend; currently only 'ms' (MindSpore) is supported |
| `**kwargs` | Any | — | Task-specific kwargs (see task-specific pipeline documentation) |

## Returns

A pipeline instance for the specified task (e.g., [[api/multimodal_to_text_pipeline]])

## Exceptions

- **KeyError:** Model or task not in supported list

## Supported Tasks

- `'text_generation'` → TextGenerationPipeline
- `'image_to_text_generation'` → ImageToTextPipeline
- `'multi_modal_to_text_generation'` → [[api/multimodal_to_text_pipeline]]

## Constraints

- Only MindSpore backend ('ms') is currently supported
- All parameters must be from the supported lists (task names, model architectures)

References: [[api/multimodal_to_text_pipeline]]