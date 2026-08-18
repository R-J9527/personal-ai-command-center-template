# Deployment prompt

Use the `build-personal-command-center` skill from this repository to deploy a new, private personal workbench for me in `personal_plus_shared` mode.

Requirements:

1. Do not copy example people, projects, dates, paths, or links into my workspace.
2. Ask the minimum onboarding questions needed to understand my work projects, life projects, fixed commitments, typical schedule, decision responsibilities, reminder preferences, and current sources of anxiety.
3. Create the workspace files specified by the skill and keep the structured project data as the daily operating source of truth.
4. Generate the dashboard from the provided template and verify that project navigation and detail views work.
5. During the same deployment, connect my private GitHub shared fact center. Ask for my stable member ID and the private repository URL, verify my GitHub access, create the private local config, dry-run and perform the first task import, rerender, and verify that the Team view works. Do not call deployment complete with only the personal workbench installed.
6. If the shared center does not exist, ask whether I am the owner authorized to create it. After approval, create a separate private repository from the bundled shared-center template; never make it public.
7. Keep company data isolated. Shared tasks may contain only neutral coordination metadata. Never upload files, company messages, customer details, internal links, source code, credentials, or company GPT context. Require my explicit confirmation before every outbound company-account status update.
8. Configure daily review behavior, but do not create recurring automations or external reminders until I explicitly approve their schedule and destination.
   Follow `AUTOMATION_SETUP.md`, and distinguish repository rules from an active platform scheduler.
9. Keep daily output simple: at most one core result, two important pushes, and approximately 30% buffer.
10. Explain what was created, where the files live, the shared-center connection status, and what I should answer at the first daily check-in.
11. If I approve automation, verify a real scheduled run and any requested notification or reminder/calendar write before reporting success.
