#!/usr/bin/env python3
"""Import coordination-only assignments from Supabase into a workbench."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


FIELDS = {
    "schema_version",
    "id",
    "title",
    "assigner_id",
    "assignee_id",
    "project_id",
    "safe_context",
    "priority",
    "status",
    "health",
    "status_reason",
    "due",
    "next_action",
    "blocker",
    "done_criteria",
    "check_date",
    "source_reference",
    "safe_evidence",
    "confidentiality",
    "revision",
    "updated_at",
    "updated_by",
}
STATUSES = {"assigned", "accepted", "in_progress", "waiting", "done", "declined"}
HEALTH = {"red", "yellow", "green"}
PRIORITIES = {"high", "medium", "low"}
ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REFERENCE = re.compile(r"^(none|[A-Za-z0-9][A-Za-z0-9._-]{0,63})$")
FORBIDDEN = (
    (re.compile(r"https?://", re.I), "URL"),
    (re.compile(r"file://", re.I), "local URL"),
    (re.compile(r"(?:^|\s)/(?:Users|home|Volumes)/"), "local path"),
    (re.compile(r"[A-Za-z]:[\\/]"), "Windows path"),
    (re.compile(r"\\\\[^\\\s]+\\"), "network path"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (
        re.compile(r"\b(?:api[_-]?key|access[_-]?token|secret)\s*[:=]", re.I),
        "credential",
    ),
    (re.compile(r"\bgh[opstu]_[A-Za-z0-9]{10,}"), "GitHub token"),
)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def safe_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: must be a non-empty string")
    if len(value) > 1000:
        raise ValueError(f"{label}: exceeds the coordination-only size limit")
    for pattern, kind in FORBIDDEN:
        if pattern.search(value):
            raise ValueError(f"{label}: contains prohibited {kind}")
    return value


def validate_task(task: Any, member_id: str) -> dict[str, Any]:
    if not isinstance(task, dict) or set(task) != FIELDS:
        raise ValueError("Supabase task fields do not match the task contract")
    if task["schema_version"] != 1 or not ID.fullmatch(str(task["id"])):
        raise ValueError("Supabase task has an invalid schema version or id")
    for field in FIELDS - {"schema_version", "revision"}:
        safe_text(task[field], f"task {task['id']}.{field}")
    if task["assignee_id"] != member_id:
        raise ValueError(f"task {task['id']} is assigned to a different member")
    if task["status"] not in STATUSES or task["health"] not in HEALTH:
        raise ValueError(f"task {task['id']} has an invalid status or health")
    if (
        task["priority"] not in PRIORITIES
        or task["confidentiality"] != "coordination_only"
    ):
        raise ValueError(f"task {task['id']} violates the coordination-only contract")
    if not REFERENCE.fullmatch(task["source_reference"]):
        raise ValueError(f"task {task['id']} has an invalid source_reference")
    if not isinstance(task["revision"], int) or task["revision"] < 1:
        raise ValueError(f"task {task['id']} has an invalid revision")
    if task["due"] != "TBD":
        datetime.fromisoformat(task["due"].replace("Z", "+00:00"))
    if task["check_date"] != "TBD":
        date.fromisoformat(task["check_date"][:10])
    datetime.fromisoformat(task["updated_at"].replace("Z", "+00:00"))
    return task


def read_config(path: Path) -> dict[str, Any]:
    config = load_object(path)
    if config.get("enabled") is not True or config.get("provider") != "supabase":
        raise ValueError("Supabase shared center is not enabled")
    member_id = config.get("member_id")
    if not isinstance(member_id, str) or not ID.fullmatch(member_id):
        raise ValueError("config.member_id must be a stable lowercase member id")
    if config.get("outbound_status_mode") != "confirm_each":
        raise ValueError("outbound_status_mode must be confirm_each")
    base_url = config.get("supabase_url")
    if not isinstance(base_url, str):
        raise ValueError("config.supabase_url is required")
    parsed = urllib.parse.urlparse(base_url)
    if not parsed.hostname:
        raise ValueError("config.supabase_url must include a hostname")
    if parsed.scheme != "https" and parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise ValueError("supabase_url must use HTTPS except for a local test server")
    return config


def required_environment(config: dict[str, Any]) -> tuple[str, str]:
    key_name = config.get("publishable_key_env", "SUPABASE_PUBLISHABLE_KEY")
    token_name = config.get("access_token_env", "SUPABASE_ACCESS_TOKEN")
    if not isinstance(key_name, str) or not isinstance(token_name, str):
        raise ValueError("credential environment variable names must be strings")
    publishable_key = os.environ.get(key_name)
    access_token = os.environ.get(token_name)
    if not publishable_key or not access_token:
        raise ValueError(f"Set {key_name} and {token_name}; never place their values in config")
    return publishable_key, access_token


def fetch_tasks(config: dict[str, Any]) -> list[dict[str, Any]]:
    publishable_key, access_token = required_environment(config)
    member_id = config["member_id"]
    query = urllib.parse.urlencode(
        {
            "select": "*",
            "assignee_id": f"eq.{member_id}",
            "order": "updated_at.asc",
        }
    )
    url = f"{config['supabase_url'].rstrip('/')}/rest/v1/task_envelopes?{query}"
    request = urllib.request.Request(
        url,
        headers={
            "apikey": publishable_key,
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ValueError("Supabase task response exceeds the 1 MB safety limit")
            payload = json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Supabase task fetch failed with HTTP {error.code}") from None
    except urllib.error.URLError as error:
        raise RuntimeError(f"Supabase task fetch failed: {error.reason}") from None
    if not isinstance(payload, list):
        raise ValueError("Supabase task response must be a list")
    return [validate_task(task, member_id) for task in payload]


def import_tasks(
    config: dict[str, Any], workbench_path: Path, tasks: list[dict[str, Any]], dry_run: bool
) -> None:
    workbench = load_object(workbench_path)
    if dry_run:
        print(
            f"Dry run: would import {len(tasks)} Supabase task(s) "
            f"for {config['member_id']}"
        )
        return
    workbench["shared_tasks"] = tasks
    workbench["collaboration"] = {
        "enabled": True,
        "member_id": config["member_id"],
        "center_status": "connected",
        "last_sync_at": datetime.now(timezone.utc).isoformat(),
        "outbound_status_mode": "confirm_each",
        "backend": "supabase",
    }
    workbench_path.write_text(
        json.dumps(workbench, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Imported {len(tasks)} Supabase task(s) for {config['member_id']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--workbench", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = read_config(args.config)
    tasks = fetch_tasks(config)
    import_tasks(config, args.workbench, tasks, args.dry_run)


if __name__ == "__main__":
    main()
