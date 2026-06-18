# Promotion Decision

## Candidate Decision

- Decision: accept
- Candidate ID: `custom-callback-norm-lr-01-candidate-01`
- Task ID: `custom-callback-norm-lr-01`

## Evidence Summary

- Evidence refs:
  - `workspace/evidence/custom-callback-norm-lr-01/commands.log`
  - `workspace/evidence/custom-callback-norm-lr-01/manual-inspection.md`
  - `workspace/evidence/custom-callback-norm-lr-01/artifact_protocol.log`
- Verification result: pass

## Memory Write-back Recommendation

- learning: yes
- notes: yes
- wiki: no
- skills: no

## Skill Promotion Recommendation

- Promote to skill: no
- Evidence threshold: at least one more successful evidence-backed task using the same MindFormers LR/global-norm extraction trigger and pattern.
- Required follow-up: after the second pass, Memory Agent may draft a skill package under `agents/memory/store/skills/` with cited evidence from both task cycles.

## Wiki / Notes Update Recommendation

- Wiki update: no
- Notes update: yes
- Destination: `agents/memory/store/notes/mf-train-wrappers.md`
- Freshness / provenance requirement: keep this as task-backed observation unless independently verified against source docs or repeated in another task.

## Rationale

The candidate satisfies the local task contract through syntax validation and manual inspection of the domain-specific callback behavior. The two-path LR extraction pattern and `MFTrainOneStepCell` output-index contract should be retained in learning and notes because they are MindFormers-specific and likely reusable.

Do not promote to a skill yet. The pattern has one successful evidence-backed task cycle; promotion requires at least one more successful task with the same trigger and extraction pattern.

Do not update wiki directly from this single task. The observed facts should first enter notes as task-backed observations unless independently confirmed by existing wiki pages.

## Residual Risks

- End-to-end Ascend/MindFormers runtime validation was not executed.
- `optimizer.get_lr()` fallback may have one-step lag for some scheduler implementations.
- Pipeline-parallel `cur_step_num` semantics can differ by MindFormers version.
