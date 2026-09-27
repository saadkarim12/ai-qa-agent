# Test Case Writer

Paste user stories, get test cases for review and Playwright.

```bash
python3 -m tcgen
```

Needs `ANTHROPIC_API_KEY` (and `ANTHROPIC_WORKSPACE_ID` if the key isn't scoped to a workspace). Uses Claude Opus 5, chosen by measurement — see [`eval/EVAL_REPORT.md`](eval/EVAL_REPORT.md) and the project's `TCGEN_DEVELOPMENT_LOG.md`.

| File | Role |
|---|---|
| `stories.py` | Splits pasted text into user stories |
| `examples.py` | The user's examples, and the grounding text per site |
| `prompt.py` | System prompt and few-shot message layout (cached) |
| `llm.py` | Model calls, prices, errors, server-side fallback |
| `guard.py` | Deterministic checks for invented data, URLs and on-screen text |
| `markdown.py` | Writes the markdown hand-off and reads it back |
| `pipeline.py` | Stories in, checked test cases and markdown out |
| `evaluate.py` | Leave-one-out model comparison (`--rescore` is free) |
| `server.py`, `page.py` | The web page |
