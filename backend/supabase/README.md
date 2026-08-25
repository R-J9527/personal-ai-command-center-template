# Supabase shared-center backend

This directory is the first migration slice from the GitHub JSON shared center to
an API-backed shared fact center. It intentionally keeps the existing GitHub
adapter available.

The approved scope and execution gates for the two-person Cloud Free Demo are in
[`decision-record.md`](decision-record.md). They are mandatory for subsequent
implementation work.

## Included

- PostgreSQL tables for organizations, members, tasks, delivery receipts, and an
  append-only task event trail.
- Row Level Security (RLS) so authenticated users can only access organizations
  they belong to.
- A server-side coordination-only text gate for obvious URLs, filesystem paths,
  network paths, and credential patterns.
- Explicit RPC functions for read receipts and status updates. Both require an
  affirmative `p_confirm` argument.
- A security-invoker `task_envelopes` view shaped like the existing GitHub task
  contract.

## Deliberate limits

- This migration is not applied to a live Supabase project automatically.
- Supabase Cloud Free is the selected two-person Demo backend, but creating the
  real project remains blocked on Ryan's explicit approval of the steps, risks,
  credential boundary, rollback path, and acceptance evidence.
- The Free project may pause after inactivity; this is accepted for the Demo.
- The text gate cannot recognize every semantic secret, customer name, or piece
  of company context. The complete envelope must still be shown to the user and
  explicitly approved before an outbound update.
- Notifications and Windows token refresh are not part of this first slice.
- Company files and personal workspace data do not belong in these tables.

## Apply in a disposable project

1. Create a non-production Supabase project containing neutral test data only.
2. Apply `migrations/202608190001_shared_fact_center.sql` with the Supabase CLI
   or SQL editor.
3. Create two Auth users.
4. Insert one organization and two `organization_members` rows while acting as
   an administrator.
5. Insert one neutral task and verify the `task_envelopes` REST endpoint.
6. Run the isolation checks described in `acceptance.md` before connecting a
   personal workbench.

Keep project URLs and all runtime credential values in process environment
variables or the operating-system credential store. Never put `service_role`, API
keys, access or refresh tokens in frontend code, this repository, ordinary
configuration files, screenshots, or logs. Browser clients must never receive
`service_role`.
