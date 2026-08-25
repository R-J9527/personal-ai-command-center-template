# Private GitHub shared-center deployment

## Deployment modes

- `personal_only`: independent personal workbench without team assignments.
- `personal_plus_shared`: personal workbench plus a private GitHub shared fact center. Use this mode when a manager must assign tasks that appear in another member's workbench.

## Backend providers

- `github_checkout`: current demo provider. It reads validated JSON envelopes
  from a private local GitHub checkout.
- `supabase`: staged API provider. It reads the same envelope shape from the
  RLS-protected `task_envelopes` view. Use only after the two-user isolation
  acceptance in `backend/supabase/acceptance.md` passes.

For the current two-person Demo, Supabase Cloud Free is the selected destination.
The binding scope, credential rules, external-action approval gate, and GitHub
fallback condition are recorded in `backend/supabase/decision-record.md`.

Do not silently switch a deployed owner between providers. Keep GitHub available
as the rollback path until the Supabase read, receipt, status update, and audit
tests all pass.

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

For the staged Supabase provider, keep the project URL and environment-variable
names only in private config, keep all credential values in process environment
variables or the operating-system credential store, query through the
authenticated user's token, validate the returned envelopes again locally, and
then render. Never expose `service_role` to a browser client. RLS is mandatory
and is not replaced by the client-side member filter.

## Write path

Never write outbound status automatically. Show the user the complete proposed envelope, obtain explicit confirmation, update only safe coordination fields on a branch, validate, show the diff, and open a pull request.

## Privacy boundary

Never copy company files, screenshots, source code, document contents, email/chat text, customer details, internal URLs, local/network paths, credentials, or company GPT context. Employer policy takes precedence. If minimal task metadata cannot leave the company account, use neutral codes or disable outbound synchronization.
