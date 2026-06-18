---
title: Tokenizer classes (PreTrained and model-specific)
category: api
sources: ["mindformers.models.PreTrainedTokenizer.html", "mindformers.models.PreTrainedTokenizerFast.html", "mindformers.models.ChatGLM3Tokenizer.html", "mindformers.models.ChatGLM4Tokenizer.html", "mindformers.models.LlamaTokenizer.html", "mindformers.models.LlamaTokenizerFast.html"]
last_updated: 2026-05-17
confidence: high
---

Tokenizer base classes and model-specific implementations. Slow tokenizers use SentencePiece/BPE; fast tokenizers wrap HuggingFace's Rust implementation.

## PreTrainedTokenizer (slow)

Base class for slow tokenizers using Python implementation.

**Key parameters:**
- `model_max_length` (int, optional) — Max input length in tokens. Default: 1e-30.
- `padding_side` (str) — Pad left or right. Choose from `['left', 'right']`. Default: class attribute.
- `truncation_side` (str) — Truncate left or right. Choose from `['left', 'right']`. Default: class attribute.
- `chat_template` (str, optional) — Jinja template for formatting chat messages.
- `model_input_names` (List[str]) — Input names model accepts (e.g., `['token_type_ids', 'attention_mask']`). Default: class attribute.
- `bos_token`, `eos_token`, `unk_token`, `sep_token`, `pad_token`, `cls_token`, `mask_token` — Special tokens.
- `additional_special_tokens` — Extra special tokens.
- `clean_up_tokenization_spaces` (bool) — Remove tokenization artifacts. Default: `True`.
- `split_special_tokens` (bool) — Split special tokens during tokenization. Default: `False`.

**Key methods:**
- `tokenize(text, pair=None, add_special_tokens=False, **kwargs)` → List[str] — Convert text to token list.
- `convert_tokens_to_ids(tokens)` → Union[int, List[int]] — Token strings to IDs.
- `convert_ids_to_tokens(ids, skip_special_tokens=False)` → Union[str, List[str]] — IDs to token strings.
- `get_added_vocab()` → dict — Added tokens as ID mapping.
- `num_special_tokens_to_add(pair=False)` → int — Count of special tokens added by tokenizer.

## PreTrainedTokenizerFast (fast)

Base class wrapping HuggingFace's Rust-based tokenizer.

**Key parameters:** Same as PreTrainedTokenizer plus:
- `tokenizer_object` (tokenizers.Tokenizer) — HuggingFace Tokenizer object.
- `tokenizer_file` (str) — Path to `.json` tokenizer file.

**Key methods:** Same as PreTrainedTokenizer plus:
- `set_truncation_and_padding(padding_strategy, truncation_strategy, max_length, stride, pad_to_multiple_of)` — Configure truncation/padding.
- `train_new_from_iterator(text_iterator, vocab_size, length=None, new_special_tokens=None, **kwargs)` — Train on new corpus.

## ChatGLM3Tokenizer

BPE tokenizer for ChatGLM3.

**Constructor:**
```python
from mindformers import ChatGLM3Tokenizer
tokenizer = ChatGLM3Tokenizer('tokenizer.model')
```

**Special tokens:**
- `bos_token` (default: `'<sop>'`) — Sequence start.
- `eos_token` (default: `'<eop>'`) — Sequence end.
- `end_token` (default: `'</s>'`) — Final sequence terminator (for multiple sequences).
- `mask_token` (default: `'[MASK]'`) — Masking token.
- `gmask_token` (default: `'[gMASK]'`) — Global mask token.
- `pad_token` (default: `'<pad>'`) — Padding token.
- `unk_token` (default: `'<unk>'`) — Unknown token.

**Example:**
```python
prompts = ["晚上睡不着应该怎么办"]
token_id = tokenizer(prompts)
input_ids = token_id['input_ids']
response = tokenizer.decode(input_ids)
```

## ChatGLM4Tokenizer

BPE tokenizer for ChatGLM4.

**Constructor:**
```python
from mindformers import ChatGLM4Tokenizer
tokenizer = ChatGLM4Tokenizer('tokenizer.model')
```

**Special tokens:**
- `eos_token` (default: `'<|endoftext|>'`) — Sequence end.
- `pad_token` (default: `'<|endoftext|>'`) — Padding (same as EOS).

**Parameters:**
- `clean_up_tokenization_spaces` (bool) — Remove extra spaces after tokenization. Default: `False`.
- `encode_special_tokens` (bool) — Encode special tokens. Default: `False`.

**Example:**
```python
prompts = ["晚上睡不着应该怎么办"]
token_id = tokenizer(prompts)
input_ids = token_id['input_ids']
```

## LlamaTokenizer (slow)

BPE tokenizer using SentencePiece for Llama.

**Constructor:**
```python
from mindformers import LlamaTokenizer
tokenizer = LlamaTokenizer('tokenizer.model')
```

**Special tokens:**
- `unk_token` (default: `'<unk>'`) — Unknown token.
- `bos_token` (default: `'<s>'`) — Begin-of-sequence.
- `eos_token` (default: `'</s>'`) — End-of-sequence.
- `pad_token` (default: `'<unk>'`) — Padding (same as unknown).

**Parameters:**
- `sp_model_kwargs` (Dict, optional) — SentencePiece processor options.
- `add_bos_token` (bool) — Add BOS at start. Default: `True`.
- `add_eos_token` (bool) — Add EOS at end. Default: `False`.
- `clean_up_tokenization_spaces` (bool) — Clean spaces after decode. Default: `False`.
- `legacy` (bool) — Use legacy behavior. Default: `True`.

**Key methods:**
- `build_inputs_with_special_tokens(token_ids_0, token_ids_1=None)` → List[int] — Insert special tokens into sequence.
- `create_token_type_ids_from_sequences(token_ids_0, token_ids_1=None)` → List[int] — Create segment mask for pair classification.
- `get_special_tokens_mask(token_ids_0, token_ids_1=None, already_has_special_tokens=False)` → List[int] — Identify special vs regular tokens.

**Note:** Default config has NO padding token because original Llama had none.

## LlamaTokenizerFast (fast)

Fast BPE tokenizer for Llama using Rust backend. Uses ByteFallback with no normalization.

**Constructor:**
```python
from mindformers import LlamaTokenizerFast
tokenizer = LlamaTokenizerFast(vocab_file='tokenizer.model')
# OR
tokenizer = LlamaTokenizerFast(tokenizer_file='tokenizer.json')
```

**Parameters:**
- `vocab_file` (str, optional) — SentencePiece vocab (`.model`).
- `tokenizer_file` (str, optional) — HuggingFace tokenizer JSON.
- `unk_token`, `bos_token`, `eos_token` — Special tokens (same defaults as slow version).
- `add_bos_token` (bool) — Add BOS at start. Default: `True`.
- `add_eos_token` (bool) — Add EOS at end. Default: `False`.
- `clean_up_tokenization_spaces` (bool) — Clean spaces after decode. Default: `False`.
- `use_default_system_prompt` (bool) — Use Llama default system prompt. Default: `False`.

**Key methods:**
- `build_inputs_with_special_tokens(token_ids_0, token_ids_1=None)` — Insert BOS/EOS.
- `save_vocabulary(save_directory, filename_prefix=None)` — Export vocab from fast tokenizer.
- `update_post_processor()` — Sync post-processor with current BOS/EOS tokens. Call if you change token settings.

**Important:** If changing `bos_token` or `eos_token`, call `update_post_processor()` to ensure correct encoding.

**Common pitfall:** Fast tokenizer may not update special token handling automatically if you modify tokens after initialization — call `update_post_processor()`.

Cross-reference: [[api/chatglm2]], [[api/llama]], [[api/model_base_classes]]