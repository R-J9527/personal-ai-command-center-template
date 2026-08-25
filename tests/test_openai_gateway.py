import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "backend" / "openai_gateway.py"
SPEC = importlib.util.spec_from_file_location("openai_gateway", MODULE_PATH)
gateway = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(gateway)


class OpenAIGatewayTests(unittest.TestCase):
    def test_payload_has_no_direct_tools_and_is_not_stored(self):
        payload = gateway.build_openai_payload(
            {
                "context_label": "项目：测试",
                "messages": [{"role": "user", "content": "先问我一个问题"}],
            },
            "gpt-5.4-mini",
        )
        self.assertEqual(payload["model"], "gpt-5.4-mini")
        self.assertFalse(payload["store"])
        self.assertNotIn("tools", payload)
        self.assertIn("没有直接写入工具", payload["instructions"])
        self.assertIn("ledger-change", payload["instructions"])

    def test_markdown_is_bounded_and_marked_as_reference(self):
        payload = gateway.build_openai_payload(
            {
                "messages": [{"role": "user", "content": "整理资料"}],
                "markdown_context": "# 标题\n- 动作",
            },
            "gpt-5.4-mini",
        )
        combined = "\n".join(item["content"] for item in payload["input"])
        self.assertIn("BEGIN MARKDOWN REFERENCE", combined)
        self.assertIn("# 标题", combined)
        with self.assertRaisesRegex(ValueError, "过长"):
            gateway.build_openai_payload(
                {
                    "messages": [{"role": "user", "content": "整理资料"}],
                    "markdown_context": "x" * (gateway.MAX_MARKDOWN_CHARS + 1),
                },
                "gpt-5.4-mini",
            )

    def test_local_personal_facts_are_marked_and_never_stored(self):
        payload = gateway.build_openai_payload(
            {"messages": [{"role": "user", "content": "我偏好什么？"}]},
            "gpt-5.4-mini",
            "# 我的事实\n- 喜欢简洁回答",
        )
        combined = "\n".join(item["content"] for item in payload["input"])
        self.assertIn("BEGIN LOCAL PERSONAL FACTS", combined)
        self.assertIn("喜欢简洁回答", combined)
        self.assertFalse(payload["store"])

    def test_team_task_context_excludes_personal_facts(self):
        self.assertFalse(
            gateway.should_include_personal_facts(
                {"context_key": "task:team-demo", "include_personal_facts": True}
            )
        )
        self.assertTrue(
            gateway.should_include_personal_facts(
                {"context_key": "project:personal-demo", "include_personal_facts": True}
            )
        )
        self.assertFalse(
            gateway.should_include_personal_facts(
                {"context_key": "global", "include_personal_facts": False}
            )
        )

    def test_discovers_inbox_and_newest_known_ledgers(self):
        original_directory = gateway.PERSONAL_FACTS_DIRECTORY
        original_path = gateway.PERSONAL_FACTS_PATH
        original_root = gateway.PERSONAL_FACTS_SEARCH_ROOT
        try:
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                inbox = root / "AI资料箱"
                inbox.mkdir()
                (inbox / "GPT_FACTS.md").write_text("# 偏好\n- 简洁", encoding="utf-8")
                older = root / "old"
                newer = root / "new"
                older.mkdir()
                newer.mkdir()
                (older / "每日进度台账.md").write_text("旧台账", encoding="utf-8")
                newest = newer / "每日进度台账.md"
                newest.write_text("最新台账", encoding="utf-8")
                newest.touch()
                (newer / "当前状态快照.md").write_text("当前重点", encoding="utf-8")
                gateway.PERSONAL_FACTS_DIRECTORY = inbox
                gateway.PERSONAL_FACTS_PATH = inbox / "GPT_FACTS.md"
                gateway.PERSONAL_FACTS_SEARCH_ROOT = root

                files = gateway.discover_personal_fact_files()
                combined = gateway.load_all_personal_facts()
                self.assertEqual(len(files), 3)
                self.assertIn("GPT_FACTS.md", combined)
                self.assertIn("最新台账", combined)
                self.assertNotIn("旧台账", combined)
                self.assertIn("当前重点", combined)
        finally:
            gateway.PERSONAL_FACTS_DIRECTORY = original_directory
            gateway.PERSONAL_FACTS_PATH = original_path
            gateway.PERSONAL_FACTS_SEARCH_ROOT = original_root

    def test_auto_personal_context_is_relevant_and_bounded(self):
        original_directory = gateway.PERSONAL_FACTS_DIRECTORY
        original_path = gateway.PERSONAL_FACTS_PATH
        original_root = gateway.PERSONAL_FACTS_SEARCH_ROOT
        try:
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                inbox = root / "AI资料箱"
                inbox.mkdir()
                (inbox / "GPT_FACTS.md").write_text(
                    "# 偏好\n- 我喜欢简洁回答\n" + "背景资料" * 4000,
                    encoding="utf-8",
                )
                (root / "每日进度台账.md").write_text(
                    "历史记录" * 4000 + "\n今天需要安排家庭活动",
                    encoding="utf-8",
                )
                gateway.PERSONAL_FACTS_DIRECTORY = inbox
                gateway.PERSONAL_FACTS_PATH = inbox / "GPT_FACTS.md"
                gateway.PERSONAL_FACTS_SEARCH_ROOT = root
                selected = gateway.select_personal_facts(
                    {"messages": [{"role": "user", "content": "帮我安排今天的家庭活动"}]}
                )
                self.assertLessEqual(len(selected), gateway.MAX_AUTO_FACT_CHARS)
                self.assertIn("今天需要安排家庭活动", selected)
        finally:
            gateway.PERSONAL_FACTS_DIRECTORY = original_directory
            gateway.PERSONAL_FACTS_PATH = original_path
            gateway.PERSONAL_FACTS_SEARCH_ROOT = original_root

    def test_output_text_is_extracted_from_rest_response(self):
        response = {
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "一个问题"}],
                }
            ]
        }
        self.assertEqual(gateway._extract_output_text(response), "一个问题")

    def test_deepseek_payload_has_confirmed_write_instructions_and_non_thinking(self):
        payload = gateway.build_deepseek_payload(
            {
                "context_label": "全局台账",
                "messages": [{"role": "user", "content": "安排今天"}],
            },
            "deepseek-v4-flash",
            "# 当前重点\n- 完成测试",
        )
        self.assertEqual(payload["model"], "deepseek-v4-flash")
        self.assertEqual(payload["thinking"], {"type": "disabled"})
        self.assertEqual(payload["messages"][0]["role"], "system")
        combined = "\n".join(item["content"] for item in payload["messages"])
        self.assertIn("无法绕过确认", combined)
        self.assertIn("完成测试", combined)
        self.assertNotIn("tools", payload)

    def test_deepseek_text_is_extracted(self):
        response = {"choices": [{"message": {"content": "只读测试成功"}}]}
        self.assertEqual(gateway._extract_deepseek_text(response), "只读测试成功")

    def test_ledger_snapshot_is_read_only_and_bounded(self):
        payload = gateway.build_deepseek_payload(
            {
                "context_label": "项目：测试",
                "ledger_context": {
                    "scope": "project",
                    "project": {"name": "测试项目", "status": "red"},
                },
                "messages": [{"role": "user", "content": "当前状态是什么？"}],
            },
            "deepseek-v4-flash",
        )
        combined = "\n".join(item["content"] for item in payload["messages"])
        self.assertIn("BEGIN READ-ONLY LEDGER SNAPSHOT", combined)
        self.assertIn("测试项目", combined)
        self.assertIn("不得声称已经写入", combined)
        with self.assertRaisesRegex(ValueError, "上下文过长"):
            gateway.build_openai_payload(
                {
                    "ledger_context": {"data": "x" * gateway.MAX_LEDGER_CONTEXT_CHARS},
                    "messages": [{"role": "user", "content": "测试"}],
                },
                "gpt-5.4-mini",
            )

    def test_local_ledger_is_injected_without_changing_template(self):
        original_path = gateway.LOCAL_LEDGER_PATH
        try:
            with tempfile.TemporaryDirectory() as folder:
                ledger_path = Path(folder) / "real-workbench.json"
                ledger_path.write_text(
                    json.dumps({"profile": {"name": "Ryan"}, "projects": []}, ensure_ascii=False),
                    encoding="utf-8",
                )
                gateway.LOCAL_LEDGER_PATH = ledger_path
                rendered = gateway.render_demo_html().decode("utf-8")
                self.assertIn('"name":"Ryan"', rendered)
                self.assertNotIn('"name":"示例用户"', rendered)
        finally:
            gateway.LOCAL_LEDGER_PATH = original_path

    def test_project_preview_does_not_write_until_confirmed(self):
        original_ledger_path = gateway.LOCAL_LEDGER_PATH
        original_operations_path = gateway.LEDGER_OPERATIONS_PATH
        gateway.PENDING_LEDGER_PREVIEWS.clear()
        try:
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                ledger_path = root / "real-workbench.json"
                operations_path = root / "ledger-operations.jsonl"
                ledger = {
                    "updated_at": "2026-08-19T10:00:00+08:00",
                    "projects": [
                        {
                            "id": "project-1",
                            "name": "测试项目",
                            "status": "red",
                            "next_action": "旧动作",
                        }
                    ],
                }
                ledger_path.write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
                gateway.LOCAL_LEDGER_PATH = ledger_path
                gateway.LEDGER_OPERATIONS_PATH = operations_path

                preview = gateway.create_ledger_preview(
                    {
                        "target_type": "project",
                        "target_id": "project-1",
                        "changes": {"status": "yellow", "next_action": "新动作"},
                        "reason": "测试",
                    }
                )
                unchanged = json.loads(ledger_path.read_text(encoding="utf-8"))
                self.assertEqual(unchanged["projects"][0]["status"], "red")
                self.assertTrue(preview["requires_confirmation"])

                result = gateway.confirm_ledger_preview(preview["preview_id"])
                updated = json.loads(ledger_path.read_text(encoding="utf-8"))
                self.assertTrue(result["ok"])
                self.assertEqual(updated["projects"][0]["status"], "yellow")
                self.assertEqual(updated["projects"][0]["next_action"], "新动作")
                operation = json.loads(operations_path.read_text(encoding="utf-8").strip())
                self.assertEqual(operation["target_id"], "project-1")
                self.assertEqual(operation["write_scope"], "workspace/real-workbench.json")
        finally:
            gateway.LOCAL_LEDGER_PATH = original_ledger_path
            gateway.LEDGER_OPERATIONS_PATH = original_operations_path
            gateway.PENDING_LEDGER_PREVIEWS.clear()

    def test_preview_rejects_team_and_unapproved_fields(self):
        with self.assertRaisesRegex(ValueError, "团队任务"):
            gateway.create_ledger_preview(
                {"target_type": "team_task", "target_id": "task-1", "changes": {"status": "done"}}
            )
        with self.assertRaisesRegex(ValueError, "不允许修改字段"):
            gateway._validated_project_changes({"shared_tasks": "覆盖"})

    def test_project_context_cannot_target_another_project(self):
        with self.assertRaisesRegex(ValueError, "不能修改其他项目"):
            gateway.create_ledger_preview(
                {
                    "context_key": "project:project-1",
                    "target_type": "project",
                    "target_id": "project-2",
                    "changes": {"status": "green"},
                }
            )


if __name__ == "__main__":
    unittest.main()
