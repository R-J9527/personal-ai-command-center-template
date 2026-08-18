---
name: build-personal-command-center
description: Deploy, initialize, update, or repair a private AI personal workbench with work/life projects, evidence-based red-yellow-green status, daily check-ins, rolling plans, a Canvas-style dashboard, and optional reminder/calendar sync. Use when a user asks to create a personal command center, copy this workbench logic, run a daily project review, update its ledger or dashboard, or package the workflow for another person's independent use.
---

# Build Personal Command Center

Create a private workspace from the bundled templates. Preserve the logic, never the example data.

## Deploy

1. Confirm the destination directory. Keep it outside this template repository unless the user explicitly wants a demo inside the repository.
2. Read [data-schema.md](references/data-schema.md) and [daily-protocol.md](references/daily-protocol.md).
3. Ask onboarding questions in short groups. Collect:
   - identity label and timezone;
   - work and life projects;
   - owner, next action, date, blocker, decision, and completion evidence for active projects;
   - fixed commitments, typical wake/sleep window, energy pattern, and reminder destination;
   - the items currently creating the most anxiety.
4. Create `outputs/current-state.md`, `outputs/daily-ledger.md`, `data/workbench.json`, and `dashboard/personal-command-center.html` from the bundled assets.
5. Replace every example value. Never carry example people, projects, dates, links, or filesystem paths into the deployed workspace.
6. Copy the bundled renderer and dashboard template into the deployed workspace, then render:

```bash
python3 scripts/render_workbench.py \
  --data data/workbench.json \
  --template assets/dashboard-template.html \
  --output dashboard/personal-command-center.html
```

7. Validate that the data parses, the renderer succeeds, the generated HTML contains no unresolved `__WORKBENCH_DATA__` marker, and project IDs are unique.

## Operate daily

Use `data/workbench.json` as the operational source and `outputs/daily-ledger.md` as the append-only history.

1. Show yesterday's colors and near-term hard dates.
2. Ask red projects first. Ask yellow only at the check date or after a dependency change. Ask green only for verified results and the next checkpoint.
3. Convert natural-language replies into structured changes without inventing facts.
4. Set at most one core result and two important pushes; preserve about 30% buffer.
5. Record every waiting item as: waiting for whom, waiting for what, next check, and default action if no reply.
6. Update JSON, snapshot, ledger, and dashboard together.
7. Treat external reminder or calendar writes as a separate explicit action. Dry-run when supported and report only verified writes.

## Guardrails

- Keep each person's data independent by default.
- Do not expose private projects when sharing the template.
- Do not use chat history as the only source of truth.
- Do not mark work complete without evidence or an explicit user confirmation.
- Do not claim synchronization, deployment, or notification success without tool evidence.
- Keep the home page simple; move complete history and low-priority projects behind project views.

## Resources

- Copy templates from `assets/` into a new user's workspace.
- Run `scripts/render_workbench.py` after every structured data change.
- Read the two references only when deploying or changing operating logic.
