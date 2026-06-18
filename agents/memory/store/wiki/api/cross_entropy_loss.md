---
title: CrossEntropyLoss
category: api
sources: ["mindformers.core.CrossEntropyLoss.html"]
last_updated: 2026-05-17
confidence: high
---

Cross-entropy loss for classification and language modeling on Ascend NPUs, with per-token masking and distributed training support.

## Class Signature

```python
class CrossEntropyLoss(
    parallel_config=default_dpmp_config,  # Distributed parallel config
    calculate_per_token_loss=False,       # Divide by token count (LLM mode)
    seq_split_num=1                       # Sequence pipeline parallelism splits
)
```

## Parameters

- **parallel_config** — OpParallelConfig dict controlling distributed strategy (data-parallel, model-parallel, pipeline-parallel). Default: `default_dpmp_config`
- **calculate_per_token_loss** — When True, loss is divided by number of valid tokens (ignore masked positions). Essential for LLM training to get comparable loss across different batch sizes and sequence lengths
- **seq_split_num** — Number of sequence splits in pipeline parallelism mode. Default: 1 (no splitting)

## Input Signature

```python
def __call__(
    logits: Tensor,      # Shape (N, C) — log probabilities, dtype float32/float16
    label: Tensor,       # Shape (N,) — class indices OR class probabilities
    input_mask: Tensor   # Shape (N,) — 0/1 mask, 1 = compute loss, 0 = ignore
) -> Tensor
```

## Target Formats

### Class Index (Standard)

```python
logits = Tensor([[3, 5, 6, 9, 12, 33, 42, 12, 32, 72]], dtype=float32)  # (1, 10)
label = Tensor([1], dtype=int32)  # class index 1
input_mask = Tensor([1.0], dtype=float32)
loss = criterion(logits, label, input_mask)  # scalar loss
```

Loss formula (reduction='mean'):
```
L = -log(exp(logits[y]) / sum(exp(logits)))
```

### Class Probabilities (Multi-label)

```python
logits = Tensor([[0.1, 0.2, 0.3]], dtype=float32)  # (1, 3)
label = Tensor([[0.0, 1.0, 0.0]], dtype=float32)  # probability distribution
loss = criterion(logits, label, input_mask)
```

Use for soft targets, knowledge distillation, or label smoothing.

## Masking

input_mask allows selective loss calculation:

```python
# Only compute loss for non-padded positions
logits = Tensor(shape=(batch, seq_len, vocab_size))
label = Tensor(shape=(batch, seq_len))
input_mask = Tensor(shape=(batch, seq_len))  # 1 for valid, 0 for padding
loss = criterion(logits, label, input_mask)
```

For per-token loss in language modeling:
```python
# Loss at each position, masked to valid tokens
total_loss = criterion(logits, label, input_mask)  # scalar (sum or mean)
```

## Reduction Modes

The loss implements reduction internally:
- `reduction='mean'` (default) — average over valid (unmasked) positions
- `reduction='sum'` — sum over all positions

## LLM-Specific Usage

For language modeling, set `calculate_per_token_loss=True`:

```python
loss_fn = CrossEntropyLoss(calculate_per_token_loss=True)

# During training
logits = model(input_ids)  # (batch, seq_len, vocab_size)
labels = input_ids[:, 1:]   # shift for next-token prediction
mask = attention_mask[:, 1:]

loss = loss_fn(logits, labels, mask)
# loss is normalized by number of valid tokens (non-masked positions)
# allows comparing loss across different batch sizes/seq lengths
```

Without `calculate_per_token_loss`, loss scales with sequence length, making hyperparameter tuning difficult.

## Common Errors

- **Logits dtype must be float32 or float16** — cast before passing
- **label shape mismatch** — for class index, must be (N,); for probabilities, must be (N, C)
- **input_mask not 0/1** — use dtype float32, values only 0.0 or 1.0
- **ignore_index out of class range** — if set, must be in [0, C)

## Notes

- [[api/training_callbacks]] shows loss monitoring with MFLossMonitor
- [[api/optimizer_adamw]] for optimization after loss.backward()
- calculate_per_token_loss is **critical** for stable LLM training hyperparameter selection