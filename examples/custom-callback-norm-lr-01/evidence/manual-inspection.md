# Manual Inspection Evidence

Task: `custom-callback-norm-lr-01`
Candidate: `custom-callback-norm-lr-01-candidate-01`

## Files inspected

- `workspace/patch/custom-callback-norm-lr-01/norm_lr_logger.py`
- `workspace/patch/custom-callback-norm-lr-01/training_config_example.yaml`
- `workspace/coder_summary.md`
- `workspace/task_contract.md`

## Findings

- Registration uses `@MindFormerRegister.register(MindFormerModuleType.CALLBACK)`, matching wiki guidance in `api/mindformer-register`.
- Constructor validates non-empty `log_file` and `log_interval >= 1`.
- Parent directory creation is performed during construction.
- `step_end` returns immediately for `step == 0`, preventing a spurious first record.
- JSONL output uses append mode with UTF-8 encoding and `ensure_ascii=False`.
- File write is guarded with `except OSError` and emits a `RuntimeWarning` instead of interrupting training.
- Primary LR extraction uses `cb_params.net_outputs[3]`, matching the `MFTrainOneStepCell` output layout recorded in `api/mf-train-wrappers`.
- Fallback LR extraction uses `cb_params.optimizer.get_lr()` when `net_outputs` is unavailable or too short.
- `global_norm` extraction uses `cb_params.net_outputs[4]` and returns `None` when the output tuple is short or the value is absent.
- YAML fragment documents `runner_wrapper.use_clip_grad: true` as required for non-null `global_norm`.
- YAML fragment documents module import as a prerequisite for registry availability before Trainer initialization.

## Limits

- The local check does not import MindSpore or MindFormers.
- End-to-end execution on Ascend hardware was not performed.
- Version behavior for MindFormers versions earlier than 0.6 remains outside this sample evidence.
