---
title: Wiki Ingest and Maintenance Log
---

# Ingest & Maintenance History

## [2026-05-17] ingest | mindformers.models module

Pages created: 4
Pages updated: 2 (index.md, log.md)

Entities: 
- Base classes: PreTrainedModel, PretrainedConfig, PreTrainedTokenizer, PreTrainedTokenizerFast
- Models: ChatGLM2ForConditionalGeneration, LlamaForCausalLM
- Configs: ChatGLM2Config, LlamaConfig
- Tokenizers: ChatGLM3Tokenizer, ChatGLM4Tokenizer, LlamaTokenizer, LlamaTokenizerFast

Key captures:
- Critical dtype parameters for Ascend (param_init_type, compute_dtype, layernorm_compute_type)
- Input/output tensor shapes and types for model forward passes
- Special token configurations per model/tokenizer variant
- Paged attention and KV cache parameters for long-context inference
- RoPE and attention mechanism tuning options
## [2026-05-17] init | Starter Agent bootstrap — topics=installation,advanced_development,core_trainer,dataset,generation,pipeline_pet,models,modules_attention,tools_config pages_created=30

## [2026-05-17] init | Starter Agent bootstrap — topics=tools_config pages_created=3

## [2026-05-17] delete | page=concepts/raw_tools_config — stale Haiku fallback, superseded by api/mindformer-config, api/mindformer-register, api/mf-train-wrappers
## [2026-05-17] update | page=api/training_callbacks task_id=custom-callback-norm-lr-01 — appended Custom Callback Registration section: MindFormerRegister decorator, YAML instantiation prerequisite, MFTrainOneStepCell net_outputs layout ([0..4], global_norm conditions), two-path LR extraction pattern, step=0 guard, OSError guard
## [2026-05-17] write-back | task_id=custom-callback-norm-lr-01 status=pass steps=1,4,5
## [2026-05-29] write-back | task_id=custom-callback-norm-lr-01 status=pass steps=1,4,5 — upgraded sample to evidence-backed learning; added notes/mf-train-wrappers observations
