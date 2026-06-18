---
title: LoRA and PET (Parameter-Efficient Tuning) Overview
category: concepts
sources: ["mindformers.pet.html", "mindformers.pet.models.LoraModel.html", "mindformers.pet.pet_config.PetConfig.html"]
last_updated: 2026-05-17
confidence: high
---

LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning method that adds trainable low-rank matrices to selected layers while freezing base model weights.

**PET (Parameter-Efficient Tuning)** is the family of fine-tuning techniques in MindFormers. Currently only LoRA is supported (`pet_type='lora'`).

## Key Concepts

**LoRA mechanism:** Instead of fine-tuning all weights in a layer, LoRA adds a pair of low-rank matrices (A and B) with rank r:
- A matrix: initialized (default: Gaussian normal)
- B matrix: initialized to zero (trainable result starts at identity)
- Adapter output: `W_new = W_base + (B @ A) * alpha/rank`

**Advantages:**
- Dramatically fewer trainable parameters (typically 0.1–1% of base model)
- Enables multi-task adapters (store multiple LoRA weights for different tasks)
- Faster inference when using original weights only

**Layer targeting:** Use regex patterns to select which layers receive LoRA (e.g., `'.*wq|.*wk|.*wv|.*wo'` targets attention matrices in Llama).

**Freezing strategy:** Control which base model weights freeze via `freeze_include` / `freeze_exclude`. By default, LoRA adds trainable layers while base model remains frozen.

References: [[api/lora_model]], [[config/lora_config]], [[api/pipeline_function]]