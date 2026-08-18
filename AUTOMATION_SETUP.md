# Automation setup

This repository defines the daily operating protocol, data formats, and dashboard templates. It does **not** contain an active scheduler, a deployed notification channel, device permissions, or a user's reminder/calendar credentials.

Recurring automation is instance-specific. Every new owner must create and verify it on the platform where their workbench runs.

## What is and is not included

Included in the repository:

- the morning and evening review protocol;
- red/yellow/green status rules;
- the one-core-result, two-important-pushes, 30%-buffer planning rule;
- the reminder/calendar interchange example in `sync-plan.example.json`;
- guardrails for evidence, privacy, and verified synchronization.

Not included:

- an active recurring task or wake-up schedule;
- a connection to a Codex task, Coze/Doubao agent, or other platform account;
- Apple Reminders, calendar, Feishu, email, SMS, or push-notification permissions;
- personal projects, contacts, calendar identifiers, device paths, or credentials;
- a guarantee that the selected delivery channel supports proactive messages.

## Required setup decisions

Before creating an automation, obtain explicit approval for:

1. owner and timezone;
2. check-in time and recurrence;
3. destination task/agent and notification channel;
4. whether the automation may update the ledger automatically;
5. whether reminders or calendar events may be written externally.

Do not create external writes merely because the template mentions reminders.

## Generic daily automation contract

Configure the platform scheduler to invoke the deployed workbench with instructions equivalent to:

```text
Run the daily project check-in for this owner.

Read the deployed instance's current structured state, not the example data in the template repository. Show yesterday's status colors and near-term hard dates. Ask red projects first; ask yellow projects only when their check date arrives or a dependency changes; ask green projects only for verified results and the next checkpoint.

After the owner replies, update the structured project data, append-only ledger, current snapshot, and dashboard together. Generate at most one core result and two important pushes, preserving approximately 30% buffer. Record every waiting item with: waiting for whom, waiting for what, next check, and default action if no reply.

Never invent progress. Never claim that a reminder, calendar event, notification, or data update succeeded without tool evidence.
```

The scheduler should prompt for updates first. It should not invent a final plan before the owner has replied, unless the platform is explicitly configured to create a provisional plan labeled with its assumptions.

## Codex deployment

1. Deploy the template into a private workspace.
2. Confirm the Codex task that owns the workbench and the absolute paths of its state files.
3. Create a recurring automation in the Codex app for the approved local time and timezone.
4. Point the automation at the deployed instance, never at the example files in this template.
5. If Apple Reminders or Calendar synchronization is requested, keep the synchronization script and device authorization in the private workspace. Do not commit them with personal identifiers or credentials.
6. Dry-run supported integrations, perform the real write only after approval, and report actual created/updated counts.

An active Codex automation is stored and managed by the Codex application, outside this Git repository. Copying or forking the repository does not copy the automation.

## Coze/Doubao deployment

Treat the repository as a specification, not as executable Coze configuration. Recreate the protocol using Coze workflows, persistent storage, and the selected publication channel.

Start with a capability proof before building the full product:

1. create and update one project through natural language;
2. close and reopen the conversation and verify persistence;
3. test two accounts and prove that neither can read or modify the other's records;
4. publish to the intended Doubao channel and repeat the database test there;
5. test whether the channel can deliver a proactive scheduled message;
6. test dashboard cards and links on the target phone;
7. document any platform limitation and its fallback.

Every database read, update, and delete must be scoped to the authenticated user identifier. Merely adding a `user_id` field is not sufficient isolation.

If the Doubao channel cannot display arbitrary HTML, host the dashboard separately and return a secure per-user link. If proactive notifications are unsupported, use a confirmed supported channel or require the user to initiate the daily check-in. Do not describe either capability as complete until the end-to-end test passes.

## Reminder and calendar policy

- Only confirmed meetings, travel, construction, or appointments become calendar events.
- Tentative arrangements become reminders to confirm, not events.
- Stable items use stable IDs so rescheduling updates rather than duplicates them.
- Completion updates the existing reminder instead of creating a replacement.
- Personal device permissions, tokens, and calendar identifiers remain outside the template repository.

## Acceptance checklist

Automation is considered active only when all applicable checks pass:

- [ ] The approved schedule and timezone are visible in the platform scheduler.
- [ ] A real scheduled run wakes the intended task or agent.
- [ ] The run reads the deployed owner's current data, not template examples.
- [ ] A reply produces verified updates to structured state and the ledger.
- [ ] Red/yellow/green logic and the 1+2+30% planning rule are preserved.
- [ ] A test notification reaches the approved destination.
- [ ] External reminder/calendar writes pass a dry run and a real-write test.
- [ ] Two-user isolation is verified when the deployment is multi-user.
- [ ] Failures are reported honestly and leave a recoverable plan or payload.

Record the platform, schedule, destination, last successful test time, and known limitations in the deployed owner's private workspace. Do not write these instance details back into this template.
