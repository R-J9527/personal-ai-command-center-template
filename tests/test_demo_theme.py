from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DEMO = (ROOT / "demo" / "personal-command-center.html").read_text(encoding="utf-8")
TEMPLATE = (
    ROOT
    / "skills"
    / "build-personal-command-center"
    / "assets"
    / "dashboard-template.html"
).read_text(encoding="utf-8")


class DemoThemeTests(unittest.TestCase):
    def test_demo_uses_official_usc_primary_colors(self):
        self.assertIn("--canvas-nav: light-dark(#990000, #660000);", DEMO)
        self.assertIn("--canvas-brand: #ffcc00;", DEMO)
        self.assertIn("USC · 后端测试版", DEMO)

    def test_daily_template_keeps_original_palette(self):
        self.assertIn("--canvas-nav: light-dark(#102b4e, #08172a);", TEMPLATE)
        self.assertIn("--canvas-brand: light-dark(#f5c242, #ffd166);", TEMPLATE)
        self.assertNotIn("USC · 后端测试版", TEMPLATE)

    def test_status_colors_remain_semantically_distinct(self):
        for color in ("--canvas-status-green", "--canvas-status-yellow", "--canvas-status-red"):
            self.assertIn(color, DEMO)

    def test_dark_mode_selected_navigation_has_high_contrast(self):
        self.assertIn(
            'background: light-dark(var(--canvas-surface), var(--canvas-brand))',
            DEMO,
        )
        self.assertIn('color: light-dark(var(--canvas-nav), var(--canvas-on-brand))', DEMO)

    def test_settings_offer_five_persistent_ui_palettes(self):
        for theme in ('usc', 'ucsd', 'sau', 'nyu', 'columbia'):
            self.assertIn(f'data-ui-theme-option="{theme}"', DEMO)
            self.assertIn(f'data-ui-theme="{theme}"', DEMO)
        for official_color in ('#990000', '#ffcc00', '#182b49', '#ffcd00', '#57068c', '#1d4f91', '#b9d9eb'):
            self.assertIn(official_color, DEMO.lower())
        self.assertIn('沈航蓝 · 数字适配', DEMO)
        self.assertIn("const themeStorageKey = 'team-ai-workbench-ui-theme';", DEMO)
        self.assertIn('window.localStorage.setItem(themeStorageKey, safeThemeKey)', DEMO)
        self.assertIn('不会上传或影响日常正式工作台', DEMO)

    def test_each_palette_adapts_page_and_card_backgrounds(self):
        expected_dark_backgrounds = {
            'usc': ('#17120f', '#241b18'),
            'ucsd': ('#0f1720', '#172331'),
            'sau': ('#0c1720', '#142631'),
            'nyu': ('#150f1a', '#211728'),
            'columbia': ('#101820', '#19242d'),
        }
        for theme, (page, surface) in expected_dark_backgrounds.items():
            selector = f'#canvas-lms-project-center[data-ui-theme="{theme}"]'
            start = DEMO.index(selector)
            end = DEMO.index('\n}', start)
            theme_css = DEMO[start:end]
            self.assertIn(page, theme_css)
            self.assertIn(surface, theme_css)

    def test_demo_has_one_unified_ai_panel(self):
        self.assertEqual(DEMO.count('id="clms-ai-panel"'), 1)
        for element_id in (
            'clms-ai-context-select',
            'clms-ai-switch-notice',
            'clms-ai-messages',
            'clms-ai-form',
        ):
            self.assertIn(f'id="{element_id}"', DEMO)
        self.assertIn('id="clms-ai-panel" aria-label="AI 对话">', DEMO)
        self.assertNotIn('id="clms-ai-open"', DEMO)
        self.assertNotIn('id="clms-ai-close"', DEMO)
        self.assertNotIn('id="clms-ai-panel"', TEMPLATE)

    def test_demo_layout_keeps_ai_sidebar_in_responsive_grid(self):
        self.assertIn('--ai-width: clamp(400px, 30vw, 460px)', DEMO)
        self.assertIn('grid-template-columns: 78px minmax(0, 1fr) var(--ai-width)', DEMO)
        self.assertIn('@media (max-width: 1199px)', DEMO)
        self.assertIn('position: fixed; right: 0; top: 0; bottom: 0', DEMO)
        self.assertIn('@media (max-width: 700px)', DEMO)
        self.assertIn('width: 100vw; height: 100dvh', DEMO)
        self.assertIn('id="clms-ai-collapse"', DEMO)
        self.assertIn('id="clms-ai-launcher"', DEMO)
        self.assertIn('height: 100vh', DEMO)

    def test_demo_contexts_and_histories_are_separated(self):
        self.assertIn("key: 'global'", DEMO)
        self.assertIn('key: `project:${project.id}`', DEMO)
        self.assertIn('key: `task:${task.id}`', DEMO)
        self.assertIn('const chatHistories = {};', DEMO)
        self.assertIn('页面已进入', DEMO)
        self.assertIn('当前对话仍在', DEMO)

    def test_demo_uses_confirmed_local_copy_write_flow(self):
        self.assertIn('修改先预览 · 确认后仅写入测试副本', DEMO)
        self.assertIn("fetch(`${aiGatewayBase}/api/chat`", DEMO)
        self.assertIn("fetch(`${aiGatewayBase}/api/ledger/preview`", DEMO)
        self.assertIn("fetch(`${aiGatewayBase}/api/ledger/confirm`", DEMO)
        self.assertIn('id="clms-ai-guide"', DEMO)
        self.assertIn('id="clms-ai-md-input"', DEMO)
        self.assertIn('id="clms-ai-md-consent"', DEMO)
        self.assertIn('id="clms-ai-facts-status"', DEMO)
        self.assertIn("include_personal_facts: context.type !== 'task'", DEMO)
        self.assertIn('ledger_context: ledgerSnapshotFor(context)', DEMO)
        self.assertIn("scope: 'team_task'", DEMO)
        self.assertIn('未勾选授权前，不会发送给当前 AI', DEMO)
        self.assertNotIn('api.openai.com', DEMO)
        self.assertNotIn('OPENAI_API_KEY', DEMO)
        self.assertNotIn('window.openai.sendFollowUpMessage', DEMO)

    def test_dashboard_removes_redundant_middle_column(self):
        self.assertNotIn('id="clms-dashboard-actions"', DEMO)
        self.assertNotIn('<h2>颜色规则</h2>', DEMO)
        self.assertNotIn('class="clms-right"', DEMO)
        self.assertNotIn('id="clms-course-todos"', DEMO)
        self.assertNotIn('id="clms-course-coming"', DEMO)
        self.assertIn('.clms-dashboard { display: block; }', DEMO)

    def test_empty_team_page_has_explicit_non_error_state(self):
        self.assertIn("'当前没有共享任务'", DEMO)
        self.assertIn('添加第一位成员', DEMO)
        self.assertIn('先创建任务草稿', DEMO)
        self.assertIn('姜圣雄 · 待连接', DEMO)
        self.assertIn("classList.toggle('is-empty-team'", DEMO)

    def test_account_settings_expose_truthful_connection_state(self):
        self.assertIn('id="clms-account-entry"', DEMO)
        self.assertIn('id="clms-settings-view"', DEMO)
        self.assertIn('Supabase 登录', DEMO)
        self.assertIn('未连接', DEMO)
        self.assertIn('仅本地 · 待连接', DEMO)

    def test_smart_dispatch_is_local_confirmed_review(self):
        for element_id in ('clms-dispatch-source', 'clms-task-title', 'clms-task-project', 'clms-task-assignee', 'clms-task-priority', 'clms-task-due', 'clms-task-next', 'clms-task-done', 'clms-task-privacy', 'clms-task-publish'):
            self.assertIn(f'id="{element_id}"', DEMO)
        self.assertIn('本地测试解析 · 不调用模型 · 不会自动发布', DEMO)
        self.assertIn('未发送、未上传', DEMO)
        self.assertIn('root.querySelector(\'#clms-task-publish\').disabled', DEMO)


if __name__ == "__main__":
    unittest.main()
