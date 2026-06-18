# notes/mf-train-wrappers.md
_Last updated: 2026-05-29_

## Confirmed

## Observed Once

- For `MFTrainOneStepCell`, `net_outputs[3]` is a better primary source for the current-step learning rate than `optimizer.get_lr()` because it reflects the LR actually applied in the step.
  Source: custom-callback-norm-lr-01 (2026-05-29)

- For `MFTrainOneStepCell`, `net_outputs[4]` exposes `global_norm` when gradient clipping is enabled; `runner_wrapper.use_clip_grad: true` is required for non-null callback logging of `global_norm`.
  Source: custom-callback-norm-lr-01 (2026-05-29)

- Callback logging code that runs inside `step_end` should guard `step == 0` before modulo interval checks and should catch `OSError` around append-mode file writes to avoid interrupting training.
  Source: custom-callback-norm-lr-01 (2026-05-29)

## Uncertain / Conflicting

