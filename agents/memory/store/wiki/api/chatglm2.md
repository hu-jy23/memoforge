---
title: ChatGLM2 model and configuration
category: api
sources: ["mindformers.models.ChatGLM2Config.html", "mindformers.models.ChatGLM2ForConditionalGeneration.html"]
last_updated: 2026-05-17
confidence: high
---

ChatGLM2 model implementation with configuration and input/output specifications.

## ChatGLM2Config parameters

Configuration class defining ChatGLM2 model architecture. All parameters optional with sensible defaults.

**Model architecture:**
- `num_layers` (int) — Transformer hidden layers. Default: 28.
- `hidden_size` (int) — Hidden dimension. Default: 4096.
- `ffn_hidden_size` (int) — FFN layer dimension. Default: 13696.
- `kv_channels` (int) — Key/value channel count. Default: 128.
- `num_attention_heads` (int) — Attention heads per layer. Default: 32.
- `padded_vocab_size` (int) — Vocabulary size. Default: 65024.
- `seq_length` (int) — Input sequence length. Default: 2048.

**Computational precision (critical for Ascend):**
- `param_init_type` (str) — Parameter init dtype. Default: `'float16'`.
- `compute_dtype` (str) — Linear layer compute dtype. Default: `'float16'`.
- `layernorm_compute_type` (str) — LayerNorm compute dtype. Default: `'float32'` (keep at f32).
- `residual_dtype` (str) — Residual connection compute dtype. Default: `'float32'`.
- `rotary_dtype` (str) — RoPE position encoding dtype. Default: `None`.
- `attention_softmax_in_fp32` (bool) — Softmax in float32. Default: `True`.

**Attention mechanisms:**
- `multi_query_attention` (bool) — Enable multi-query attention. Default: `True`.
- `multi_query_group_num` (int) — MQA group count. Default: 2.
- `apply_query_key_layer_scaling` (bool) — Scale query/key. Default: `True`.
- `use_flash_attention` (bool) — Enable flash attention. Default: `False`.
- `use_ring_attention` (bool) — Enable ring attention. Default: `False`.

**Regularization:**
- `hidden_dropout` (float) — Dropout rate. Default: 0.0.
- `attention_dropout` (float) — Attention dropout. Default: 0.0.
- `layernorm_epsilon` (float) — LayerNorm epsilon. Default: 1e-5.

**Inference & generation:**
- `use_past` (bool) — Enable KV cache for autoregressive decoding. Default: `False`.
- `eos_token_id` (int) — End-of-sequence token ID. Default: 2.
- `pad_token_id` (int) — Padding token ID. Default: 0.
- `gmask_token_id` (int) — Global mask token. Default: `None`.
- `bos_token_id` (int) — Begin-of-sequence token. Default: `None`.
- `repetition_penalty` (float) — Penalty for repeated tokens. Default: 1.0.

**Paged attention (for long context):**
- `block_size` (int) — Tokens per block. Default: 16.
- `num_blocks` (int) — Maximum blocks. Default: 128.

**Performance tuning:**
- `enable_high_performance` (bool) — Optimize qkv/ffn parallelism. Default: `False`.
- `mlp_concat` (bool) — Merge two MLPs into one linear. Default: `True`.
- `qkv_concat` (bool) — Merge query/key/value linears. Default: `True`.

## ChatGLM2ForConditionalGeneration

Model class computing loss and logits during training; logits during inference.

**Constructor:**
```python
from mindformers.models import ChatGLM2Config, ChatGLM2ForConditionalGeneration
config = ChatGLM2Config(batch_size=2)
network = ChatGLM2ForConditionalGeneration(config=config)
```

**Inputs (all Tensor except noted):**
- `input_ids` (int32/int64, shape `[batch, seq_length]`) — Token indices from vocabulary.
- `labels` (int32/int64, shape `[batch, seq_length]`) — Training target labels.
- `input_position` (int32/int64, shape `[batch, seq_length]`) — Position indices. Used in incremental inference.
- `attention_mask` — Reserved, not used.
- `input_embeds` — Reserved, not used.
- `init_reset` (bool, shape `[1]`) — Clear previous KV cache in incremental inference. Default: `None`.
- `batch_valid_length` (int32, shape `[batch_size]`) — Length of computed sequence for KV indexing. Default: `None`.
- `prefix_key_values` — Additional KV pairs for long-range dependencies. Default: `None`.
- `block_tables` (int64) — Sequence mapping table for paged attention. Default: `None`.
- `slot_mapping` (int32) — Cache slot indices. Default: `None`.
- `input_mask` — Input portion mask in `input_ids`. Default: `None`.

**Outputs:**
- Tensor containing loss (training) or logits (inference), prediction sequence, input mask.

**Example:**
```python
from mindformers import ChatGLM2ForConditionalGeneration
network = ChatGLM2ForConditionalGeneration.from_pretrained('glm3_6b')
```

Cross-reference: [[api/model_base_classes]], [[api/tokenizers]]