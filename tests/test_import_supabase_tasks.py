from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "build-personal-command-center"
    / "scripts"
    / "import_supabase_tasks.py"
)
SPEC = importlib.util.spec_from_file_location("import_supabase_tasks", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def task(**updates):
    value = {
        "schema_version": 1,
        "id": "task-backend-proof",
        "title": "确认后端验证结果",
        "assigner_id": "ryan",
        "assignee_id": "jiang-shengxiong",
        "project_id": "none",
        "safe_context": "仅使用中性测试数据验证任务同步。",
        "priority": "medium",
        "status": "assigned",
        "health": "yellow",
        "status_reason": "等待负责人确认接收。",
        "due": "2026-08-21T10:00:00Z",
        "next_action": "确认测试任务并反馈状态。",
        "blocker": "none",
        "done_criteria": "双方均看到相同的脱敏任务状态。",
        "check_date": "2026-08-20",
        "source_reference": "BACKEND-PROOF-001",
        "safe_evidence": "none",
        "confidentiality": "coordination_only",
        "revision": 1,
        "updated_at": "2026-08-19T12:00:00Z",
        "updated_by": "ryan",
    }
    value.update(updates)
    return value


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _size=-1):
        return json.dumps(self.payload, ensure_ascii=False).encode("utf-8")


class SupabaseImporterTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "enabled": True,
            "provider": "supabase",
            "member_id": "jiang-shengxiong",
            "supabase_url": "https://project.supabase.co",
            "publishable_key_env": "TEST_SUPABASE_KEY",
            "access_token_env": "TEST_SUPABASE_TOKEN",
            "outbound_status_mode": "confirm_each",
        }

    def test_valid_task_is_fetched_and_filtered_by_member(self):
        environment = {"TEST_SUPABASE_KEY": "key", "TEST_SUPABASE_TOKEN": "token"}
        with patch.dict(os.environ, environment), patch.object(
            MODULE.urllib.request,
            "urlopen",
            return_value=FakeResponse([task()]),
        ) as mocked:
            result = MODULE.fetch_tasks(self.config)
        self.assertEqual([item["id"] for item in result], ["task-backend-proof"])
        requested_url = mocked.call_args.args[0].full_url
        self.assertIn("assignee_id=eq.jiang-shengxiong", requested_url)

    def test_company_path_is_rejected_before_import(self):
        with self.assertRaisesRegex(ValueError, "Windows path"):
            MODULE.validate_task(
                task(safe_context=r"Open C:\\Company\\private.xlsx"),
                "jiang-shengxiong",
            )

    def test_import_updates_only_shared_collaboration_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "workbench.json"
            original = {
                "profile": {"name": "Private owner"},
                "today": {"important_pushes": [], "buffer_percent": 30},
                "projects": [{"id": "private-project"}],
                "upcoming": [],
                "updated_at": "2026-08-19T00:00:00Z",
            }
            path.write_text(json.dumps(original), encoding="utf-8")
            MODULE.import_tasks(self.config, path, [task()], dry_run=False)
            updated = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(updated["projects"], original["projects"])
        self.assertEqual(updated["shared_tasks"][0]["assignee_id"], "jiang-shengxiong")
        self.assertEqual(updated["collaboration"]["backend"], "supabase")


if __name__ == "__main__":
    unittest.main()
