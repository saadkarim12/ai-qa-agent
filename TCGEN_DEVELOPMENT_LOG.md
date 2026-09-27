# Test Case Writer — Development Log

**Date:** 27 September 2026
**What it is:** a simple page where a QA engineer pastes user stories and gets test cases back, written by an AI model, grounded in the team's own examples, and saved as a markdown file for the Playwright step.
**Code:** [`tcgen/`](tcgen/) · **Tests:** [`tests/test_tcgen.py`](tests/test_tcgen.py) · **Model evaluation:** [`tcgen/eval/EVAL_REPORT.md`](tcgen/eval/EVAL_REPORT.md)

---

## 1. Requirements (from the user)

1. A simple page: input user stories, get test cases.
2. The conversion is done by an AI model through the API.
3. Use the supplied user stories and test cases as few-shot examples; explore other cases, but **nothing hallucinated**.
4. Output is a markdown file with the BRD §12.2 columns; Playwright reads it next.
5. Evaluate chat models and use the most cost-effective one that is good enough.
6. Ask where clarity is needed.

**Decisions taken with the user:**

| Question | Answer |
|---|---|
| Model provider | Anthropic, key set on the user's machine |
| What "not hallucinated" means for test data | Only values from the story or the examples for the same site; anything else is a `<placeholder>` |
| Columns | BRD §12.2 **plus a Test Data column**, because Playwright needs the data separately |
| Who uses it | The QA team, online (hosting still to be chosen) |

## 2. Inputs

`Sample US-TC.xlsx` — 2 user stories on saucedemo.com with 13 test cases (8 login, 5 cart). It supersedes the older files in `AI QA Agent Documents/`. Copied to [`sample_data/fewshot/Sample-US-TC.xlsx`](sample_data/fewshot/Sample-US-TC.xlsx) and converted to the output format in [`tcgen/fewshot/exemplars.json`](tcgen/fewshot/exemplars.json).

The live site was opened to ground the conversion: the fields are **Username** and **Password**, the button is **Login**, the landing page is **Products**. The empty-login message matched the spreadsheet's *Actual Result* word for word, which confirmed those strings were observed by running the site, so the model must never write them from memory.

**Correction recorded, not hidden:** TC-LOGIN-008's test data reads ` OR '1'='1` in the spreadsheet. Excel treats a leading apostrophe as a text marker and hides it; the intended value is `' OR '1'='1`.

**Judgement to review:** the spreadsheet had no Steps, Risk, Priority or Evidence. These were written for the examples during conversion and should be checked by QA.

## 3. How it works

```
stories ─► split into stories ─► model (examples as prior turns) ─► checker ─► markdown
```

- **Prompt** ([`prompt.py`](tcgen/prompt.py)): the examples do most of the teaching. The system prompt draws the line between what the model may state and what must be a placeholder.
- **Structured output:** the model can only return the agreed fields. Test IDs, story reference and status are filled in by code, so the model cannot misnumber tests or claim one has passed. *Actual Result* is never generated — Playwright records it.
- **Checker** ([`guard.py`](tcgen/guard.py)) — no AI, plain text comparison. Flags any test data, URL, backticked value or quoted on-screen text that isn't in the story or the examples for the same site. Flagged cases are kept and listed under **Check before running**, so nothing is hidden from the reviewer.
- **Per-site scoping:** examples for saucedemo contribute nothing to a story for another site, so `standard_user` can't leak into another application's tests.
- **Stated vs derived:** every case says whether the story asks for it or whether it was explored beyond the story.
- **Markdown** ([`markdown.py`](tcgen/markdown.py)) — fixed conventions, and a parser that reads the file back. Every field is round-tripped in the tests: that is the guarantee Playwright can read it.

## 4. Choosing the model

**Method:** leave-one-out over the two stories — show the model one story and its test cases, ask for the other, compare with the user's reference cases. Two runs per story per model.

**Pass criteria, fixed before any run:** every answer parses · covers ≥ 75% of the reference test cases · ≤ 1 invented detail per run. Cheapest passing model wins.

**Scoring calibration:** each of the 13 reference cases must be matched by exactly one scoring rule when the user's own cases are scored. This caught two loose rules that would have credited tests that were never written, and later a rule that missed Haiku's single-product test.

### Round 1

No model passed. Reading every flag showed four kinds:

| Flagged | Example | Real invention? |
|---|---|---|
| Site facts from memory | `locked_out_user`, `problem_user`, "Sauce Labs Backpack", `/inventory.html` | **Yes** — true for saucedemo, but only known because the site is famous |
| Guessed button labels | `Add to cart`, `Remove` | **Partly** — would break Playwright if the label differed |
| Generic attack strings | `' OR '1'='1`, `<script>alert(1)</script>` | No — say nothing about the application |
| Variants of the user's data | `STANDARD_USER` for a case-sensitivity test | No — derived from `standard_user` |

The checker was also counting one invention once per test case.

**Fixes:** the checker stopped flagging generic attack strings, case/whitespace variants, keyboard keys, and same-site URLs whose path appears in the examples, and now counts distinct problems. The prompt gained: *"You may recognise the website. Don't use anything you know about it from outside this conversation."* Round-1 outputs are kept in `tcgen/eval_v1/`.

### Round 2 (final)

| Model | Coverage | Invented details / run | Cost / story | Result |
|---|---|---|---|---|
| Haiku 4.5 | 71% | 0.0 | $0.010 | ✗ misses masking, locked-out and access-control cases |
| Sonnet 5 | 74% | 0.5 | $0.031 | ✗ one point short; guessed two button labels once |
| **Opus 5** | **97%** | **0.0** | **$0.106** | **✓** |

**Chosen: Opus 5.** "Based on criticality" decided it: the cases the cheaper models dropped are the security and access-control ones, which are the most expensive to miss.

**Trade-off found:** the anti-memory instruction made Sonnet timid — its coverage fell from 94% in round 1 to 74%. Opus followed the same instruction without losing coverage. Sonnet might be recoverable with prompt work, but tuning further on two stories would be tuning to noise.

**Server-side fallback** is enabled for Opus 5: if the model declines a request, the API retries it on another model; the page reports which model actually answered.

### Real run through the page

2 stories → **23 test cases, 0 flagged, $0.17 total, 32 s.** 10,507 input tokens were served from the prompt cache, so per-story cost in use is below the evaluation figure. All 13 reference scenarios were present, plus reasonable extras (case sensitivity, script injection, product-detail add, cart cleared on logout). One case to challenge: *TC-CART-011* checks that "stock" doesn't change, which the site may not show — it is labelled *derived*, which is how a reviewer finds it.

## 5. Round 2 of changes: model choice, speed, upload

The user asked for three things after trying it: choose between models, much higher speed, and uploading stories.

### Model choice

The page offers **Opus 5, Sonnet 5 and Haiku 4.5**, each labelled with its measured coverage, cost and speed. The choice is remembered in the browser. Opus 5 stays the default.

### Speed

**Where the time went:** almost entirely the model writing output, at ~100–120 tokens/second whatever the model. Opus was slowest because it writes the most (13 cases plus its thinking, ~3,700 tokens a story).

| Lever tried | Result |
|---|---|
| Opus fast mode | **Not available** — the account has zero fast-mode allowance (research preview; Anthropic must enable it) |
| Less thinking (`effort: low`) | Evaluated: **same 97% coverage, 0 invented details, 40% faster, 40% cheaper** (`tcgen/eval_effort/`). Now the Opus setting. It writes ~10 cases a story instead of ~13; the ones dropped are extras, not the reference scenarios. |
| Every story at once | Previously the first story ran alone to write the prompt cache. Now the page warms the cache while the user is typing, and all stories run in parallel. |
| Show cases as they're written | Streaming, with a parser that pulls each finished test case out of the partial JSON. Tested one character at a time, including braces and quotes inside text. |

**Measured on the two example stories:**

| | First test case on screen | All done | Cost |
|---|---|---|---|
| Before | 32 s (spinner until the end) | 32 s | 17¢ |
| Opus 5 | **3.6 s** | 25 s | 14¢ |
| Haiku 4.5 | **2.3 s** | 9 s | 1¢ |

The deprecated `output_format` request field was replaced with `output_config.format` using the SDK's own `transform_schema`, which also lets `effort` sit in the same request.

### Upload

`.docx`, `.xlsx`, `.pdf`, `.txt`, `.md`, by button or by dropping files on the text box. The extracted text goes into the box first, so the user sees and can edit what will be sent. Workbooks that hold stories and test cases together (like the user's own) have their test-case sheets skipped, with a note saying so. Tested on the user's real files: the workbook gives 2 stories with TC1/TC2 skipped; each Word file gives its story with title and site URL.

### More checker corrections from real output

- Plain numbers (`-1`, `0`, `101`) are boundary inputs, not claims about the app.
- Keyboard keys (`Enter`) and whitespace-padded variants of example data are not inventions.
- Haiku regularly starts steps with verbs outside the fixed list ("Attempt", "Note", "Modify"). These remain flagged as **format** issues — they will matter to the Playwright step.

## 6. Running it

```bash
python3 -m tcgen
```

Opens `http://127.0.0.1:8030`. Needs `ANTHROPIC_API_KEY`, and `ANTHROPIC_WORKSPACE_ID` because this organisation key isn't scoped to a workspace.

| Setting | Purpose |
|---|---|
| `TCGEN_MODEL` | The page's default choice: `opus`, `sonnet`, `haiku` |
| `TCGEN_PASSWORD` | Required once the page is reachable by others |
| `TCGEN_DAILY_USD` | Spending cap per day, default $5 |

Re-run the evaluation: `python3 -m tcgen.evaluate` (about $1). Re-check saved runs with the current checker, free: `python3 -m tcgen.evaluate --rescore`.

## 7. Open items

| # | Item |
|---|---|
| 1 | **Hosting** for the QA team — Render, AWS, Azure, or local until QA approves. The server is host-ready (key and password from settings, spending cap, health check). |
| 2 | **Workspace-scoped key with a spend limit** — create a dedicated workspace for this tool and set a monthly limit in the Anthropic console before hosting. |
| 3 | **Bigger evaluation set** — two stories on one site is a small sample. A dozen stories across two or three applications would make the model choice much firmer, and could show whether Sonnet is enough. |
| 4 | **QA review of the converted examples** — Steps, Risk, Priority and Evidence were written during conversion. |
| 5 | **Playwright step** — reads the markdown via `tcgen.markdown.parse_markdown`. |
