# Supabase two-person Demo decision record

Status: approved architecture constraint, 2026-08-19.

## Decision

- Use Supabase Cloud Free as the shared data and communication center for the
  Ryan / Jiang Shengxiong Demo.
- Do not self-host a server, buy Pro or Team, or design multi-cloud and migration
  paths during this Demo.
- Use the Free project only for neutral, non-sensitive two-person test data.
- Keep complete personal ledgers, life data, AI conversations, and company data
  in each person's local environment.
- Keep the existing private GitHub channel working until real two-account
  authorization, isolation, read/accept/update/complete, and audit acceptance
  have all passed against Supabase.
- Accept that a Free project may pause after inactivity. Reassess Pro only before
  production use.

## Credential boundary

- Never place `service_role`, API keys, access or refresh tokens, or other secrets
  in browser code, this repository, generated dashboards, ordinary configuration
  files, examples, screenshots, or test logs.
- Browser clients must never receive `service_role`.
- When execution is approved, keep required runtime values in process environment
  variables or an operating-system credential store. Commit only variable names
  and placeholders.

## Approval gate for external actions

Before creating a real Supabase project, entering credentials, making an external
write, or incurring any cost, present Ryan with:

1. The exact proposed steps and external resources affected.
2. The data and credential boundary for every step.
3. The main security, privacy, availability, and cost risks.
4. The rollback path, including continued GitHub operation.
5. The observable acceptance checks and evidence to retain.

Do not execute those actions until Ryan explicitly confirms the proposal.

## Exit condition for the GitHub fallback

Keeping GitHub is mandatory until every check in `acceptance.md` passes with two
real Supabase Auth accounts and neutral data. Removing GitHub requires a separate
explicit product decision; passing the checklist alone does not authorize its
removal.
