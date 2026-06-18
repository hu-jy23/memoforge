---
title: Generation Strategies — Sampling vs. Greedy Decoding
category: concepts
sources: ["mindformers.generation.GenerationConfig", "mindformers.generation.GenerationMixin"]
last_updated: 2026-05-17
confidence: high
---

MindFormers supports two fundamentally different decoding strategies that trade speed and diversity for determinism.

## Greedy Decoding

**Setting:** `do_sample=False` (default)

At each step, pick the token with the highest probability: `argmax(logits)`.

**Characteristics:**
- **Deterministic** — same input always produces same output.
- **Fast** — single token per step, no sampling overhead.
- **Repetitive** — prone to cycles and dull output without [[#repetition-penalties]].
- **Typical use:** factual Q&A, code generation where reproducibility matters.

## Sampling (Stochastic)

**Setting:** `do_sample=True`

Draw next token from a distribution shaped by logits.

**Characteristics:**
- **Stochastic** — different outputs on repeated calls (controlled by `seed`).
- **Diverse** — avoids repetitive patterns naturally.
- **Slower** — multinomial sampling adds overhead; mitigate with `use_past=True` and KV-cache.
- **Typical use:** creative writing, conversation, dialogue systems.

## Sampling Controls

### Temperature

Scales logits before softmax: `softmax(logits / temperature)`.

| Value | Effect | Use |
|-------|--------|-----|
| < 1.0 | Sharper distribution; model more confident in high-prob tokens | Focused, coherent output |
| = 1.0 | No scaling; unbiased sampling | Default; balanced diversity |
| > 1.0 | Flatter distribution; all tokens more equally likely | Creative, diverse output |

> **Pitfall:** Temperature = 0 is **not** equivalent to greedy. Set `do_sample=False` for deterministic.

### Top-K Filtering

Keep only the K tokens with highest probability; set others to 0.

| Example | Effect |
|---------|--------|
| `top_k=50` | At each step, only top 50 tokens are candidates | Filters out low-prob noise; avoids tail-distribution gibberish |
| `top_k=1` | Only the most likely token (like greedy, but still samples) | Not typically useful |

### Top-P (Nucleus Sampling)

Keep tokens whose cumulative probability ≥ P.

| Example | Effect |
|---------|--------|
| `top_p=0.9` | Dynamically keep tokens adding up to 90% cumulative prob | Adaptive: high-entropy positions keep more tokens; low-entropy positions keep fewer |
| `top_p=1.0` | Keep all tokens (no filtering) | Default; no nucleus constraint |

> **Note:** If `top_p > 1`, it switches to top-k mode instead.

### Repetition Penalty

Reduce probability of tokens already in the sequence: `logits[prev_token] /= repetition_penalty`.

| Value | Effect |
|-------|--------|
| 1.0 | No penalty (default) |
| > 1.0 | Penalize repetition; higher = stronger penalty | Common: 1.1–1.5 to avoid word loops |
| < 1.0 | Reward repetition (rare; can cause monotone output) | Not recommended |

## Encoder Repetition Penalty

For encoder-decoder models (e.g., translation, summarization): penalize tokens **not** in the original input.

Useful when you want the model to reference the source (translation must ground in source), not generate novel words.

## KV-Cache & Use_Past

For both strategies, set `use_past=True` + provide `key_cache` and `value_cache`:

- Reuses attention keys/values from prior steps (constant memory overhead, linear speedup).
- Critical for long sequences on Ascend NPUs; omitting forces O(n²) recomputation.
- Works identically under greedy and sampling.

## Logit Normalization

After applying temperature, top-k, top-p, repetition penalties, logit scores may no longer sum to 1 (probabilities). Set `renormalize_logits=True` to renormalize. **Strongly recommended** if using custom logit processors.