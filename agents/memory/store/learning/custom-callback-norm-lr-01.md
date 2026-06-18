## custom-callback-norm-lr-01 | 2026-05-29 | pass

**Summary**: Task implemented `NormLRLogger`, a MindFormers-registered `Callback` subclass that logs `step`, `learning_rate`, `global_norm`, and `timestamp` to JSONL every `log_interval` steps. The final candidate uses `@MindFormerRegister.register(MindFormerModuleType.CALLBACK)`, reads the current-step LR from `MFTrainOneStepCell` output index 3, reads `global_norm` from output index 4, writes in append mode, skips `step == 0`, and catches `OSError` during file writes so logging does not interrupt training.

**Task contract**: `workspace/task_contract.md` defines the objective, constraints, validation command, and promotion criteria. Validation command: `python3 -m py_compile workspace/patch/custom-callback-norm-lr-01/norm_lr_logger.py`.

**Candidate evidence**: Candidate `custom-callback-norm-lr-01-candidate-01` is recorded in `workspace/candidates.jsonl`. Evidence refs:
- `workspace/evidence/custom-callback-norm-lr-01/commands.log`
- `workspace/evidence/custom-callback-norm-lr-01/manual-inspection.md`
- `workspace/evidence/custom-callback-norm-lr-01/artifact_protocol.log`

**Outcome**: pass. `workspace/verify_result.json` records syntax validation pass, manual inspection pass, and task artifact protocol pass. End-to-end Ascend/MindFormers runtime execution was not performed in this sample cycle.

**Promotion decision**: `workspace/promotion_decision.md` recommends writing this task to learning and notes, but not updating wiki directly and not promoting a skill yet. Skill promotion requires a second successful evidence-backed task with the same trigger and extraction pattern.

**Domain facts**:
- `MFTrainOneStepCell` emits `net_outputs` with layout `[0]=loss`, `[1]=overflow_flag`, `[2]=loss_scale`, `[3]=learning_rate`, `[4]=global_norm`.
- `global_norm` at index 4 is `None` and serializes as JSON `null` when `runner_wrapper.use_clip_grad: false`, when `net_outputs` has fewer than 5 elements, or when the tensor value itself is `None`.
- Setting `runner_wrapper.use_clip_grad: true` in YAML is mandatory for non-null `global_norm`.
- LR extraction should prefer `cb_params.net_outputs[3]` because it reflects the LR actually applied in the current step.
- `cb_params.optimizer.get_lr()` is a fallback when `MFTrainOneStepCell` output is unavailable or shorter than expected, but it may have one-step scheduler lag.
- `step % N == 0` is true for `step == 0`; callback code should guard `if step == 0: return` before interval checks.
- File writes inside `step_end` should catch `OSError` and emit a warning instead of aborting the training loop.
- The callback module must be imported before the Trainer reads YAML so the class is present in `MindFormerRegister`.

**Potential skill**: yes — The two-path LR extraction pattern (`net_outputs[3]` primary plus `optimizer.get_lr()` fallback) combined with the `MFTrainOneStepCell` output-index contract is MindFormers-specific and repeatable. Do not promote yet; wait for a second successful evidence-backed task with the same trigger.
