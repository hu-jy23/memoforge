---
title: Training Metrics
category: api
sources: ["mindformers.core.EmF1Metric.html", "mindformers.core.EntityScore.html", "mindformers.core.PerplexityMetric.html", "mindformers.core.PromptAccMetric.html"]
last_updated: 2026-05-17
confidence: high
---

Evaluation metrics for monitoring model performance during and after training.

## Common Pattern

All metrics follow this interface:

```python
metric = MetricClass()

# Clear previous state
metric.clear()

# Accumulate batch results
for batch_pred, batch_label in data:
    metric.update(batch_pred, batch_label)

# Compute final result
result_dict = metric.eval()
print(result_dict)
```

## PerplexityMetric

Measures language model prediction quality. Lower is better.

### Input Signature

```python
def update(
    logits: Tensor,   # Shape (N, S, W) — log-probabilities, float16/float32
    label: Tensor,    # Shape (N, S) — token IDs, int32/int64
    input_mask: Tensor  # Shape (N, S) — 0/1 mask for valid positions
)
```

### Formula

```
PP(W) = exp(-1/N * Σ log P(w_i | context))
```

where N is total valid tokens (sum of input_mask), and P(w_i | context) is the probability assigned to the true next token at position i.

### Output

```python
result = metric.eval()
# {'loss': float, 'PPL': float}
```

PPL is the exponentiated negative log-likelihood. Compare across models:
- Lower PPL = better predictions
- PPL < 10 = good language model quality
- PPL 10-50 = moderate
- PPL > 100 = poor

## EmF1Metric

Exact Match (EM) and F1 score for question-answering and text generation tasks.

### Input Signature

```python
def update(
    predictions: List[str],  # N predictions
    labels: List[str]        # N ground-truth labels
)
```

### Metrics

**Exact Match (EM):** Does the prediction exactly match the label (ignoring punctuation)?
- 1.0 = perfect match
- 0.0 = no match

Examples:
```
Prediction: "Beijing"        Label: "Beijing"        → EM = 100%
Prediction: "Beijing"        Label: "Beijing, China" → EM = 100% (punctuation ignored)
Prediction: "Beijing China"  Label: "Beijing"        → EM = 0%
```

**F1 Score:** Overlap between prediction and label words (longest common subsequence).

```
F1 = 2 × (precision × recall) / (precision + recall)
precision = LCS_length / len(prediction)
recall = LCS_length / len(label)
```

Ranges from 0 to 100.

### Output

```python
result = metric.eval()
# Per-example: {'F1': float, 'Em': float}
# Aggregated: {'F1': float, 'Em': float}  (averaged across all examples)
```

## EntityScore

Precision, recall, F1 for named entity recognition (NER) and structured extraction.

### Input Signature

```python
def update(
    logits: Tensor,   # Shape (N, C) — prediction scores, float16/float32
    label: Tensor     # Shape (N,) — entity type IDs, int32/int64
)
```

where N = batch size, C = number of entity types.

### Metrics

```
Precision = correct_entities / predicted_entities
Recall = correct_entities / true_entities
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

### Output

```python
result = metric.eval()
# Tuple: (overall_dict, per_entity_dict)
# overall_dict = {'precision': float, 'recall': float, 'f1': float}
# per_entity_dict = {
#     'entity_type_name': {'precision': float, 'recall': float, 'f1': float},
#     ...
# }
```

Example:
```python
# For NER with 'ADDRESS', 'PERSON', 'ORG' entities
result = metric.eval()
# ({
#     'precision': 0.95,
#     'recall': 0.92,
#     'f1': 0.935
# }, {
#     'address': {'precision': 0.98, 'recall': 0.90, 'f1': 0.94},
#     'person': {'precision': 0.93, 'recall': 0.95, 'f1': 0.94},
#     'org': {'precision': 0.94, 'recall': 0.91, 'f1': 0.925}
# })
```

## PromptAccMetric

Prompt-based classification accuracy for zero-shot and few-shot learning.

### Concept

Compare perplexity of input text under different labeled prompts:
```
Prompt 0: "This is a Sports article: {passage}"
Prompt 1: "This is a Culture article: {passage}"
Prompt 2: "This is a News article: {passage}"

Model assigns lowest perplexity to the correct prompt → correct classification
```

### Input Signature

```python
def update(
    logits: Tensor,     # Shape (N, S, W) — model predictions, float16/float32
    input_ids: Tensor,  # Shape (N, S) — token IDs
    input_mask: Tensor, # Shape (N, S) — attention mask
    labels: Tensor      # Shape (N,) — correct prompt index
)
```

### Output

```python
result = metric.eval()
# {'accuracy': float}  (0 to 1)
```

### Notes

- Model must assign higher probability to correct prompt than incorrect ones
- Used for in-context learning evaluation
- Computationally cheaper than traditional evaluation (single forward pass)

## Usage Example

```python
from mindformers.core.metric.metric import PerplexityMetric, EmF1Metric

# Language model evaluation
ppl_metric = PerplexityMetric()
ppl_metric.clear()

for logits, labels, mask in validation_loader:
    ppl_metric.update(logits, labels, mask)

ppl_result = ppl_metric.eval()
print(f"Validation PPL: {ppl_result['PPL']:.2f}")

# QA evaluation
qa_metric = EmF1Metric()
qa_metric.clear()

for pred, true_label in qa_results:
    qa_metric.update([pred], [true_label])

qa_result = qa_metric.eval()
print(f"EM: {qa_result['Em']:.1f}%, F1: {qa_result['F1']:.1f}%")
```

## Notes

- All metrics are cumulative; call `clear()` before each evaluation epoch
- Metrics work with batch or single-sample inputs
- [[api/training_callbacks]] shows EvalCallBack for periodic metric evaluation during training