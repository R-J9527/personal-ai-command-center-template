#!/usr/bin/env python3
"""Validate workbench JSON and inject it into the standalone HTML template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


VALID_STATUSES = {"red", "yellow", "green"}
VALID_SPACES = {"work", "life"}
REQUIRED_PROJECT_FIELDS = {
    "id",
    "space",
    "name",
    "summary",
    "status",
    "status_reason",
    "owner",
    "next_action",
    "due",
    "blocker",
    "decision",
    "done_criteria",
    "check_date",
    "links",
}


def validate(data: dict[str, Any]) -> None:
    for field in ("profile", "today", "projects", "upcoming", "updated_at"):
        if field not in data:
            raise ValueError(f"Missing top-level field: {field}")

    projects = data["projects"]
    if not isinstance(projects, list):
        raise ValueError("projects must be a list")

    ids: set[str] = set()
    for index, project in enumerate(projects):
        missing = REQUIRED_PROJECT_FIELDS - set(project)
        if missing:
            raise ValueError(f"Project {index} missing: {', '.join(sorted(missing))}")
        project_id = project["id"]
        if not isinstance(project_id, str) or not project_id:
            raise ValueError(f"Project {index} has an invalid id")
        if project_id in ids:
            raise ValueError(f"Duplicate project id: {project_id}")
        ids.add(project_id)
        if project["status"] not in VALID_STATUSES:
            raise ValueError(f"Project {project_id} has invalid status")
        if project["space"] not in VALID_SPACES:
            raise ValueError(f"Project {project_id} has invalid space")
        if not isinstance(project["links"], list):
            raise ValueError(f"Project {project_id} links must be a list")

    today = data["today"]
    pushes = today.get("important_pushes", [])
    if len(pushes) > 2:
        raise ValueError("today.important_pushes may contain at most two items")
    buffer_percent = today.get("buffer_percent")
    if not isinstance(buffer_percent, (int, float)) or not 0 <= buffer_percent <= 100:
        raise ValueError("today.buffer_percent must be between 0 and 100")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    data = json.loads(args.data.read_text(encoding="utf-8"))
    validate(data)
    template = args.template.read_text(encoding="utf-8")
    marker = "__WORKBENCH_DATA__"
    if template.count(marker) != 1:
        raise ValueError(f"Template must contain exactly one {marker} marker")

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    rendered = template.replace(marker, payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Rendered {args.output} with {len(data['projects'])} projects")


if __name__ == "__main__":
    main()
