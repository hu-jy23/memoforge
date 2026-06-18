#!/usr/bin/env python3
"""Validate Goal Harness and Alignment Starter structural integration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "docs/alignment_starter_protocol.md",
    "docs/goal_harness.md",
    "docs/templates/alignment_plan.md",
    "docs/templates/goal_contract.md",
    "goals/README.md",
    "goals/active/README.md",
]

REQUIRED_PREFIX_SHARED = {
    "docs/alignment_starter_protocol.md",
    "docs/goal_harness.md",
}

REQUIRED_PLANNER_TOKENS = [
    "Alignment Starter",
    "MultiAlignment",
    "/goal create",
    "goals/active/plan.md",
    "goals/active/goal_contract.md",
]

REQUIRED_ALIGNMENT_TEMPLATE_TOKENS = [
    "Source Section",
    "MultiAlignment Questions",
    "Agent Propose QA",
    "Double Check",
]

REQUIRED_GOAL_TEMPLATE_TOKENS = [
    "Objective",
    "Success Criteria",
    "Required Evidence For Completion",
    "Audit Policy",
]


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing json: {path.relative_to(ROOT)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid json: {path.relative_to(ROOT)}:{exc.lineno}:{exc.colno}: {exc.msg}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"json root must be object: {path.relative_to(ROOT)}")
        return {}
    return data


def require_file(path: str, errors: list[str]) -> None:
    abs_path = ROOT / path
    if not abs_path.is_file():
        errors.append(f"missing file: {path}")


def require_tokens(path: str, tokens: list[str], errors: list[str]) -> None:
    abs_path = ROOT / path
    if not abs_path.is_file():
        errors.append(f"missing file for token check: {path}")
        return
    text = abs_path.read_text(encoding="utf-8")
    for token in tokens:
        if token not in text:
            errors.append(f"{path} missing token: {token}")


def validate_prefix_manifest(errors: list[str]) -> None:
    manifest = load_json(ROOT / "context" / "prefix_manifest.json", errors)
    shared = manifest.get("shared", [])
    if not isinstance(shared, list):
        errors.append("context/prefix_manifest.json shared must be a list")
        return
    shared_paths = {entry.get("path") for entry in shared if isinstance(entry, dict)}
    for required in sorted(REQUIRED_PREFIX_SHARED - shared_paths):
        errors.append(f"context/prefix_manifest.json shared missing: {required}")


def validate_runtime_manifest(errors: list[str]) -> None:
    manifest = load_json(ROOT / "runtime" / "extension_manifest.json", errors)
    extension_points = manifest.get("extension_points", {})
    if not isinstance(extension_points, dict):
        errors.append("runtime/extension_manifest.json missing extension_points")
        return
    slash_commands = extension_points.get("slash_commands", {})
    if not isinstance(slash_commands, dict) or "goal" not in slash_commands:
        errors.append("runtime/extension_manifest.json missing slash_commands.goal")


def main() -> int:
    errors: list[str] = []

    for path in REQUIRED_FILES:
        require_file(path, errors)

    require_tokens("CLAUDE.md", REQUIRED_PLANNER_TOKENS, errors)
    require_tokens("docs/templates/alignment_plan.md", REQUIRED_ALIGNMENT_TEMPLATE_TOKENS, errors)
    require_tokens("docs/templates/goal_contract.md", REQUIRED_GOAL_TEMPLATE_TOKENS, errors)
    validate_prefix_manifest(errors)
    validate_runtime_manifest(errors)

    if errors:
        print("Goal/alignment validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("goal_alignment_validation_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
