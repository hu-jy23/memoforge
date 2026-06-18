---
title: Config Change Validation Workflow
category: workflows
sources: ["AGENTS.md — change validation"]
last_updated: 2026-05-17
confidence: high
---

Before adding any code, config field, script argument, environment variable, or structured change, trace the **full upstream and downstream path**.

**Validation checklist:**
1. Identify who produces the value (config file? CLI argument? computed?)
2. Identify who parses it (which builder? which API consumer?)
3. Identify who mutates it (if any transformation happens)
4. Identify who consumes it (MindSpore? ModelArts? WandB? OBS?)
5. Verify against the real consumer API, not name similarity

**Critical validation paths:** For changes to `parallel`, `context`, `parallel_config`, optimizer, wrapper, and callback fields, inspect the corresponding builder code before editing. YAML parsing alone is insufficient.

**Workflow:** Test config changes against the closest known-good baseline (`configs/qwen3/wsdsc_qwen3_0b5_1m_30b_no_shuffle.yaml` for qwen3). Review the final diff to ensure only intended fields changed.

**Example:** To add a new callback field, trace: config YAML → callback constructor → MindSpore/SwanLab API. Verify the field name and type match the API signature.