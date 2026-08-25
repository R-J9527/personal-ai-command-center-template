# Local isolated AI gateway

The Demo AI sidebar can use the OpenAI Responses API through
`backend/openai_gateway.py`. The gateway is intentionally local and exposes no
ledger, filesystem, Supabase, or GitHub write tools.

The same local gateway can run an isolated DeepSeek trial. It keeps original
Markdown and shared data read-only, while routing inference to
DeepSeek Chat Completions. The browser receives neither provider's API key.

## Safety boundary

- The browser never receives `OPENAI_API_KEY`.
- The key is read from the process environment only.
- Responses are requested with `store: false`.
- Conversation history remains in page memory and resets on reload.
- On first start, the gateway creates the git-ignored local file
  `AI资料箱/GPT_FACTS.md`. Global and personal-project conversations include it
  automatically; team-task conversations always exclude it.
- The gateway also finds the newest `每日进度台账.md` and `当前状态快照.md`
  beneath `~/Documents/Codex` (or `WORKBENCH_MARKDOWN_ROOT`) and combines them as
  local personal context. Arbitrary repository documentation is not included.
- Full local files stay on disk. Each request selects at most 6,000 characters
  of relevant and recent snippets, reducing rate-limit risk and API cost.
- Each page sends a bounded ledger snapshot for its active scope.
  Global chat sees the compact global snapshot, project chat sees only that
  project, and team-task chat receives only the task's coordination-safe fields.
  The model receives no direct write tool. A separate preview and confirmation
  flow can update only `workspace/real-workbench.json`; original Markdown and
  team/shared data remain read-only. Confirmed changes are appended to
  `workspace/ledger-operations.jsonl`.
- A selected Markdown file is read and rendered locally first. Its contents are
  included in an API request only after the user checks the per-conversation
  consent box.
- The gateway binds to `127.0.0.1` by default and rejects non-local bind targets.
- The AI cannot claim a modification before the local confirmation endpoint
  returns success.

## Run locally

Do not put the key in this repository or a config file. In a terminal session,
provide the environment variable and start the gateway:

```sh
export OPENAI_API_KEY="replace-with-a-key-from-your-secure-store"
python3 backend/openai_gateway.py
```

Then open `http://127.0.0.1:8765/`. The default model is `gpt-5.4-mini`. To use a
different approved model for one process, set `OPENAI_MODEL` in that same terminal
session before starting the gateway.

For the reversible DeepSeek trial, run `START_DEEPSEEK_DEMO.command`. It prompts
for `DEEPSEEK_API_KEY` without echoing or persisting it, selects
`deepseek-v4-flash` in non-thinking mode, and keeps ledger writes disabled.

Creating an API key, entering it, or making the first paid API request is an
external action. Review the exact steps, data sent, expected cost, and acceptance
checks with Ryan before performing those actions.

## Acceptance

1. With no key, the UI shows `GPT 未配置` and no fake answer is generated.
2. With a valid key, the UI shows the active model and returns a guided question.
3. Asking GPT to change the ledger produces only a draft and no local data change.
4. Selecting a Markdown file shows a local formatted preview before consent.
5. Without consent, the Markdown contents are absent from `/api/chat`.
6. With consent, GPT can summarize the Markdown while preserving its facts.
7. Reloading the page clears conversation history and Markdown selection.
8. `GPT_FACTS.md` is included automatically in personal conversations and is
   absent from team-task requests.
9. The `AI资料箱` directory remains local and cannot be committed accidentally.
10. The newest known daily ledger and state snapshot are discovered without a
    manual file picker, while duplicate older copies are not sent.
