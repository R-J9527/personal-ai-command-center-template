#!/usr/bin/env python3
"""Import validated assignments from a private shared center into a workbench."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    return value


def resolve_checkout(config_path: Path, raw_path: str) -> Path:
    checkout = Path(raw_path).expanduser()
    if not checkout.is_absolute():
        checkout = (config_path.parent / checkout).resolve()
    return checkout


def run_center_validation(center: Path) -> None:
    validator = center / "scripts" / "validate_shared_center.py"
    if not validator.is_file():
        raise ValueError(f"Shared-center validator missing: {validator}")
    spec = importlib.util.spec_from_file_location("shared_center_validator", validator)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load validator: {validator}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--workbench", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load(args.config)
    if config.get("enabled") is not True:
        raise ValueError("Shared center is disabled")
    member_id = config.get("member_id")
    if not isinstance(member_id, str) or not member_id.strip():
        raise ValueError("config.member_id must be a non-empty string")
    if config.get("outbound_status_mode") != "confirm_each":
        raise ValueError("outbound_status_mode must be confirm_each")

    center = resolve_checkout(args.config, str(config.get("checkout_path", "")))
    run_center_validation(center)
    tasks = []
    for path in sorted((center / "data" / "tasks").glob("*.json")):
        task = load(path)
        if task.get("assignee_id") == member_id:
            tasks.append(task)

    workbench = load(args.workbench)
    workbench["shared_tasks"] = tasks
    workbench["collaboration"] = {
        "enabled": True,
        "member_id": member_id,
        "center_status": "connected",
        "last_sync_at": datetime.now(timezone.utc).isoformat(),
        "outbound_status_mode": "confirm_each",
    }

    if args.dry_run:
        print(f"Dry run: would import {len(tasks)} task(s) for {member_id}")
        return
    args.workbench.write_text(json.dumps(workbench, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(tasks)} task(s) for {member_id} into {args.workbench}")


if __name__ == "__main__":
    main()
