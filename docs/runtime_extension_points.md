# Runtime Extension Points

MemoForge keeps the four-main-agent design. Runtime extensions must plug into that design instead of creating new top-level roles.

`runtime/extension_manifest.json` is the machine-checkable registry for these reserved positions. Validate it with:

```bash
python3 tools/validate_runtime_extensions.py
```

## Lightweight Subagents

Each main agent may use lightweight subagents for local work:

- Planner: focused research or route probing.
- Coder: parallel code exploration or isolated candidate analysis.
- Verifier: independent validation fan-out.
- Memory Agent: batch wiki/notes scanning or consolidation.

Rules:

- Subagents inherit the main agent's responsibility boundary.
- Subagents return distilled results to the main agent.
- Subagents do not become persistent roles.
- Persistent memory writes still go through Memory Agent.

## Tool-call Repair Layer

Tool-call repair belongs below the agent prompts, in the future runtime/tool adapter layer.

Reserved repair hooks:

- `schema_flatten`: present complex tool schemas to the model in a flatter form, then restore structure before dispatch.
- `tool_scavenge`: recover tool calls that the model emitted in reasoning text but failed to emit as structured calls.
- `truncation_repair`: detect truncated tool-call JSON and request continuation or repair safely.
- `storm_suppression`: detect repeated identical tool calls and interrupt the loop with a reflection signal.

Current status:

- Reserved design position only.
- Do not simulate these behaviors in Planner/Coder/Verifier prompts.
- Implement when the harness owns the tool runtime.

## Hooks

Hooks are lifecycle governance slots. They are useful, but not urgent until a concrete enforcement or evidence-capture need appears.

Reserved hook points:

- `UserPromptSubmit`: before task classification and alignment gate checks.
- `PreToolUse`: before command/tool dispatch.
- `PostToolUse`: after command/tool result.
- `Stop`: before a task cycle ends.

Possible future uses:

- command approval
- artifact completeness checks
- evidence capture
- write-back trigger checks
- policy enforcement
- audit logging

Current status:

- Keep hook positions explicit in design docs.
- Avoid adding a complex hook framework until real task cycles require it.

## Slash Commands

Slash commands are user-facing control surfaces handled by Planner.

Reserved command:

- `/goal`: create, resume, inspect, audit, complete, or block a long-horizon goal.

Current status:

- Reserved design position with prompt-level behavior.
- No separate runtime command dispatcher yet.
- `/goal create` must run Alignment Starter before execution.
