---
title: MultiModalToTextPipeline — Multimodal-to-Text Inference
category: api
sources: ["mindformers.pipeline.MultiModalToTextPipeline.html"]
last_updated: 2026-05-17
confidence: high
---

Pipeline for multimodal inputs (image + text) to text generation tasks.

## Constructor

```python
class mindformers.pipeline.MultiModalToTextPipeline(model, processor=None, **kwargs)
```

| Parameter | Type | Requirement | Purpose |
|-----------|------|-------------|---------|
| `model` | PretrainedModel or Model | Required | Must be an instance of a PretrainedModel subclass |
| `processor` | BaseXModalToTextProcessor, optional | Optional | Processor for multimodal inputs; None uses model defaults |
| `**kwargs` | Any | Optional | Task-specific options (passed to parent pipeline) |

## Returns

A `MultiModalToTextPipeline` instance for inference.

## Exceptions

- **TypeError:** Model or processor type is incorrect
- **ValueError:** Model not in supported list for this task

## Key Behavior

- Accepts mixed multimodal inputs (images + text)
- Uses processor to prepare inputs (if provided)
- Returns generated text
- Inherits standard pipeline interface (e.g., `__call__()` for inference)

## Common Usage Pattern

```python
from mindformers import pipeline

pipe = pipeline(
    task='multi_modal_to_text_generation',
    model='your-multimodal-model',
    image_processor=your_processor
)

# Then: output = pipe(image_tensor, text_prompt)
```

## Typical Supported Models

Models with both vision and language encoders (e.g., LLaVA, Flamingo architectures).

References: [[api/pipeline_function]]