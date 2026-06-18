# Runtime Extension Layer

This directory records reserved runtime extension points without adding a new top-level agent layer.

Files:

- `extension_manifest.json`: machine-checkable extension point registry

Current policy:

- Lightweight subagents are allowed inside the four main agents.
- Tool-call repair points are reserved for a future tool adapter layer.
- Lifecycle hooks are reserved for future governance and evidence capture.
- Disabled or reserved extensions must remain explicit so future implementation can be audited against the original design.
