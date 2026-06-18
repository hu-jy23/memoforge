---
title: Llama model and configuration
category: api
sources: ["mindformers.models.LlamaConfig.html", "mindformers.models.LlamaForCausalLM.html"]
last_updated: 2026-05-17
confidence: high
---

Llama model implementation with configuration and input/output specifications for causal language modeling.

## LlamaConfig parameters

Configuration class defining Llama model architecture. All parameters optional with sensible defaults.

**Model architecture:**
- `num_layers` (int) — Transformer hidden layers. Default: 32.
- `hidden_size` (int) — Hidden dimension. Default: 4096.
- `num_heads` (int) — Attention heads per layer. Default: 32.
- `n_kv_heads` (int, optional) — Multi-head attention KV heads. Default: `None`.
- `intermediate_size` (int, optional) — Custom FFN dimension. Default: `None` (computed from `hidden_size * ffn_dim_multiplier`).
- `ffn_dim_multiplier` (int, optional) — FFN dimension multiplier. Default: `None`.
- `vocab_size` (int) — Vocabulary size. Default: 32000.
- `max_position_embedding` (int, optional) — Custom max sequence length. Default: `None`.

**Computational precision (critical for Ascend):**
- `param_init_type` (str) — Parameter init dtype. Default: `'float16'`.
- `compute_dtype` (str) — Linear layer compute dtype. Default: `'float16'`.
- `layernorm_compute_type` (str) — LayerNorm compute dtype. Default: `'float32'` (keep at f32).
- `softmax_compute_type` (str) — Softmax compute dtype. Default: `'float32'`.
- `rotary_dtype` (str) — RoPE dtype. Default: `'float32'`.
- `residual_dtype` (str, optional) — Residual connection dtype. Default: `None`.
- `embedding_init_type` (str, optional) — Embedding weight init dtype. Default: `None`.

**Attention mechanisms:**
- `qkv_has_bias` (bool) — QKV linear bias. Default: `False`.
- `qkv_concat` (bool) — Merge QKV linears. Default: `False`.
- `attn_proj_has_bias` (bool) — Attention output projection bias. Default: `False`.
- `use_flash_attention` (bool) — Enable flash attention. Default: `False`.
- `use_ring_attention` (bool) — Enable ring attention. Default: `False`.
- `use_attn_mask_compression` (bool) — Compress attention mask. Default: `False`.
- `use_rope_slice` (bool) — Enable RoPE slicing. Default: `False`.

**Tokens:**
- `bos_token_id` (int) — Begin-of-sequence token. Default: 1.
- `eos_token_id` (int) — End-of-sequence token. Default: 2.
- `pad_token_id` (int) — Padding token. Default: 0.
- `ignore_token_id` (int) — Token to ignore in loss. Default: -100.

**RoPE rotary position encoding:**
- `theta` (float) — Frequency factor. Default: 10000.0.
- `scaling_factor` (float) — Position scaling for length extension. Default: 1.0.
- `extend_method` (str) — Sequence length extension method. Default: `'None'`.

**Inference & generation:**
- `use_past` (bool) — Enable KV cache. Default: `False`.
- `max_decode_length` (int) — Max generated tokens. Default: 1024.
- `repetition_penalty` (float) — Repeated token penalty. Default: 1.0.
- `top_k` (int) — Top-k sampling. Default: 5.
- `top_p` (float) — Nucleus sampling threshold. Default: 1.0.
- `do_sample` (bool) — Use sampling vs greedy. Default: `True`.

**Paged attention (long context):**
- `block_size` (int) — Tokens per block. Default: 16.
- `num_blocks` (int) — Max blocks. Default: 512.

**Parallel training:**
- `parallel_config` — Distributed training config. Default: `default_transformer_config`.
- `parallel_optimizer` (bool) — Optimizer parallelism. Default: `False`.
- `fine_grain_interleave` (int) — Fine-grain multi-copy slices. Default: 1.
- `pp_interleave_num` (int) — Pipeline interleave count. Default: 1.
- `offset` (int) — Transformer layer offset for pipeline stages. Default: 0.

**Other:**
- `batch_size` (int) — Inference batch size. Default: 1.
- `seq_length` (int) — Input sequence length. Default: 2048.
- `is_dynamic` (bool) — Dynamic shape. Default: `False`.
- `fused_rms_norm` (bool) — Fused RMS normalization. Default: `True`.
- `calculate_per_token_loss` (bool) — Loss per token (vs reduced). Default: `False`.

## LlamaForCausalLM

Model class for causal language modeling (next-token prediction). Loss during training, logits during inference.

**Constructor:**
```python
from mindformers.models import LlamaConfig, LlamaForCausalLM
config = LlamaConfig()
network = LlamaForCausalLM(config=config)
```

**Inputs (all Tensor except noted):**
- `input_ids` (int64/int32, shape `[batch, seq_length]`) — Token indices from vocabulary.
- `labels` (int64/int32, shape `[batch, seq_length]`) — Training target labels. Default: `None`.
- `input_position` (int64/int32) — Position indices for incremental inference. Default: `None`.
- `position_ids` (int64/int32) — Position IDs (reserved, not used). Default: `None`.
- `attention_mask` (int64/int32, shape `[batch, seq_length]`) — Padding mask (0=pad). Default: `None`.
- `input_embeds` (float32/float16) — Embedding input (reserved). Default: `None`.
- `init_reset` (bool, shape `[1]`) — Reset KV cache for incremental inference. Default: `Tensor([True])`.
- `batch_valid_length` (int32, shape `[batch_size]`) — Precomputed sequence length per sequence. Default: `None`.
- `block_tables` (int64) — Paged attention mapping table. Default: `None`.
- `slot_mapping` (int32) — Cache slot indices. Default: `None`.
- `loss_mask` (float32/int32) — Token-level loss mask. Default: `None`.
- `gather_index` (int32, shape `[batch_size]`) — Last token position per sequence. Default: `None`.
- `seq_range` (int32, shape `[batch_size]`) — Actual sequence length per sequence. Default: `None`.
- `actual_seq_len` (int32) — For EOD attention mask generation. Default: `None`.
- `q_seq_lens` — Flattened query lengths in parallel decoding. Default: `None`.

**Outputs:**
- Tensor: loss (training mode), logits (inference/eval mode), or logits + tokens + mask (eval mode).

**Example:**
```python
from mindformers import LlamaForCausalLM
network = LlamaForCausalLM.from_pretrained('llama_7b')
```

Cross-reference: [[api/model_base_classes]], [[api/tokenizers]]