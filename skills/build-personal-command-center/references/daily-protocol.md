# Daily protocol

## Morning check-in

1. Read `outputs/current-state.md` and `data/workbench.json`.
2. Display yesterday's red/yellow/green state and confirmed dates within seven days.
3. Ask red projects first: latest result, next action, owner, completion time, blocker, decision, today's change, and the smallest action that removes red.
4. Ask yellow only when its check date is due, a dependency changed, or a new risk appeared.
5. Ask green only for a verified result and next checkpoint.
6. Finally ask only: fixed commitments today, new external replies, available time, energy, and the item most likely to be forgotten.

## After the reply

1. Separate completed, incomplete, inserted, waiting, and blocked items.
2. Recalculate color from evidence and explain every change.
3. Set one core result, at most two pushes, and approximately 30% buffer.
4. Produce time blocks with action, duration, owner, and completion standard.
5. Produce rolling three-day and seven-day checkpoints.
6. Mark items delegated, waiting, deferred, or intentionally not done.
7. Update JSON, snapshot, append-only ledger, and dashboard together. If one write fails, report the partial state and do not claim full completion.

## Evening close

Ask only for the day's most important result, any unfulfilled promise, new replies or blockers, and the first action for tomorrow. Do not run a full project interrogation at bedtime.

## Reminder adapters

Detect the user's platform before offering synchronization. Keep the planning JSON separate from the adapter. A successful plan file is not proof that Apple Reminders, Google Calendar, or another service was updated.
