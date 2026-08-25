from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "backend" / "supabase" / "migrations" / "202608190001_shared_fact_center.sql"


class SupabaseMigrationSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = MIGRATION.read_text(encoding="utf-8")

    def test_all_shared_tables_enable_rls(self):
        for table in (
            "organizations",
            "organization_members",
            "tasks",
            "task_receipts",
            "task_events",
        ):
            self.assertIn(f"alter table public.{table} enable row level security;", self.sql)

    def test_outbound_receipt_and_status_rpc_require_confirmation(self):
        self.assertGreaterEqual(self.sql.count("if p_confirm is not true then"), 2)
        self.assertIn("task revision changed; review the full envelope again", self.sql)

    def test_direct_task_updates_are_not_granted(self):
        self.assertIn("revoke update, delete on public.tasks from authenticated;", self.sql)
        self.assertNotIn("grant update on public.tasks to authenticated", self.sql)


if __name__ == "__main__":
    unittest.main()
