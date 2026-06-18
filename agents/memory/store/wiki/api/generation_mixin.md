---
title: GenerationMixin — Text Generation Methods
category: api
sources: ["mindformers.generation.GenerationMixin"]
last_updated: 2026-05-17
confidence: high
---

Mixin class that provides autoregressive text generation methods for [[api/mindformers_pretrained_model]]. Models inherit this to gain `.generate()`, `.chat()`, and `.infer()` capabilities.

## Core Methods

### `generate(input_ids, generation_config=None, logits_processor=None, streamer=None, seed=None, **kwargs)`

Generate token sequences given input token IDs.

**Parameters:**
- `input_ids` (List[str] | List[List[str]]) — Single or batch of token index lists. All lists in a batch must have same length.
- `generation_config` (GenerationConfig, optional) — Base config; kwargs override its values. If None, uses model's default. See [[api/generation_config]].
- `logits_processor` (LogitsProcessorList, optional) — Custom logit processors (advanced). Supplements default ones built from parameters.
- `streamer` (TextStreamer, optional) — Streamer for incremental output.
- `seed` (int, optional) — Random seed for sampling.
- `**kwargs` — Passed to `generation_config` attributes or model's `forward()`.

**Returns:** List of generated token indices.

**Key kwargs:**
- `max_length`, `max_new_tokens`, `min_length`, `min_new_tokens` — See [[api/generation_config]].
- `do_sample`, `top_k`, `top_p`, `temperature`, `repetition_penalty` — See [[api/generation_config]].
- `eos_token_id`, `pad_token_id` — See [[api/generation_config]].
- `num_beams` — Currently only `1` supported (no beam search yet).

**Note:** Most generation parameters come from `[[api/generation_config]]`; check its docs for full parameter list and defaults.

### `chat(tokenizer, query, history=None, system_role_name='system', user_role_name='user', assistant_role_name='assistant', instruction='', max_length=512, max_new_tokens=None, min_length=0, min_new_tokens=None, do_sample=True, temperature=1.0, top_k=50, top_p=1.0, repetition_penalty=1.0)`

High-level conversational generation with chat template handling.

**Parameters:**
- `tokenizer` (PreTrainedTokenizer) — Tokenizer for token encoding/decoding.
- `query` (str) — Current user input.
- `history` (List[Dict[str, str]], optional) — Conversation history; each entry has `"role"` and `"content"` keys. Default: None.
- `system_role_name`, `user_role_name`, `assistant_role_name` (str) — Role identifiers in template. Defaults: "system", "user", "assistant".
- `instruction` (str, optional) — System-level instruction message. Default: "".
- `max_length`, `max_new_tokens`, `min_length`, `min_new_tokens`, `do_sample`, `temperature`, `top_k`, `top_p`, `repetition_penalty` — See [[api/generation_config]].

**Returns:** Tuple `(response, updated_history)`.
- `response` — Model's reply string.
- `updated_history` — Conversation history with new exchange appended.

**Process:** Tokenizer's chat template formats the conversation → `generate()` → tokenizer decodes output.

### `forward(input_ids, valid_length_each_example, block_tables=None, slot_mapping=None, prefill=None, use_past=False, encoder_mask=None, encoder_output=None, target_mask=None, key_cache=None, value_cache=None, **model_kwargs)`

Model forward pass for generation.

**Parameters:**
- `input_ids` (List[List[int]]) — Padded input token indices.
- `valid_length_each_example` (np.ndarray) — Actual length of each example excluding padding.
- `block_tables` (Tensor, optional) — Page attention parameter. See [[concepts/paged_attention]].
- `slot_mapping` (Tensor, optional) — Page attention parameter (token cache slot index).
- `prefill` (bool, optional) — `True` = prefill phase (full context); `False` = decode phase (single token).
- `use_past` (bool, optional) — Use cached KV from prior steps (essential for speed).
- `encoder_mask`, `encoder_output`, `target_mask` (Tensor, optional) — Encoder-decoder only; not needed for decoder-only.
- `key_cache`, `value_cache` (List[Tensor], optional) — KV-cache tensors from prior steps.
- `**model_kwargs` — Additional model-specific parameters.

**Returns:** Tuple `(output, current_index)`.
- `output` — Forward pass result.
- `current_index` — Current sequence index.

### `infer(input_ids, valid_length_each_example, generation_config=None, logits_processor=None, logits_warper=None, block_tables=None, slot_mapping=None, prefill=True, is_finished=None, encoder_mask=None, encoder_output=None, target_mask=None, **model_kwargs)`

Infer next token and return logits; supports both prefill and decode phases.

**Parameters:**
- `input_ids`, `valid_length_each_example` — See `forward()`.
- `generation_config` (GenerationConfig, optional) — Generation parameters.
- `logits_processor` (LogitsProcessorList, optional) — Processors modifying logit scores (e.g., top-k, temperature).
- `logits_warper` (LogitsProcessorList, optional) — Warpers adjusting score distribution before multinomial sampling (e.g., top-p nucleus).
- `block_tables`, `slot_mapping` — Page attention parameters.
- `prefill` (bool, optional) — `True` = prefill; `False` = decode. Default: True.
- `is_finished` (List[bool], optional) — Per-sequence completion flags.
- Other parameters as in `forward()`.

**Returns:** Tuple `(next_token, is_finished)`.
- `next_token` — Generated next token ID.
- `is_finished` — Updated completion flags.

### `postprocess(input_ids, is_finished, res, generation_config, valid_length_each_example, current_index, logits_processor=None, logits_warper=None, need_gather_logits=True)`

Post-process model generation output.

**Parameters:**
- `input_ids` — Padded input token indices.
- `is_finished` — Completion flags (per sequence).
- `res` — Logits from inference.
- `generation_config` — Active generation config.
- `valid_length_each_example`, `current_index` — Sequence metadata.
- `logits_processor`, `logits_warper` — Logit modifiers.
- `need_gather_logits` (bool, optional) — If decoding (first iteration), gather results. Default: True.

**Returns:** Tuple `(target_list, next_probs_cache, next_logits_cache, is_finished)`.

## Typical Flow

```python
# High-level chat
response, history = model.chat(
    tokenizer,
    query="How to train a model?",
    history=[...],
    max_new_tokens=100,
    do_sample=True,
    top_k=50
)

# Low-level generate with config
config = GenerationConfig(max_new_tokens=256, temperature=0.7, use_past=True)
ids = model.generate(input_ids, generation_config=config)
```