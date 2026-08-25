#!/usr/bin/env python3
"""Migrate the existing Markdown command center into an ignored local Demo ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPOSITORY_ROOT / "workspace" / "real-workbench.json"

LIFE_MARKERS = (
    "装修",
    "homekit",
    "婚礼",
    "高才",
    "移居",
    "婚纱",
    "签证",
    "健康",
    "游泳",
)


def section(markdown: str, title: str) -> str:
    match = re.search(rf"^## {re.escape(title)}\s*$", markdown, re.MULTILINE)
    if not match:
        return ""
    following = markdown[match.end() :]
    next_heading = re.search(r"^## ", following, re.MULTILINE)
    return following[: next_heading.start()] if next_heading else following


def markdown_table(markdown: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        return []
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def stable_id(name: str) -> str:
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:12]
    return f"local-{digest}"


def status_value(color: str) -> str:
    normalized = color.lower()
    if "红" in normalized:
        return "red"
    if "绿" in normalized:
        return "green"
    return "yellow"


def first_date(value: str) -> str:
    match = re.search(r"20\d{2}-\d{2}-\d{2}", value)
    return match.group(0) if match else ""


def project_from_row(row: dict[str, str]) -> dict[str, Any]:
    name = row.get("项目", "未命名项目")
    state = row.get("最近证据 / 当前状态") or row.get("当前状态") or "待确认"
    next_action = row.get("下一动作与完成标准") or row.get("下一动作 / 触发条件") or "待确认下一动作"
    check = row.get("下次检查", "")
    due_date = first_date(check) or first_date(next_action)
    space = "life" if any(marker in name.lower() for marker in LIFE_MARKERS) else "work"
    blocker = state if any(marker in state for marker in ("等待", "待补", "尚未", "阻塞")) else "none"
    return {
        "id": stable_id(name),
        "space": space,
        "name": name,
        "summary": state[:220],
        "status": status_value(row.get("颜色", "黄")),
        "status_reason": state,
        "owner": row.get("负责人", "待补"),
        "next_action": next_action,
        "due": f"{due_date}T18:00:00+08:00" if due_date else "",
        "blocker": blocker,
        "decision": "待从原台账按需确认",
        "done_criteria": next_action,
        "check_date": first_date(check),
        "links": [],
    }


def concise_event_title(line: str) -> str:
    rules = (
        ("团队共享台账", "团队工作台｜准备度检查"),
        ("LA", "LA｜架构方案与周会"),
        ("铜川", "铜川｜充电桩会面"),
        ("Token", "Token｜确认测试接收"),
        ("全屋智能", "HomeKit｜完成点位设计"),
        ("沈阳", "沈阳｜确认返程航班"),
    )
    for marker, title in rules:
        if marker in line:
            return title
    cleaned = re.sub(r"^\s*-\s*", "", line)
    cleaned = re.sub(r"(?:自\s*)?20\d{2}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?(?:\s*起)?[：:]?", "", cleaned)
    cleaned = re.split(r"[；。]", cleaned, maxsplit=1)[0].strip(" ：:")
    return cleaned if len(cleaned) <= 24 else cleaned[:23] + "…"


def upcoming_events(markdown: str, today: date | None = None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    reference_date = today or datetime.now().date()
    for line in section(markdown, "已知硬节点与等待").splitlines():
        date_matches = list(re.finditer(r"(20\d{2}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}))?", line))
        future_matches = [
            match
            for match in date_matches
            if datetime.strptime(match.group(1), "%Y-%m-%d").date() >= reference_date
        ]
        if not future_matches:
            continue
        date_match = future_matches[0]
        full_text = re.sub(r"^\s*-\s*", "", line).strip()
        title = concise_event_title(line)
        key = (date_match.group(1), title)
        if key in seen:
            continue
        seen.add(key)
        events.append(
            {
                "date": date_match.group(1),
                "time": date_match.group(2) or "待定",
                "title": title,
                "details": full_text,
                "project_id": "none",
                "confirmed": "暂估" not in full_text and "未最终确认" not in full_text,
            }
        )
    return events[:12]


def migrate(state_markdown: str, source_paths: list[Path]) -> dict[str, Any]:
    rows = markdown_table(section(state_markdown, "今日优先队列"))
    rows.extend(markdown_table(section(state_markdown, "计划推进与等待")))
    projects_by_name: dict[str, dict[str, Any]] = {}
    for row in rows:
        project = project_from_row(row)
        projects_by_name[project["name"]] = project
    projects = list(projects_by_name.values())
    priority = projects[:3]
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    return {
        "profile": {
            "name": "Ryan",
            "timezone": "Asia/Shanghai",
            "check_in_time": "11:00",
            "wake_time": "10:30",
            "sleep_time": "01:00",
        },
        "today": {
            "core_result": {
                "title": priority[0]["name"] if priority else "完成今日盘点",
                "project_id": priority[0]["id"] if priority else "none",
                "due": priority[0]["due"] if priority else "",
                "duration_minutes": 90,
                "done_criteria": priority[0]["done_criteria"] if priority else "形成今日计划",
            },
            "important_pushes": [
                {
                    "title": project["next_action"],
                    "project_id": project["id"],
                    "due": project["due"],
                    "duration_minutes": 45,
                    "done_criteria": project["done_criteria"],
                }
                for project in priority[1:3]
            ],
            "buffer_percent": 30,
        },
        "projects": projects,
        "upcoming": upcoming_events(state_markdown),
        "collaboration": {
            "enabled": True,
            "member_id": "ryan",
            "center_status": "local_only",
            "last_sync_at": None,
            "outbound_status_mode": "confirm_each",
        },
        "shared_tasks": [],
        "migration": {
            "local_only": True,
            "source_files": [path.name for path in source_paths],
            "migrated_at": now,
        },
        "updated_at": now,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate Markdown workbench data locally")
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--history", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    sources = [args.state, args.ledger] + ([args.history] if args.history else [])
    for source in sources:
        if not source.is_file():
            raise SystemExit(f"Missing source: {source}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    backup = args.output.parent / f"migration-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    backup.mkdir(parents=True, exist_ok=False)
    for source in sources:
        shutil.copy2(source, backup / source.name)

    payload = migrate(args.state.read_text(encoding="utf-8"), sources)
    temporary = args.output.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({
        "output": str(args.output),
        "backup": str(backup),
        "projects": len(payload["projects"]),
        "work": sum(1 for project in payload["projects"] if project["space"] == "work"),
        "life": sum(1 for project in payload["projects"] if project["space"] == "life"),
        "shared_tasks_published": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
