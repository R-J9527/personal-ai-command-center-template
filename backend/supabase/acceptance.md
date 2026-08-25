# Two-user backend acceptance

The Supabase adapter is acceptable for the two-person pilot only when all checks
below pass with neutral data.

- [ ] Ryan can create a task assigned to Jiang Shengxiong.
- [ ] Jiang Shengxiong can read the assigned envelope through
      `task_envelopes`.
- [ ] A user outside the organization receives zero rows for its tasks,
      receipts, and events.
- [ ] Calling `mark_task_read` without `p_confirm = true` fails.
- [ ] Calling `update_task_status` without `p_confirm = true` fails.
- [ ] An assignee cannot update a task assigned to somebody else.
- [ ] A Windows path, network path, URL, or credential-shaped value is rejected
      by the database even if a client-side check is bypassed.
- [ ] `assigned -> accepted -> in_progress -> done` creates immutable event rows.
- [ ] The completion event includes only short, reviewed safe evidence.
- [ ] The personal workbench imports only the authenticated member's envelopes.
- [ ] No company file, attachment, internal link, customer data, token, or full
      AI conversation appears in the database or test logs.

Record the project identifier, test user IDs, test time, pass/fail result, and
screenshots or sanitized logs outside the template repository.
