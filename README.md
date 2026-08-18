# Personal AI Command Center Template

A private, reusable personal workbench that turns natural-language check-ins into structured projects, daily priorities, follow-ups, and a Canvas-style dashboard. It can also deploy with a private GitHub shared fact center so assignments from another member appear directly in the Team view.

This repository contains no personal data. Each deployment creates a separate local workspace for its owner.

## Quick start

To preview the complete Canvas-style interface after downloading the repository, open [`demo/personal-command-center.html`](demo/personal-command-center.html). It contains neutral example data only.

Give your AI coding assistant this repository and paste the contents of [`DEPLOY_PROMPT.md`](DEPLOY_PROMPT.md). The assistant will:

1. Ask a short onboarding questionnaire.
2. Create a private workspace with a snapshot, append-only ledger, and structured data.
3. Generate a Canvas-style dashboard.
4. Configure a daily review protocol and optional reminders supported by the device.
5. In team mode, connect a private GitHub shared center and import only coordination-safe assignments for the deployed member.

The repository does not carry an active recurring task. Read [`AUTOMATION_SETUP.md`](AUTOMATION_SETUP.md) to create and verify instance-specific scheduling, notifications, and reminder/calendar integrations.

For Codex, install or invoke the skill in [`skills/build-personal-command-center`](skills/build-personal-command-center/SKILL.md).

Do not open `assets/dashboard-template.html` directly. It contains the `__WORKBENCH_DATA__` build marker and must be rendered with a user's structured data. The ready-to-open file in `demo/` shows the same interface using safe example data.

## Design principles

- One source of truth: structured project data and an append-only ledger.
- Simple foreground, complete background: the home page shows at most one core result and two important pushes.
- Evidence-based status: green means verified progress, yellow means bounded waiting, and red means intervention is required.
- Independent ownership: template updates never overwrite a user's private workspace.
- Separated collaboration: the dashboard is the operating interface; a separate private GitHub repository is the shared fact and audit layer.
- Company-data isolation: shared tasks contain coordination metadata only and never files, internal links, messages, customer details, code, or company-account context.
- No silent sync claims: reminders and calendars are only reported as synchronized after a real dry run and write succeeds.
- Portable rules, private execution: automation schedules, platform bindings, device permissions, and credentials remain outside the template.

## Privacy

Never commit a deployed user's `workspace/`, `config/shared-center.json`, shared-center checkout, personal links, contacts, credentials, calendar identifiers, health data, or private project history. Keep the template and each user's data separate.

## Runtime dependencies

The bundled renderer uses only Python's standard library. No `pip install` is required to render the example or a deployed workbench. Optional formatter and linter dependencies are listed in `requirements-dev.txt` for contributors only.

## License

No open-source license is currently granted. Keep the repository private or obtain an explicit licensing decision from the owner before public distribution or commercial reuse.
