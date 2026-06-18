#!/usr/bin/env python3
"""Validate reserved MemoForge runtime extension points."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "runtime" / "extension_manifest.json"
DOC = ROOT / "docs" / "runtime_extension_points.md"

REQUIRED_LIGHTWEIGHT_SUBAGENTS = {"planner", "coder", "verifier", "memory"}
REQUIRED_REPAIR_POINTS = {
    "schema_flatten",
    "tool_scavenge",
    "truncation_repair",
    "storm_suppression",
}
REQUIRED_HOOKS = {"UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"}
REQUIRED_SLASH_COMMANDS = {"goal"}
ALLOWED_STATUS = {"allowed", "reserved", "disabled"}


def load_manifest(errors: list[str]) -> dict[str, Any]:
    if not MANIFEST.exists():
        errors.append(f"missing manifest: {MANIFEST.relative_to(ROOT)}")
        return {}
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json: runtime/extension_manifest.json:{exc.lineno}:{exc.colno}: {exc.msg}")
        return {}
    if not isinstance(data, dict):
        errors.append("runtime/extension_manifest.json must be a json object")
        return {}
    return data


def require_keys(mapping: dict[str, Any], keys: set[str], label: str, errors: list[str]) -> None:
    missing = sorted(keys - set(mapping))
    for key in missing:
        errors.append(f"{label}: missing {key}")


def validate_entries(entries: dict[str, Any], label: str, required_field: str, errors: list[str]) -> None:
    for name, value in entries.items():
        if not isinstance(value, dict):
            errors.append(f"{label}.{name}: must be an object")
            continue
        status = value.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(f"{label}.{name}: invalid status: {status!r}")
        if not isinstance(value.get(required_field), str) or not value.get(required_field):
            errors.append(f"{label}.{name}: missing string field: {required_field}")


def validate_doc_mentions(errors: list[str]) -> None:
    if not DOC.exists():
        errors.append(f"missing doc: {DOC.relative_to(ROOT)}")
        return
    text = DOC.read_text(encoding="utf-8")
    text_lower = text.lower()
    doc_tokens = REQUIRED_LIGHTWEIGHT_SUBAGENTS | REQUIRED_REPAIR_POINTS | REQUIRED_HOOKS | {"/goal"}
    for token in sorted(doc_tokens):
        if token not in text and token.lower() not in text_lower:
            errors.append(f"docs/runtime_extension_points.md does not mention: {token}")


def main() -> int:
    errors: list[str] = []
    manifest = load_manifest(errors)
    if not manifest:
        for error in errors:
            print(f"- {error}")
        return 1

    if manifest.get("version") != 1:
        errors.append("manifest version must be 1")
    if not isinstance(manifest.get("principle"), str) or not manifest.get("principle"):
        errors.append("manifest missing principle")

    extension_points = manifest.get("extension_points")
    if not isinstance(extension_points, dict):
        errors.append("manifest missing object: extension_points")
        extension_points = {}

    lightweight = extension_points.get("lightweight_subagents")
    if not isinstance(lightweight, dict):
        errors.append("extension_points.lightweight_subagents must be an object")
        lightweight = {}
    require_keys(lightweight, REQUIRED_LIGHTWEIGHT_SUBAGENTS, "lightweight_subagents", errors)
    validate_entries(lightweight, "lightweight_subagents", "boundary", errors)

    repair = extension_points.get("tool_call_repair")
    if not isinstance(repair, dict):
        errors.append("extension_points.tool_call_repair must be an object")
        repair = {}
    require_keys(repair, REQUIRED_REPAIR_POINTS, "tool_call_repair", errors)
    validate_entries(repair, "tool_call_repair", "trigger", errors)
    for name, value in repair.items():
        if isinstance(value, dict) and value.get("owner_layer") != "future tool adapter":
            errors.append(f"tool_call_repair.{name}: owner_layer must be future tool adapter")

    hooks = extension_points.get("hooks")
    if not isinstance(hooks, dict):
        errors.append("extension_points.hooks must be an object")
        hooks = {}
    require_keys(hooks, REQUIRED_HOOKS, "hooks", errors)
    validate_entries(hooks, "hooks", "purpose", errors)

    slash_commands = extension_points.get("slash_commands")
    if not isinstance(slash_commands, dict):
        errors.append("extension_points.slash_commands must be an object")
        slash_commands = {}
    require_keys(slash_commands, REQUIRED_SLASH_COMMANDS, "slash_commands", errors)
    validate_entries(slash_commands, "slash_commands", "purpose", errors)

    validate_doc_mentions(errors)

    if errors:
        print("Runtime extension validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Runtime extension validation passed: "
        f"subagents={len(lightweight)} repair={len(repair)} hooks={len(hooks)} slash_commands={len(slash_commands)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
