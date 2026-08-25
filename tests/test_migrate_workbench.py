import importlib.util
from datetime import date
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "backend" / "migrate_markdown_workbench.py"
SPEC = importlib.util.spec_from_file_location("migrate_workbench", MODULE_PATH)
migration = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(migration)


class MigrationDisplayTests(unittest.TestCase):
    def test_known_hard_nodes_use_short_titles(self):
        line = "- 2026-08-20 08:30：到达铜川新区参加充电桩会面；会后复盘。"
        self.assertEqual(migration.concise_event_title(line), "铜川｜充电桩会面")

    def test_unknown_hard_nodes_are_bounded(self):
        line = "- 2026-08-25：这是一个非常非常长而且包含许多细节的未来事项，需要稍后处理。"
        self.assertLessEqual(len(migration.concise_event_title(line)), 24)

    def test_team_node_wins_over_other_project_mentions(self):
        line = "- 团队共享台账不挤占铜川节点；2026-08-23 检查准备度。"
        self.assertEqual(migration.concise_event_title(line), "团队工作台｜准备度检查")

    def test_upcoming_nodes_drop_past_and_duplicates(self):
        markdown = """## 已知硬节点与等待

- 2026-08-18：LA 已完成；2026-08-25 提交架构。
- 自 2026-08-25 起：LA 固定周会。
- 2026-08-17：过去事项。
- 2026-08-20 08:30：铜川会面。
"""
        events = migration.upcoming_events(markdown, today=date(2026, 8, 19))
        self.assertEqual([event["title"] for event in events], ["LA｜架构方案与周会", "铜川｜充电桩会面"])
        self.assertEqual(events[0]["date"], "2026-08-25")


if __name__ == "__main__":
    unittest.main()
