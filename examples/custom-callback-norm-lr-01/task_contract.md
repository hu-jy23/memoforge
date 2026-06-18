# Task Contract

## Objective

Implement a MindFormers callback named `NormLRLogger` that records training `step`, `learning_rate`, `global_norm`, and UTC timestamp to a JSONL file every configured interval.

## Inputs / Outputs

- Inputs:
  - MindSpore callback runtime context from `step_end`.
  - MindFormers `MFTrainOneStepCell` outputs where available.
  - YAML callback configuration.
- Expected outputs:
  - `workspace/patch/custom-callback-norm-lr-01/norm_lr_logger.py`
  - `workspace/patch/custom-callback-norm-lr-01/training_config_example.yaml`
  - A callback that can be registered through `MindFormerRegister` and configured from YAML.

## Constraints

- Use `@MindFormerRegister.register(MindFormerModuleType.CALLBACK)`.
- Do not interrupt training when LR or global norm cannot be extracted.
- Use append-mode JSONL output so resumed training preserves earlier records.
- Record `global_norm` as `null` when gradient clipping is disabled or unavailable.
- Document that `runner_wrapper.use_clip_grad: true` is required for non-null `global_norm`.
- Keep the patch self-contained and suitable for insertion into an existing MindFormers training repo.

## Validation Command

```bash
python3 -m py_compile workspace/patch/custom-callback-norm-lr-01/norm_lr_logger.py
```

## Evaluation Command

No separate benchmark command. Runtime behavior requires a MindFormers + MindSpore training environment and Ascend hardware, which is outside this local sample cycle.

## Promotion Criteria

- Candidate passes Python syntax validation.
- Manual inspection confirms registration, JSONL append behavior, `step == 0` guard, `OSError` guard, LR extraction from `net_outputs[3]`, and `global_norm` extraction from `net_outputs[4]`.
- Learning record should mark the two-path LR extraction as a potential skill only after evidence is cited.
- Skill promotion requires a second successful task using the same MindFormers LR/global-norm extraction pattern.

## Out Of Scope

- End-to-end Ascend 910 training validation.
- Multi-version compatibility guards for MindFormers versions older than 0.6.
- Packaging the callback as an installable Python module.
