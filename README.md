# AI QA Agent

## Start here: Test Case Writer

Paste or upload user stories, get test cases written by AI, download them as markdown for Playwright.

**1. Install (once)**

```bash
pip install -r requirements.txt
```

**2. Set your API key (once)** — ask your admin for a key from the team's Anthropic workspace. Never commit it.

macOS / Linux:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Windows (PowerShell):

```powershell
setx ANTHROPIC_API_KEY "sk-ant-..."
```

If the key isn't tied to a workspace, also set `ANTHROPIC_WORKSPACE_ID` the same way (ask your admin for the `wrkspc_...` value). After `setx`, open a new terminal.

**3. Run**

```bash
python -m tcgen
```

It opens **http://127.0.0.1:8030**. Keep the terminal open while you use it.

> ⚠️ `python -m layer1.web` (port 8010, "AI QA Agent — offline mode") is the **older rules-only prototype**. It doesn't use AI, and a story without acceptance criteria comes back as "not yet testable". Use `python -m tcgen` for user stories → test cases.

More: [`tcgen/README.md`](tcgen/README.md) · how the model was chosen: [`tcgen/eval/EVAL_REPORT.md`](tcgen/eval/EVAL_REPORT.md) · full history: [`TCGEN_DEVELOPMENT_LOG.md`](TCGEN_DEVELOPMENT_LOG.md)

## Other parts of this repo

| Folder | What it is |
|---|---|
| `tcgen/` | **Test Case Writer** (current tool) |
| `layer1/`, `layer2/`, `layer3/` | Earlier rules-only prototype of the nine-layer design (no AI) |
| `demo_app/` | A small bank app for the prototype's crawler |
| `ai-qa-agent/` | First prototype, superseded |
