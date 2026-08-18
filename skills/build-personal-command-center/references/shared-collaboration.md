# Private GitHub shared-center deployment

## Deployment modes

- `personal_only`: independent personal workbench without team assignments.
- `personal_plus_shared`: personal workbench plus a private GitHub shared fact center. Use this mode when a manager must assign tasks that appear in another member's workbench.

## Required components for `personal_plus_shared`

1. A private shared-center GitHub repository created from `assets/shared-center-template/`.
2. GitHub collaborator access for every member.
3. A local private checkout of that repository.
4. `config/shared-center.json`, created from `assets/shared-center-config.example.json` and excluded from Git.
5. `scripts/import_shared_tasks.py` copied into the deployed personal workspace.
6. `shared_tasks` and `collaboration` in `data/workbench.json`.
7. The dashboard's Team view, rendered after every successful import.

## Install sequence

1. Verify Python 3, Git, GitHub authentication, and access to the private shared-center repository.
2. If no shared-center repository exists, create one only after the user approves the repository owner/name and private visibility. Copy `assets/shared-center-template/` into it and validate before the first push.
3. Clone the shared center into a private local directory outside the personal template repository.
4. Create the private config with the member ID, checkout path, remote URL, and `outbound_status_mode: confirm_each`.
5. Run the importer with `--dry-run`, then run it without `--dry-run`.
6. Render the workbench and verify the Team navigation, assignment list, and task detail page.

## Read path

Fetch the private shared center, validate all envelopes, filter tasks by `assignee_id`, import only matching tasks, and render. Reject the entire import if validation fails.

## Write path

Never write outbound status automatically. Show the user the complete proposed envelope, obtain explicit confirmation, update only safe coordination fields on a branch, validate, show the diff, and open a pull request.

## Privacy boundary

Never copy company files, screenshots, source code, document contents, email/chat text, customer details, internal URLs, local/network paths, credentials, or company GPT context. Employer policy takes precedence. If minimal task metadata cannot leave the company account, use neutral codes or disable outbound synchronization.
