#!/usr/bin/env python3
"""Validate the MemoForge task artifact protocol."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKSPACE = ROOT / "workspace"
DEFAULT_LEARNING_ROOT = ROOT / "agents" / "memory" / "store" / "learning"

TASK_CONTRACT_SECTIONS = [
    "objective",
    "inputs / outputs",
    "constraints",
    "validation command",
    "promotion criteria",
    "out of scope",
]

PROMOTION_SECTIONS = [
    "candidate decision",
    "evidence summary",
    "memory write-back recommendation",
    "skill promotion recommendation",
    "wiki / notes update recommendation",
    "residual risks",
]

CANDIDATE_FIELDS = {
    "candidate_id",
    "task_id",
    "parent_id",
    "role",
    "status",
    "summary",
    "artifact_refs",
    "evidence_refs",
    "timestamp",
}
CANDIDATE_ROLES = {"coder", "verifier"}
CANDIDATE_STATUSES = {
    "proposed",
    "implemented",
    "pass",
    "fail",
    "partial",
    "rejected",
    "promoted",
}

VERIFY_FIELDS = {
    "task_id",
    "candidate_id",
    "status",
    "log_summary",
    "failure_reason",
    "success_pattern",
    "potential_skill",
    "evidence_refs",
    "findings",
    "suggested_fix",
}
VERIFY_STATUSES = {"pass", "fail", "partial", "blocked"}


@dataclass
class CheckResult:
    errors: list[str]
    warnings: list[str]

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def resolve_ref(ref: str, workspace: Path) -> Path:
    path = Path(ref)
    if path.is_absolute():
        return path
    if ref == "workspace":
        return workspace
    if ref.startswith("workspace/"):
        return workspace / ref.removeprefix("workspace/")
    return ROOT / path


def markdown_sections(text: str) -> set[str]:
    sections: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^#{2,6}\s+(.+?)\s*$", line)
        if match:
            sections.add(match.group(1).strip().lower())
    return sections


def require_file(result: CheckResult, path: Path) -> bool:
    if not path.exists():
        result.error(f"missing file: {rel(path)}")
        return False
    if not path.is_file():
        result.error(f"not a file: {rel(path)}")
        return False
    return True


def load_json(result: CheckResult, path: Path) -> Any | None:
    if not require_file(result, path):
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        result.error(f"invalid json: {rel(path)}:{exc.lineno}:{exc.colno}: {exc.msg}")
        return None


def validate_task_contract(result: CheckResult, path: Path) -> None:
    if not require_file(result, path):
        return
    text = path.read_text(encoding="utf-8")
    sections = markdown_sections(text)
    for section in TASK_CONTRACT_SECTIONS:
        if section not in sections:
            result.error(f"{rel(path)} missing section: {section}")
    if "```" not in text:
        result.warn(f"{rel(path)} has no fenced validation command block")


def validate_plan(result: CheckResult, path: Path, workspace: Path) -> str | None:
    data = load_json(result, path)
    if not isinstance(data, dict):
        result.error(f"{rel(path)} must be a json object")
        return None

    task_id = data.get("task_id")
    if not isinstance(task_id, str) or not task_id:
        result.error(f"{rel(path)} missing string field: task_id")
    if not isinstance(data.get("goal"), str) or not data.get("goal"):
        result.error(f"{rel(path)} missing string field: goal")

    subtasks = data.get("subtasks")
    if not isinstance(subtasks, list) or not subtasks:
        result.error(f"{rel(path)} missing non-empty list field: subtasks")
        return task_id if isinstance(task_id, str) else None

    seen_ids: set[str] = set()
    for index, subtask in enumerate(subtasks, 1):
        if not isinstance(subtask, dict):
            result.error(f"{rel(path)} subtasks[{index}] must be an object")
            continue
        subtask_id = subtask.get("id")
        if not isinstance(subtask_id, str) or not subtask_id:
            result.error(f"{rel(path)} subtasks[{index}] missing string field: id")
        elif subtask_id in seen_ids:
            result.error(f"{rel(path)} duplicate subtask id: {subtask_id}")
        else:
            seen_ids.add(subtask_id)

        for field in ("description",):
            if not isinstance(subtask.get(field), str) or not subtask.get(field):
                result.error(f"{rel(path)} subtasks[{index}] missing string field: {field}")

        for field in ("context_refs", "depends_on"):
            if not isinstance(subtask.get(field), list):
                result.error(f"{rel(path)} subtasks[{index}] missing list field: {field}")

        for context_ref in subtask.get("context_refs", []):
            if not isinstance(context_ref, str):
                result.error(f"{rel(path)} subtasks[{index}] has non-string context_ref")
                continue
            if not resolve_ref(context_ref, workspace).exists():
                result.warn(f"{rel(path)} context_ref does not exist: {context_ref}")

    for subtask in subtasks:
        if not isinstance(subtask, dict):
            continue
        for dependency in subtask.get("depends_on", []):
            if dependency not in seen_ids:
                result.error(f"{rel(path)} unknown dependency: {dependency}")

    return task_id if isinstance(task_id, str) else None


def validate_candidates(result: CheckResult, path: Path, task_id: str, workspace: Path) -> list[dict[str, Any]]:
    if not require_file(result, path):
        return []

    candidates: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            result.error(f"{rel(path)}:{line_number}: invalid jsonl: {exc.msg}")
            continue
        if not isinstance(entry, dict):
            result.error(f"{rel(path)}:{line_number}: candidate entry must be an object")
            continue

        missing = sorted(CANDIDATE_FIELDS - set(entry))
        for field in missing:
            result.error(f"{rel(path)}:{line_number}: missing field: {field}")

        if entry.get("task_id") != task_id:
            result.error(f"{rel(path)}:{line_number}: task_id mismatch: {entry.get('task_id')!r}")
        if entry.get("role") not in CANDIDATE_ROLES:
            result.error(f"{rel(path)}:{line_number}: invalid role: {entry.get('role')!r}")
        if entry.get("status") not in CANDIDATE_STATUSES:
            result.error(f"{rel(path)}:{line_number}: invalid status: {entry.get('status')!r}")
        if not isinstance(entry.get("candidate_id"), str) or not entry.get("candidate_id"):
            result.error(f"{rel(path)}:{line_number}: missing candidate_id")
        if not isinstance(entry.get("summary"), str) or not entry.get("summary"):
            result.error(f"{rel(path)}:{line_number}: missing summary")

        for field in ("artifact_refs", "evidence_refs"):
            refs = entry.get(field)
            if not isinstance(refs, list):
                result.error(f"{rel(path)}:{line_number}: {field} must be a list")
                continue
            for item in refs:
                if not isinstance(item, str):
                    result.error(f"{rel(path)}:{line_number}: {field} contains non-string ref")
                    continue
                if not resolve_ref(item, workspace).exists():
                    result.error(f"{rel(path)}:{line_number}: {field} missing ref: {item}")

        candidates.append(entry)

    if not candidates:
        result.error(f"{rel(path)} has no candidate entries")
    if not any(c.get("role") == "coder" and c.get("status") == "implemented" for c in candidates):
        result.error(f"{rel(path)} has no implemented coder candidate")

    return candidates


def validate_verify_result(
    result: CheckResult,
    path: Path,
    task_id: str,
    candidates: list[dict[str, Any]],
    workspace: Path,
) -> dict[str, Any] | None:
    data = load_json(result, path)
    if not isinstance(data, dict):
        result.error(f"{rel(path)} must be a json object")
        return None

    missing = sorted(VERIFY_FIELDS - set(data))
    for field in missing:
        result.error(f"{rel(path)} missing field: {field}")

    if data.get("task_id") != task_id:
        result.error(f"{rel(path)} task_id mismatch: {data.get('task_id')!r}")
    if data.get("status") not in VERIFY_STATUSES:
        result.error(f"{rel(path)} invalid status: {data.get('status')!r}")

    candidate_id = data.get("candidate_id")
    candidate_ids = {c.get("candidate_id") for c in candidates}
    if candidate_id not in candidate_ids:
        result.error(f"{rel(path)} candidate_id not in candidates.jsonl: {candidate_id!r}")

    evidence_refs = data.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        result.error(f"{rel(path)} evidence_refs must be a non-empty list")
    else:
        for ref_item in evidence_refs:
            if not isinstance(ref_item, str):
                result.error(f"{rel(path)} evidence_refs contains non-string ref")
                continue
            if not resolve_ref(ref_item, workspace).exists():
                result.error(f"{rel(path)} evidence ref missing: {ref_item}")

    if data.get("status") == "pass":
        matching_pass = [
            c for c in candidates
            if c.get("candidate_id") == candidate_id
            and c.get("role") == "verifier"
            and c.get("status") == "pass"
        ]
        if not matching_pass:
            result.error(f"{rel(path)} status pass has no matching verifier pass ledger entry")

    return data


def validate_evidence_dir(result: CheckResult, workspace: Path, task_id: str) -> None:
    evidence_dir = workspace / "evidence" / task_id
    if not evidence_dir.exists():
        result.error(f"missing evidence directory: {rel(evidence_dir)}")
        return
    if not evidence_dir.is_dir():
        result.error(f"not a directory: {rel(evidence_dir)}")
        return
    evidence_files = [p for p in evidence_dir.iterdir() if p.is_file()]
    if not evidence_files:
        result.error(f"empty evidence directory: {rel(evidence_dir)}")


def validate_promotion_decision(result: CheckResult, path: Path, task_id: str, verify_result: dict[str, Any] | None) -> None:
    if not require_file(result, path):
        return
    text = path.read_text(encoding="utf-8")
    sections = markdown_sections(text)
    for section in PROMOTION_SECTIONS:
        if section not in sections:
            result.error(f"{rel(path)} missing section: {section}")

    if task_id not in text:
        result.error(f"{rel(path)} does not cite task_id: {task_id}")
    if verify_result:
        candidate_id = verify_result.get("candidate_id")
        if isinstance(candidate_id, str) and candidate_id not in text:
            result.error(f"{rel(path)} does not cite candidate_id: {candidate_id}")
        for evidence_ref in verify_result.get("evidence_refs", []):
            if isinstance(evidence_ref, str) and evidence_ref not in text:
                result.error(f"{rel(path)} does not cite evidence ref: {evidence_ref}")


def validate_learning(
    result: CheckResult,
    task_id: str,
    verify_result: dict[str, Any] | None,
    learning_root: Path,
) -> None:
    path = learning_root / f"{task_id}.md"
    if not require_file(result, path):
        return
    text = path.read_text(encoding="utf-8")
    required_fragments = [
        "workspace/task_contract.md",
        "workspace/candidates.jsonl",
        "workspace/verify_result.json",
        "workspace/promotion_decision.md",
    ]
    if verify_result:
        candidate_id = verify_result.get("candidate_id")
        if isinstance(candidate_id, str):
            required_fragments.append(candidate_id)
        for evidence_ref in verify_result.get("evidence_refs", []):
            if isinstance(evidence_ref, str):
                required_fragments.append(evidence_ref)

    for fragment in required_fragments:
        if fragment not in text:
            result.error(f"{rel(path)} missing citation: {fragment}")


def validate_workspace(
    workspace: Path,
    task_id_arg: str | None,
    require_learning: bool,
    learning_root: Path,
) -> CheckResult:
    result = CheckResult(errors=[], warnings=[])
    validate_task_contract(result, workspace / "task_contract.md")

    plan_task_id = validate_plan(result, workspace / "plan.json", workspace)
    task_id = task_id_arg or plan_task_id
    if not task_id:
        result.error("cannot determine task_id from --task-id or workspace/plan.json")
        return result
    if task_id_arg and plan_task_id and task_id_arg != plan_task_id:
        result.error(f"--task-id {task_id_arg!r} does not match plan task_id {plan_task_id!r}")

    candidates = validate_candidates(result, workspace / "candidates.jsonl", task_id, workspace)
    validate_evidence_dir(result, workspace, task_id)
    verify_result = validate_verify_result(result, workspace / "verify_result.json", task_id, candidates, workspace)
    validate_promotion_decision(result, workspace / "promotion_decision.md", task_id, verify_result)
    if require_learning:
        validate_learning(result, task_id, verify_result, learning_root)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=str(DEFAULT_WORKSPACE), help="Workspace directory")
    parser.add_argument(
        "--learning-root",
        default=str(DEFAULT_LEARNING_ROOT),
        help="Directory containing {task_id}.md learning records.",
    )
    parser.add_argument("--task-id", help="Expected task_id. Defaults to plan.json task_id.")
    parser.add_argument(
        "--require-learning",
        action="store_true",
        help="Also require agents/memory/store/learning/{task_id}.md to cite task artifacts.",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace)
    if not workspace.is_absolute():
        workspace = ROOT / workspace
    learning_root = Path(args.learning_root)
    if not learning_root.is_absolute():
        learning_root = ROOT / learning_root

    result = validate_workspace(workspace, args.task_id, args.require_learning, learning_root)
    for warning in result.warnings:
        print(f"warning: {warning}")
    for error in result.errors:
        print(f"error: {error}")

    if result.errors:
        print(f"artifact_protocol_fail errors={len(result.errors)} warnings={len(result.warnings)}")
        return 1

    task_id = args.task_id or json.loads((workspace / "plan.json").read_text(encoding="utf-8")).get("task_id")
    print(f"artifact_protocol_ok task_id={task_id} warnings={len(result.warnings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
