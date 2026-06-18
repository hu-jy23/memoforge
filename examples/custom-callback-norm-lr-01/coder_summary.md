# Coder Summary

## task_id
`custom-callback-norm-lr-01`

## Modified / Created Files

| File | Description |
|------|-------------|
| `workspace/patch/custom-callback-norm-lr-01/norm_lr_logger.py` | Final implementation of `NormLRLogger` — a MindFormers-registered `Callback` subclass that appends `step`, `learning_rate`, `global_norm`, and `timestamp` to a JSONL file every `log_interval` steps. |
| `workspace/patch/custom-callback-norm-lr-01/training_config_example.yaml` | Annotated YAML fragment showing how to add `runner_wrapper` (gradient clipping) and the `NormLRLogger` callback entry to an existing MindFormers training config. |

No files outside `workspace/` were modified.

## Rationale and Wiki Sources

### Class signature
Parameters were aligned with the task spec (`log_file: str`, `log_interval: int = 100`) rather than the earlier draft (`log_path`, `interval`), which used non-standard names.

### MindFormerRegister decoration
`@MindFormerRegister.register(MindFormerModuleType.CALLBACK)` is required for YAML-driven instantiation. Confirmed from `[api/training_callbacks]` usage examples and the existing `MetricLoggingCallback` draft.

### LR extraction strategy
Primary: `cb_params.net_outputs[3]` — emitted by `MFTrainOneStepCell` and reflects the LR **actually applied** in the current step (on-device value, no scheduling lag). Source: wiki `[api/training_callbacks]` and the `MetricLoggingCallback` draft which documents the output layout as `[loss, overflow, loss_scale, learning_rate, global_norm]`.

Fallback: `cb_params.optimizer.get_lr()` — used when the wrapper is not `MFTrainOneStepCell` or the output tuple is shorter than 4 elements. The fallback may reflect the **next**-step LR in some scheduler implementations (one-step lag). Documented as a known limitation in the open questions below.

### global_norm extraction
Source: `cb_params.net_outputs[4]`. The value is `None` (and recorded as JSON `null`) when:
- `runner_wrapper.use_clip_grad: false` (MindFormers default)
- `net_outputs` tuple length < 5 (non-MindFormers wrappers)
- The tensor contains `None` explicitly

This matches the contract described in both previous drafts and is consistent with the `runner_wrapper` requirement stated in `workspace/mock_qwen3_training.yaml` comments.

### Append mode + directory creation
The file is opened with `"a"` mode so that checkpoint-and-resume runs accumulate a continuous log rather than overwriting. Parent directories are created in `__init__` via `os.makedirs(..., exist_ok=True)` — avoids silent failures if the directory does not exist at training start.

### Timestamp format
ISO-8601 UTC with trailing `Z` (`%Y-%m-%dT%H:%M:%SZ`) — consistent with the `MetricLoggingCallback` draft; unambiguous for downstream parsing.

### YAML config example
- `runner_wrapper.use_clip_grad: true` is mandatory for non-null `global_norm`. Noted prominently in the YAML comments and confirmed by the comment block in `mock_qwen3_training.yaml`.
- Callback order: `MFLossMonitor` → `CheckpointMonitor` → `NormLRLogger`. The logger is last so it does not slow down the primary monitors.
- Included import instructions as YAML comments because MindFormerRegister requires the module to be imported before the Trainer reads the config.

## Open Questions

1. **MindSpore version compatibility**: `Tensor.asnumpy()` is available in MindSpore >= 1.6. On graph-mode compilation with `ms.set_context(mode=GRAPH_MODE)`, `net_outputs` items may be `Tensor` proxies that are only materialised after the step; `asnumpy()` in `step_end` should work because `step_end` runs in eager context post-step, but this has not been validated end-to-end on Ascend 910.

2. **get_lr() fallback scope**: `optimizer.get_lr()` is a documented `mindspore.nn.Optimizer` method, but not all third-party optimizer wrappers implement it. If the fallback is reached, `NormLRLogger` returns `null` silently rather than raising. Users relying on LR values from non-standard optimizers should verify the fallback actually returns the correct step LR.

3. **Pipeline parallelism**: In pipeline-parallel training the `cur_step_num` reported in `cb_params` may count micro-batches rather than gradient-accumulation steps depending on MindFormers version. The `log_interval` parameter should be tuned accordingly.

4. **net_outputs index stability**: The `[loss, overflow, loss_scale, lr, global_norm]` layout is confirmed for `MFTrainOneStepCell` in current MindFormers (0.8.x – 1.x). Earlier versions (< 0.6) used a 3-element tuple. If the index layout changes in a future version, both LR and global_norm extraction will silently fall back to `null`. A version guard could be added if multi-version support is needed.

## Novel Pattern Flag

**YES** — The two-path LR extraction strategy (primary `net_outputs[3]`, fallback `optimizer.get_lr()`) is a MindFormers-specific pattern not obvious from generic MindSpore Callback documentation. It warrants a potential skill entry in `store/skills/` if this pattern appears in a second successful task cycle.

---

## Fix Pass (task_id: custom-callback-norm-lr-01, fix-pass)

Two warnings from the Verifier's pass-with-warnings result were addressed in-place. No logic was otherwise changed.

### Change 1 — step=0 boundary guard (`step_end`)

**Location**: `step_end()`, immediately before the `log_interval` modulo check.

**Added**:
```python
if step == 0:
    return
```

**Rationale**: `0 % N == 0` is always true, so without this guard the callback would fire at step 0 before any meaningful training outputs exist. MindSpore conventionally starts step numbering at 1 in production runs, but the code should not rely on that implicit convention. The early return makes the boundary behaviour explicit and safe regardless of how the framework initialises `cur_step_num`.

### Change 2 — OSError guard around file write (`step_end`)

**Location**: `step_end()`, the `with open(...)` block.

**Changed from**:
```python
with open(self.log_file, "a", encoding="utf-8") as fh:
    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
```

**Changed to**:
```python
try:
    with open(self.log_file, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
except OSError as exc:
    warnings.warn(
        f"NormLRLogger: failed to write to {self.log_file!r} at step {step}: {exc}",
        RuntimeWarning,
        stacklevel=2,
    )
```

**Rationale**: An unhandled `OSError` (disk full, permission denied, NFS disconnect) would propagate into the MindSpore training loop and abort training. Catching `OSError` specifically (not bare `Exception`) keeps the guard precise; the `warnings.warn(..., RuntimeWarning)` path makes the failure visible in logs without stopping the run. `import warnings` was added at the top of the module.

No files outside `workspace/` were modified. `training_config_example.yaml` was not touched.
