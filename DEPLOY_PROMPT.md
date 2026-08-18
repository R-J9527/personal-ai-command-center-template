# Deployment prompt

Use the `build-personal-command-center` skill from this repository to deploy a new, private personal workbench for me.

Requirements:

1. Do not copy example people, projects, dates, paths, or links into my workspace.
2. Ask the minimum onboarding questions needed to understand my work projects, life projects, fixed commitments, typical schedule, decision responsibilities, reminder preferences, and current sources of anxiety.
3. Create the workspace files specified by the skill and keep the structured project data as the daily operating source of truth.
4. Generate the dashboard from the provided template and verify that project navigation and detail views work.
5. Configure daily review behavior, but do not create recurring automations or external reminders until I explicitly approve their schedule and destination.
   Follow `AUTOMATION_SETUP.md`, and distinguish repository rules from an active platform scheduler.
6. Keep daily output simple: at most one core result, two important pushes, and approximately 30% buffer.
7. Explain what was created, where the files live, and what I should answer at the first daily check-in.
8. If I approve automation, verify a real scheduled run and any requested notification or reminder/calendar write before reporting success.
