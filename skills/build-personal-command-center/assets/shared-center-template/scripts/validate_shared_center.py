#!/usr/bin/env python3
"""Validate a coordination-only private shared fact center."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REFERENCE = re.compile(r"^(none|[A-Za-z0-9][A-Za-z0-9._-]{0,63})$")
STATUSES = {"assigned", "accepted", "in_progress", "waiting", "done", "declined"}
HEALTH = {"red", "yellow", "green"}
PRIORITIES = {"high", "medium", "low"}
FIELDS = {
    "schema_version", "id", "title", "assigner_id", "assignee_id", "project_id",
    "safe_context", "priority", "status", "health", "status_reason", "due",
    "next_action", "blocker", "done_criteria", "check_date", "source_reference",
    "safe_evidence", "confidentiality", "revision", "updated_at", "updated_by",
}
FORBIDDEN = (
    (re.compile(r"https?://", re.I), "URL"),
    (re.compile(r"file://", re.I), "local URL"),
    (re.compile(r"(?:^|\s)/(?:Users|home|Volumes)/"), "local path"),
    (re.compile(r"[A-Za-z]:[\\/]"), "Windows path"),
    (re.compile(r"\\\\[^\\\s]+\\"), "network path"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"\b(?:api[_-]?key|access[_-]?token|secret)\s*[:=]", re.I), "credential"),
    (re.compile(r"\bgh[opstu]_[A-Za-z0-9]{10,}"), "GitHub token"),
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: must be a non-empty string")
    for pattern, kind in FORBIDDEN:
        if pattern.search(value):
            raise ValueError(f"{label}: contains prohibited {kind}")
    return value


def validate_members() -> set[str]:
    path = DATA / "members.json"
    data = load(path)
    if set(data) != {"schema_version", "members"} or data["schema_version"] != 1:
        raise ValueError(f"{path}: invalid member structure")
    ids: set[str] = set()
    for index, member in enumerate(data["members"]):
        if not isinstance(member, dict) or set(member) != {"id", "display_name", "github_username"}:
            raise ValueError(f"{path}: member {index} has invalid fields")
        member_id = text(member["id"], f"{path}: member {index}.id")
        text(member["display_name"], f"{path}: member {index}.display_name")
        text(member["github_username"], f"{path}: member {index}.github_username")
        if not ID.fullmatch(member_id) or member_id in ids:
            raise ValueError(f"{path}: invalid or duplicate member id {member_id!r}")
        ids.add(member_id)
    return ids


def validate_task(path: Path, members: set[str]) -> str:
    task = load(path)
    if set(task) != FIELDS or task["schema_version"] != 1:
        raise ValueError(f"{path}: fields do not match task contract")
    if not ID.fullmatch(task["id"]) or path.stem != task["id"]:
        raise ValueError(f"{path}: task id must match its filename")
    for field in FIELDS - {"schema_version", "revision"}:
        if isinstance(task[field], str):
            text(task[field], f"{path}: {field}")
    if task["status"] not in STATUSES or task["health"] not in HEALTH or task["priority"] not in PRIORITIES:
        raise ValueError(f"{path}: invalid status, health, or priority")
    if task["confidentiality"] != "coordination_only":
        raise ValueError(f"{path}: confidentiality must be coordination_only")
    if not REFERENCE.fullmatch(task["source_reference"]):
        raise ValueError(f"{path}: source_reference must be an opaque code or 'none'")
    referenced = {task["assigner_id"], task["assignee_id"], task["updated_by"]}
    if members and not referenced <= members:
        raise ValueError(f"{path}: references unknown members {sorted(referenced - members)}")
    if not isinstance(task["revision"], int) or task["revision"] < 1:
        raise ValueError(f"{path}: revision must be positive")
    if task["due"] != "TBD":
        datetime.fromisoformat(task["due"].replace("Z", "+00:00"))
    if task["check_date"] != "TBD":
        date.fromisoformat(task["check_date"][:10])
    datetime.fromisoformat(task["updated_at"].replace("Z", "+00:00"))
    return task["id"]


def main() -> None:
    members = validate_members()
    task_ids: set[str] = set()
    for path in sorted((DATA / "tasks").glob("*.json")):
        task_id = validate_task(path, members)
        if task_id in task_ids:
            raise ValueError(f"duplicate task id: {task_id}")
        task_ids.add(task_id)
    print(f"Valid private shared center: {len(members)} members, {len(task_ids)} tasks")


if __name__ == "__main__":
    main()
