# Data schema

## Workspace

`data/workbench.json` contains:

- `profile`: `name`, `timezone`, `check_in_time`, `wake_time`, `sleep_time`.
- `today`: one `core_result`, zero to two `important_pushes`, and `buffer_percent`.
- `projects`: all work and life projects, including inactive low-priority entries.
- `upcoming`: confirmed events and hard checkpoints.
- `updated_at`: ISO-8601 timestamp.

## Project

Every project requires:

- `id`: stable lowercase identifier; never reuse it for another project.
- `space`: `work` or `life`.
- `name` and `summary`.
- `status`: `red`, `yellow`, or `green`.
- `status_reason`: evidence for the current color.
- `owner`: one accountable owner; collaborators may be listed separately.
- `next_action`: a concrete verb-led action.
- `due`: ISO date/time or an explicit `TBD`.
- `blocker`: `none` or a concrete obstacle.
- `decision`: `none` or a specific pending decision.
- `done_criteria`: observable completion evidence.
- `check_date`: next date to inspect this project.
- `links`: zero or more `{title, url, kind}` objects.

## Color rules

- Green: verified progress or result exists, with a clear next checkpoint.
- Yellow: waiting is reasonable and has an owner/dependency plus a next check date.
- Red: blocked, overdue, near a hard date without a result, or missing owner, next action, due date, or external reply.
- No new evidence: keep the prior color and label it `pending confirmation`; a green project without a new result becomes yellow at its next check.

## Today

- `core_result`: `{title, project_id, due, duration_minutes, done_criteria}` or `null`.
- `important_pushes`: the same shape, maximum two items.
- Do not schedule more than 70% of the user's available time.

## Upcoming

Each entry uses `{date, time, title, project_id, confirmed}`. Only confirmed meetings, travel, construction, or appointments belong here. Unconfirmed items remain reminders to confirm, not events.
