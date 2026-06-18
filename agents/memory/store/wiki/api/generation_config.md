---
title: GenerationConfig — Text Generation Parameters
category: api
sources: ["mindformers.generation.GenerationConfig"]
last_updated: 2026-05-17
confidence: high
---

Configuration class that holds all parameters controlling autoregressive text generation behaviour in MindFormers models.

## Parameter Categories

### Output Length Control

| Parameter | Type | Default | Effect |
|-----------|------|---------|--------|
| `max_length` | int | 20 | Total sequence length (prompt + generated tokens). Overridden by `max_new_tokens` if both set. |
| `max_new_tokens` | int | None | Max tokens to generate, excluding prompt. Takes precedence over `max_length`. |
| `min_length` | int | 0 | Minimum total sequence length. Overridden by `min_new_tokens` if both set. |
| `min_new_tokens` | int | None | Minimum new tokens to generate. Takes precedence over `min_length`. |

### Generation Strategy

| Parameter | Type | Default | Effect |
|-----------|------|---------|--------|
| `do_sample` | bool | False | `True` = sampling (stochastic); `False` = greedy decoding. |
| `use_past` | bool | False | Use KV-cache (key/value attention cache) from previous steps to accelerate decoding. Essential for long sequences. |

### Logit Control (output probability shaping)

| Parameter | Type | Default | Constraints | Effect |
|-----------|------|---------|-------------|--------|
| `temperature` | float | 1.0 | > 0 | Scales logits before softmax. > 1.0 = more diverse; < 1.0 = more confident/sharp. |
| `top_k` | int | 50 | > 0 | Keep only top-K highest-probability tokens as candidates. |
| `top_p` | float | 1.0 | (0, 1] or > 1 | Nucleus sampling: keep tokens whose cumulative probability ≥ top_p. If > 1, enables top-k algorithm instead. |
| `repetition_penalty` | float | 1.0 | 1.0 = no penalty; > 1.0 = penalize; < 1.0 = reward | Penalizes tokens that have already appeared in the sequence. |
| `encoder_repetition_penalty` | float | 1.0 | 1.0 = no penalty; > 1.0 = penalize; < 1.0 = reward | Penalizes repetition of tokens not in the original encoder input (encoder-decoder models only). |
| `renormalize_logits` | bool | False | — | Renormalize logits after all logit processors/warpers applied. **Strongly recommended `True`** because sampling algorithms assume normalized scores, but some processors break normalization. |

### Output Format Control

| Parameter | Type | Default | Effect |
|-----------|------|---------|--------|
| `output_scores` | bool | False | Return prediction scores before softmax. |
| `output_logits` | bool | False | Return raw (unprocessed) logit scores. |
| `return_dict_in_generate` | bool | False | Return dict output instead of tuple of output_ids. |

### Special Token IDs

| Parameter | Type | Default | Effect |
|-----------|------|---------|--------|
| `pad_token_id` | int | None | Padding token index. |
| `bos_token_id` | int | None | Beginning-of-sequence token index. |
| `eos_token_id` | int \| List[int] | [] | End-of-sequence token ID(s). Can specify multiple to stop on any. |

## Common Pitfalls

- **Length override**: If both `max_length` and `max_new_tokens` are set, `max_new_tokens` wins. Plan one source of truth.
- **Normalization**: With custom logit processors, set `renormalize_logits=True` to avoid scoring artifacts that break sampling.
- **Cache with batching**: `use_past=True` is critical for efficient batched decoding on Ascend NPUs; omitting it forces full recomputation at each step.

## Example

```python
from mindformers.generation import GenerationConfig

config = GenerationConfig(
    max_new_tokens=100,
    min_new_tokens=10,
    do_sample=True,
    top_k=5,
    top_p=0.8,
    temperature=0.7,
    use_past=True,
    repetition_penalty=1.2,
    renormalize_logits=True,
    eos_token_id=2
)
```