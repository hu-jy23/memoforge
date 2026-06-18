---
title: Training Callbacks
category: api
sources: ["mindformers.core.CheckpointMonitor.html", "mindformers.core.EvalCallBack.html", "mindformers.core.MFLossMonitor.html", "mindformers.core.ProfileMonitor.html"]
last_updated: 2026-05-17
confidence: high
---

Callback functions invoked during training to monitor progress, save checkpoints, evaluate, and profile performance.

## CheckpointMonitor

Saves model checkpoints during training.

```python
class CheckpointMonitor(
    prefix='CKP',
    directory=None,          # Default: ./output/checkpoint
    config=None,             # CheckpointConfig object
    save_checkpoint_steps=1,  # Interval in steps
    save_checkpoint_seconds=0,  # Alternative: interval in seconds (mutually exclusive)
    keep_checkpoint_max=5,    # Max checkpoints to keep
    keep_checkpoint_per_n_minutes=0,  # Keep one per N minutes (conflicts with keep_checkpoint_max)
    integrated_save=True,    # Auto-merge sharded tensors (auto-parallel only)
    save_network_params=False,  # Also save only network params
    save_trainable_params=False,  # Also save only trainable params
    async_save=False,        # Non-blocking save
    saved_network=None,      # Network to save (if different from training net)
    append_info=None,        # List: ["epoch_num", "step_num"] + dicts with str keys, int/float/bool/str/Parameter/Tensor values
    enc_key=None,            # Encryption key (bytes) for encrypted checkpoints
    enc_mode='AES-GCM',      # 'AES-GCM', 'AES-CBC', 'SM4-CBC'
    exception_save=False,    # Save on training exception
    global_batch_size=0,
    checkpoint_format='ckpt',  # 'ckpt' or 'safetensors'
    remove_redundancy=False,  # Strip redundant data during save
    embedding_size=4096,     # For embedding norm calculation
    use_checkpoint_health_monitor=False,  # Monitor embedding norm for weight health
    embedding_local_norm_threshold=1.0,
    health_ckpts_record_dir='./output',
    use_legacy_format=True,  # Use old format (False = new format)
    save_optimizer=True      # Save optimizer state (new format only)
)
```

### Key Parameters

- **directory** — If None, saves to `./output/checkpoint` in current working directory
- **save_checkpoint_steps vs save_checkpoint_seconds** — Use one or the other, not both
- **keep_checkpoint_max vs keep_checkpoint_per_n_minutes** — Use one or the other, not both
- **checkpoint_format** — `'safetensors'` for Hugging Face-compatible format; `'ckpt'` for MindSpore native format
- **use_checkpoint_health_monitor** — Monitor model weight health via embedding norm. Flags potential divergence early
- **append_info** — Custom metadata to include in checkpoint (e.g., custom metrics, config snapshots)

### Notes

- Integrated save only works in auto-parallel mode; manual parallel ignores it
- Async save is non-blocking but may delay training finish until queued saves complete
- Encrypted checkpoints require matching `enc_key` at load time
- Health monitoring adds overhead but can catch divergence before full training failure

## EvalCallBack

Evaluate model at intervals during training.

```python
class EvalCallBack(
    eval_func,             # Callable that runs evaluation
    step_interval=100,     # Eval every N steps
    epoch_interval=-1      # -1 = eval only at epoch end; else eval every N epochs
)
```

### Notes

- step_interval doesn't work in data-lower mode; use epoch_interval instead
- `eval_func` should be user-defined and return metrics dict

## MFLossMonitor

Monitor loss and training metrics at intervals.

```python
class MFLossMonitor(
    learning_rate=None,                  # Scheduler to log (optional)
    per_print_times=1,                   # Log every N steps
    micro_batch_num=1,                   # For pipeline parallelism
    micro_batch_interleave_num=1,        # For interleaved pipeline
    origin_epochs=None,
    dataset_size=None,
    initial_epoch=0,
    initial_step=0,
    global_batch_size=0,
    gradient_accumulation_steps=1,
    check_for_nan_in_loss_and_grad=False,  # Warn on NaN in loss/gradients
    calculate_per_token_loss=False,      # Log per-token loss (LLM training)
    print_separate_loss=False            # Separate loss components
)
```

### Key Parameters

- **check_for_nan_in_loss_and_grad** — Catches divergence early (training instability)
- **calculate_per_token_loss** — For LLMs, divides loss by token count for comparable metrics across batch sizes
- **print_separate_loss** — Useful when loss is sum of multiple components

## ProfileMonitor

Profile training performance (computation, memory, communication).

```python
class ProfileMonitor(
    start_step=1,
    stop_step=10,
    output_path=None,
    start_profile=True,
    profile_rank_ids=None,           # List of rank IDs to profile (None = all)
    profile_pipeline=False,          # One card per pipeline stage
    profile_communication=False,     # Distributed communication overhead
    profile_memory=False,            # Per-tensor memory consumption
    profiler_level=0,                # 0=minimal, 1=+CANN/AICORE, 2=+graph-compile/runtime
    with_stack=False,                # Capture Python call stacks
    data_simplification=True,        # Delete FRAMEWORK dir after export
    config=None,                     # Custom config (e.g., parallel config)
    mstx=False                       # Enable mstx latency tracing
)
```

### Profiler Levels

- **0** — Basic operator timing, large-op communication data
- **1** — +CANN/AscendCL details, AICORE performance, small-op communication
- **2** — +graph compilation, runtime data (most comprehensive, slowest)

### Notes

- Profile output requires offline analysis; generates large files
- Use on small step ranges (start_step to stop_step) to limit overhead
- profile_rank_ids useful for distributed debugging (don't profile all ranks at once)

## Usage Example

```python
from mindformers.core import CheckpointMonitor, MFLossMonitor, EvalCallBack

callbacks = [
    CheckpointMonitor(
        directory='./checkpoints',
        save_checkpoint_steps=500,
        keep_checkpoint_max=3,
        checkpoint_format='safetensors'
    ),
    MFLossMonitor(
        per_print_times=10,
        check_for_nan_in_loss_and_grad=True,
        calculate_per_token_loss=True
    ),
    EvalCallBack(
        eval_func=my_eval_function,
        step_interval=1000
    )
]

# Pass to model.train() or trainer
```

## Notes

- Callbacks run in order; keep them lightweight to avoid training slowdown
- [[config/training_config]] shows how to configure callbacks in YAML

---

## Custom Callback Registration

*Source: task `custom-callback-norm-lr-01` (2026-05-17). Confidence: medium.*

MindFormers supports user-defined callbacks that are instantiated from YAML config via the `MindFormerRegister` mechanism. This section documents the pattern confirmed in a working implementation.

### Registration decorator

```python
from mindformers.tools.register import MindFormerRegister, MindFormerModuleType
from mindformers.core.callback.callback import Callback  # or mindspore.train.Callback

@MindFormerRegister.register(MindFormerModuleType.CALLBACK)
class MyCallback(Callback):
    def __init__(self, param_a: str, param_b: int = 100):
        super().__init__()
        ...
```

The `@MindFormerRegister.register(MindFormerModuleType.CALLBACK)` decorator registers the class under its class name. The YAML `type` field must match the class name exactly.

### YAML instantiation prerequisite

The callback module **must be imported before the `Trainer` reads the YAML config**. Without this import, `get_instance_from_cfg` cannot resolve the `type` key and will raise a lookup error. Document the import requirement in the module docstring and in the YAML example comments.

```yaml
# In your training script, import the callback module before creating the Trainer:
# import my_package.my_callback  # registers NormLRLogger via MindFormerRegister

callbacks:
  - type: MFLossMonitor
    per_print_times: 10
  - type: CheckpointMonitor
    save_checkpoint_steps: 500
  - type: MyCallback       # resolved via MindFormerRegister at Trainer init
    param_a: "./logs/my_log.jsonl"
    param_b: 50
```

### MFTrainOneStepCell net_outputs layout

When `runner_wrapper.type: MFTrainOneStepCell`, the `cb_params.net_outputs` tuple has the following layout (MindFormers 0.8.x–1.x):

| Index | Field | Type | Notes |
|-------|-------|------|-------|
| 0 | `loss` | Tensor | Training loss |
| 1 | `overflow_flag` | Tensor / bool | Loss scaling overflow indicator |
| 2 | `loss_scale` | Tensor | Current loss scale value |
| 3 | `learning_rate` | Tensor | LR **actually applied** this step (on-device) |
| 4 | `global_norm` | Tensor or None | Gradient global norm; `None` if `use_clip_grad: false` |

> **Note (low confidence):** Versions < 0.6 used a 3-element tuple (no `learning_rate` or `global_norm` fields). If the index layout changes in a future version, LR and global_norm extraction will silently fall back to `null`.

`global_norm` is `None` (JSON `null`) when:
- `runner_wrapper.use_clip_grad: false` (MindFormers default)
- `net_outputs` tuple length < 5 (non-MFTrainOneStepCell wrappers)
- The tensor value itself is `None`

To obtain non-null `global_norm`, set `runner_wrapper.use_clip_grad: true` in the training YAML.

### Two-path LR extraction pattern

*(See task `custom-callback-norm-lr-01` for reference implementation.)*

```python
def _extract_lr(self, cb_params) -> float | None:
    """Primary: net_outputs[3] (on-device, no scheduling lag).
    Fallback: optimizer.get_lr() (may have one-step lag in some schedulers)."""
    try:
        net_out = cb_params.net_outputs
        if net_out is not None and len(net_out) >= 4:
            lr = net_out[3]
            if hasattr(lr, 'asnumpy'):
                return float(lr.asnumpy())
            return float(lr)
    except Exception:
        pass
    # Fallback
    try:
        optimizer = cb_params.optimizer
        if optimizer is not None and hasattr(optimizer, 'get_lr'):
            lr = optimizer.get_lr()
            if hasattr(lr, 'asnumpy'):
                return float(lr.asnumpy())
            return float(lr)
    except Exception:
        pass
    return None
```

**When to use primary vs fallback:**
- Primary (`net_outputs[3]`) reflects the LR applied in the **current** step — preferred for monitoring.
- Fallback (`optimizer.get_lr()`) is used when the wrapper is not `MFTrainOneStepCell` or the tuple is too short. May reflect the **next**-step LR in some scheduler implementations (one-step lag). Acceptable for monitoring-only callbacks.

### step=0 boundary guard

`0 % N == 0` is always true for any `N`, so without an explicit guard the callback fires at step 0 before meaningful training outputs exist. Always add:

```python
def step_end(self, run_context):
    cb_params = run_context.original_args()
    step = cb_params.cur_step_num
    if step == 0:          # explicit boundary guard — do not rely on MindSpore starting at 1
        return
    if step % self.log_interval != 0:
        return
    ...
```

### OSError guard for file writes

An unhandled `OSError` in `step_end` (disk full, NFS disconnect, permission revoked) propagates into the MindSpore training loop and aborts the run. Wrap file writes:

```python
import warnings

try:
    with open(self.log_file, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
except OSError as exc:
    warnings.warn(
        f"MyCallback: failed to write to {self.log_file!r} at step {step}: {exc}",
        RuntimeWarning,
        stacklevel=2,
    )
```

Catch `OSError` specifically (not bare `Exception`) to keep the guard precise. Use `warnings.warn(..., RuntimeWarning)` so the failure is visible in logs without stopping training.

### Related pages

- [[api/mindformer-register]] — `MindFormerRegister` and `MindFormerModuleType` reference
- [[api/mf-train-wrappers]] — `MFTrainOneStepCell` and `runner_wrapper` configuration