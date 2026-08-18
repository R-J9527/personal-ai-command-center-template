# Shared fact-center rules

- Treat this repository as a coordination layer, never a personal or company-file repository.
- Read `CONFIDENTIALITY.md` before editing live task data.
- Store tasks only under `data/tasks/` and members only in `data/members.json`.
- Never add attachments, URLs, filesystem paths, customer details, source code, email/chat contents, credentials, or secrets.
- Show the complete diff before publishing an update.
- Require explicit confirmation before publishing status originating from a company account.
- Run `python scripts/validate_shared_center.py` before every commit.
- Use a branch and pull request; never push task changes directly to `main`.
