---
title: MindFormers Models Wiki Index
---

# Wiki Index

## API Reference

- [[api/model_base_classes]] — PreTrainedModel, PretrainedConfig base classes; inheritance pattern
- [[api/chatglm2]] — ChatGLM2 model and ChatGLM2Config; 28-layer architecture; attention/precision tuning
- [[api/llama]] — Llama model and LlamaConfig; 32-layer architecture; RoPE, parallel training
- [[api/tokenizers]] — Tokenizer base classes and ChatGLM3/4, Llama slow/fast variants

## Categories

**api/** — API signatures, parameter semantics, behavioral quirks
**config/** — YAML config fields, valid values, runtime flags (future)
**concepts/** — Terminology, hardware abstractions, architecture concepts (future)
**errors/** — Error patterns, root causes, fixes (future)
**workflows/** — Multi-step procedures, training sequences (future)
## Api
- [[api/optimizer_adamw]] — AdamW optimizer with weight decay support for stable training on Ascend NPUs, with advanced features like fused operations and optimizer sta
- [[api/learning_rate_schedules]] — Learning rate schedulers for MindFormers training. Each implements a specific schedule strategy to balance training stability and convergenc
- [[api/training_callbacks]] — Callback functions invoked during training to monitor progress, save checkpoints, evaluate, and profile performance.
- [[api/cross_entropy_loss]] — Cross-entropy loss for classification and language modeling on Ascend NPUs, with per-token masking and distributed training support.
- [[api/training_metrics]] — Evaluation metrics for monitoring model performance during and after training.
- [[api/learning_rate_wise_layer]] — Apply per-layer learning rate scaling on top of any base learning rate schedule.
- [[api/causal_language_model_dataset]] — CausalLanguageModelDataset constructs pretraining data pipelines for causal language models, handling tokenized sequences, EOD tokens, and d
- [[api/keyword_gen_dataset]] — KeyWordGenDataset handles conditional sequence generation tasks (e.g., headline/keyword generation from source text) with phase-dependent ou
- [[api/multi_turn_dataset]] — MultiTurnDataset constructs dialogue training pipelines for multi-turn conversation models, handling dialogue history, response targets, and
- [[api/generation_config]] — Configuration class that holds all parameters controlling autoregressive text generation behaviour in MindFormers models.
- [[api/generation_mixin]] — Mixin class that provides autoregressive text generation methods for [[api/mindformers_pretrained_model]]. Models inherit this to gain `.gen
- [[api/mindformers_pretrained_model]] — `PreTrainedModel` is the base model abstraction referenced by generation-related APIs; this page routes agents to [[api/model_base_classes]] until a fuller API page is consolidated.
- [[api/lora_model]] — Wraps a pre-trained base model with LoRA adapters for parameter-efficient fine-tuning.
- [[api/pipeline_function]] — Factory function that constructs an inference pipeline for a supported task and model.
- [[api/multimodal_to_text_pipeline]] — Pipeline for multimodal inputs (image + text) to text generation tasks.
- [[api/model_base_classes]] — Base classes for all pretrained models and configurations in MindFormers.
- [[api/chatglm2]] — ChatGLM2 model implementation with configuration and input/output specifications.
- [[api/llama]] — Llama model implementation with configuration and input/output specifications for causal language modeling.
- [[api/tokenizers]] — Tokenizer base classes and model-specific implementations. Slow tokenizers use SentencePiece/BPE; fast tokenizers wrap HuggingFace's Rust im
- [[api/op_parallel_config]] — Configuration class for setting operator-level parallelism modes in MindFormers distributed training.
- [[api/common_validation_commands]] — Syntax and structure validation commands for development and testing.

## Concepts
- [[concepts/hardware-requirements]] — Minimum and recommended hardware and software configurations for running MindSpore Transformers.
- [[concepts/generation_strategy]] — MindFormers supports two fundamentally different decoding strategies that trade speed and diversity for determinism.
- [[concepts/lora_pet_overview]] — LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning method that adds trainable low-rank matrices to selected layers while freezi
- [[concepts/paged_attention]] — Paged attention is a generation-time attention memory-management concept referenced by MindFormers generation APIs; this page is a placeholder until task evidence or official docs are consolidated.
- [[concepts/parallel-training-modes]] — Parallel training modes describe how MindSpore/MindFormers distributes model, data, pipeline, and optimizer work across devices; use [[config/parallel_context_configuration]] for current local rules.

## Config
- [[config/version-compatibility]] — MindSpore Transformers version pairs with required MindSpore, CANN, and Ascend firmware releases.
- [[config/environment-variables]] — Environment variables that control runtime behaviour, logging, debugging, and device management in MindSpore Transformers.
- [[config/lora_config]] — Configuration class for LoRA fine-tuning parameters. Create a `LoraConfig` instance and pass it to [[api/lora_model]] to wrap a base model w
- [[config/mindformers_tokenizer_config]] — MindFormers tokenizer config controls tokenizer construction and dataset preprocessing behavior for text and dialogue tasks.
- [[config/parallel_context_configuration]] — MindSpore auto-parallel configuration is injected through the `parallel` block in training configs.
- [[config/training_config]] — Training config is the top-level YAML structure that wires optimizer, callbacks, wrappers, datasets, context, and parallel settings into a MindFormers run.
- [[config/yaml-config-fields]] — YAML config fields are the structured configuration keys consumed by MindFormers builders, registries, callbacks, wrappers, and runtime context setup.

## Workflows
- [[workflows/installation-steps]] — Step-by-step installation of MindSpore Transformers and its dependencies on Ascend hardware.
- [[workflows/docker-setup]] — Build a Docker image containing MindSpore Transformers with all dependencies pre-installed, using multi-stage build to minimize image size.
- [[workflows/config_change_validation]] — Before adding any code, config field, script argument, environment variable, or structured change, trace the full upstream and downstream path.
- [[workflows/remote_monitoring]] — Remote monitoring watches training jobs running on ModelArts from a development machine that can read OBS and upload to WandB.
- [[workflows/training_entry_points]] — The MindFormers codebase is organized around a single training entry point: `run_mindformer.py`.

## Api
- [[api/mindformer-config]] — `MindFormerConfig` is a `dict` subclass that loads MindFormers configuration from YAML files or plain dicts and exposes values via attribute
- [[api/mindformer-register]] — `MindFormerRegister` is MindFormers' central class registry; `MindFormerModuleType` is the enum of valid registry namespaces. All methods on
- [[api/mf-train-wrappers]] — MindFormers provides two training-step wrappers that replace MindSpore's bare `TrainOneStepCell`: `MFTrainOneStepCell` for standard data-par
