# Goal Harness

## Purpose

Goal Harness gives the project a persistent long-horizon controller similar to Codex `/goal`.

It keeps the objective, alignment artifacts, status, progress, blockers, and completion audit outside a single chat turn.

## Command Surface

`/goal` is a slash-command-style capability. It plugs into Planner and does not create a fifth main agent.

Planner dispatches this command only when the user explicitly enters `/goal ...`. Default Alignment Starter does not automatically start Goal Harness.

| Command | Behavior |
|---|---|
| `/goal create` | Run Alignment Starter, create `goals/active/plan.md`, create `goals/active/goal_contract.md`, ask for user double check |
| `/goal status` | Report objective, current status, latest progress, budget, blockers, and next task |
| `/goal continue` | Resume from `goals/active/goal_contract.md` and `goals/active/status.json` |
| `/goal audit` | Decide continue, complete, or blocked from available evidence |
| `/goal complete` | Mark complete only when evidence satisfies the goal contract |
| `/goal block` | Mark blocked only after repeated blocker evidence shows no meaningful progress is possible |

## Persistent Files

Goal-level state lives in:

```text
goals/active/
```

Task-cycle state still lives in:

```text
workspace/
```

This separation matters because `workspace/` is ephemeral and safe to delete between task cycles. A long-horizon goal must survive task-cycle cleanup.

## Goal Contract

`goals/active/goal_contract.md` records:

- objective
- user-approved plan reference
- scope
- non-goals
- required sources
- constraints
- autonomy boundaries
- success criteria
- evidence required for completion
- first task-cycle seed

## Status State

`goals/active/status.json` records:

- goal id
- state: `aligning`, `active`, `blocked`, `complete`
- token or budget limit when available
- current task id
- completed task ids
- latest evidence refs
- blocker summary
- next action

## Audit Rule

The goal is complete only when the evidence satisfies the original goal contract.

The goal is blocked only when the same blocker repeats and the agent cannot make meaningful progress without user input or an external-state change.

Stopping because of time, budget, or uncertainty is not completion.

## Relation To Task Artifact Protocol

Goal Harness controls the long-horizon loop. Task Artifact Protocol controls one execution cycle.

```text
Goal Contract
  -> task_contract.md
  -> candidates.jsonl
  -> evidence/
  -> promotion_decision.md
  -> goal audit
```
