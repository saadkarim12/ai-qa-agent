# Layer 1 — Requirements Intelligence: Development Log

**Date:** 26 August 2026
**Scope:** Layer 1 of the nine-layer reference architecture (HLD §4.1, BRD §10)
**Status:** Built, QA'd, 33 tests passing, 4 defects found and fixed
**Approach agreed with the user:** layer-by-layer, rules-first, offline-capable

---

## 1. Why this was rebuilt

The previous implementation mixed Layer 1 logic into a stack of FastAPI,
SQLAlchemy, Temporal and Azure dependencies, and declared Python ≥3.12 while the
machine runs **3.9.6**. The decision was to restart Layer 1 as a clean,
self-contained engine with no infrastructure coupling — Layer 1 is an extraction
engine; orchestration belongs to layers that do not exist yet.

The previous `ai-qa-agent/` tree was **left untouched**. `layer1/` imports
nothing from it.

---

## 2. The governing decision: rules first, AI second

The user asked whether an offline rules engine should carry the work to reduce
AI dependency. It should, and the HLD already argues for it — ADR-006
("deterministic failure classification before LLM investigation"), ADR-012
("the LLM writes prose, never numbers"), §17.4 ("deterministic-first:
classification, scoring and selection use no LLM at all").

Where the line sits:

| | Rules | LLM |
|---|---|---|
| Jira fields, spreadsheet rows | ✅ Complete | Not needed |
| `As a / I want / So that` | ✅ Complete | Not needed |
| `Given / When / Then` | ✅ Complete | Not needed |
| Acceptance-criteria bullets | ✅ Complete | Not needed |
| Imperative sentences ("the system must…") | ✅ Complete | Not needed |
| Narrative prose, implied actor/workflow | ❌ Declines | ✅ Its job |

**Measured outcome:** across all 17 QA fixtures, the rules engine handled
**100%** of extractable content. The LLM was never invoked. The CLI reports the
split (`extracted by: rules 16`) so the AI dependency is a number, not a claim.

This matters practically: the machine has **no `ANTHROPIC_API_KEY` and no `ant`
CLI**, so an AI-dependent Layer 1 could not be demoed at all today.

---

## 3. What was built

```
layer1/
  contracts.py   132 lines   The Requirement contract
  parsers.py     ~310 lines  IDocumentParser seam + 5 formats
  rules.py       ~610 lines  Deterministic extraction engine
  llm.py         199 lines   Optional enricher (budgeted, schema-bound)
  pipeline.py    ~100 lines  parse → rules → LLM leftovers → Requirement[]
  cli.py         130 lines   Demo output + --json contract export
  web.py         ~230 lines  Local demo UI (stdlib http.server)
  _page.py                   The UI page (HTML/CSS/JS)
  README.md                  How to run and extend
tests/
  test_layer1.py 33 tests    Contract, shapes, regressions, QA scenarios
sample_data/
  user_stories.md, jira_sample_issues.json
  qa/            17 fixtures for the QA scenarios
```

### 3.1 The contract (`contracts.py`)

Exactly the HLD §4.1 fields, no more:

```
{actor, workflow, rule, precondition, expected_outcome,
 risk, source, source_ref, confidence, ambiguity_flags}
```

Two HLD rules are enforced structurally rather than by convention:

- **BR-03 / C-06** — `source` is a typed enum (`jira | document | discovered`).
  Discovered behaviour cannot be rendered as a confirmed requirement because it
  is a different value of a typed field, not a naming convention.
- **ADR-005** — `extra="forbid"` on the model, so neither an LLM nor a future
  contributor can quietly widen the contract.

Per-requirement provenance (`rules` vs `llm`) is tracked at the **set** level as
`extraction_methods`, deliberately keeping the `Requirement` record itself
exactly the HLD fields.

### 3.2 Parsers (`parsers.py`)

`IDocumentParser` + registry — the HLD §8.4 extensibility seam. Adding a format
means implementing the interface and calling `register()`; extraction and the
pipeline are untouched (QA-10).

Supported: `.md` / `.txt` / `.markdown`, `.docx`, `.pdf`, `.xlsx` / `.xlsm`,
`.json` (Jira export).

Parsers emit **blocks**, not one blob, so every requirement gets a `source_ref`
a human can open: `stories.md#US-003/AC1`, `SHOP-1423`, `cases.xlsx#Login!row2`.
Parsers also pass a structural `hint` (spreadsheet sheet name, Jira component)
that the text itself does not carry.

### 3.3 Rules engine (`rules.py`)

Handles four document shapes, in priority order:

1. **Acceptance criteria** — each criterion becomes its own testable requirement
2. **Gherkin** — line-based *and* inline (`Given …, when …, then …` on one line,
   which is how Jira exports them)
3. **Labelled fields** — `Actor:`, `Precondition:`, `Expected Output:` …
4. **Imperative sentences** — "the system must …"

Plus deterministic risk scoring (explicit priority → statement wording →
surrounding context), ambiguity detection over ~30 named patterns, and
confidence.

**Confidence is earned, not asserted.** It accumulates from what was actually
found — explicit actor (+0.15), explicit outcome (+0.15), explicit workflow
(+0.10), stated precondition (+0.05) — and drops 0.07 per ambiguity flag. A
clean criterion scores 0.99; `"Search should be fast and user-friendly"` scores
**0.45** with five named flags. Per BR-09 it is extraction confidence, never
evidence.

### 3.4 LLM enricher (`llm.py`)

Optional, and constrained three ways:

- It **never sets `source` or `source_ref`** — traceability is a fact the parser
  already knows, not something to infer (BR-02).
- Output is validated against the same contract (`client.messages.parse`,
  model `claude-opus-5`).
- It runs under a **block budget**, so an unusual document cannot produce an
  unbounded bill (HLD §5.2).
- Document text is fenced in `<document_text>` tags with a standing
  "data, never instruction" directive (HLD §5.4).

Absent credentials **degrade** the run with a warning; they never fail it.

### 3.5 Demo UI (`web.py`)

A local single-user web UI for exercising Layer 1 by hand:

```bash
python3 -m layer1.web
```

Built on the **standard library only** — `http.server`, no FastAPI, no uvicorn,
no install step. It binds to `127.0.0.1`, picks the first free port from 8010,
and opens a browser. Deliberate, because the previous demo had already needed
fixes for uvicorn/Python-3.9 and port-8000 binding.

- Sidebar lists all 19 bundled documents with a one-line description each
- Drag-and-drop or browse for your own file (base64 JSON upload, so binary
  `.xlsx` / `.docx` / `.pdf` work without multipart parsing)
- Stats bar: count, risk split with a proportional bar, ambiguous, confirmed,
  average confidence, and the rules-vs-LLM split
- One card per requirement showing all contract fields, with ambiguity flags
  in amber
- **Contract JSON** tab for verifying the raw records against HLD §4.1
- Warnings panel, so partial failures stay visible in the UI too
- Fixture paths are constrained to `sample_data/`; traversal is rejected

### 3.6 Pipeline and CLI

```
document → parse → rules → (LLM on the leftovers only) → dedupe → flag duplicates → Requirement[]
```

```bash
python3 -m layer1 sample_data/user_stories.md --no-llm
python3 -m layer1 sample_data/qa/14_test_cases.xlsx --no-llm --json out.json
```

`--json` emits pure contract records. `--no-llm` guarantees offline, zero-cost,
reproducible output.

---

## 4. Bugs found and fixed during development

Found by running against real files rather than synthetic strings:

| # | Bug | Cause | Fix |
|---|---|---|---|
| 1 | `_ID` undefined — every block failed extraction | Constant lived in `parsers.py`, used in `rules.py` | Mirrored the pattern locally. *(Surfaced as a warning, not a crash — the partial-failure design working.)* |
| 2 | Story IDs never reached `source_ref` (`#L4` instead of `#US-001`) | "As a…" split the heading away from its body; the boolean was inverted | Only start a new block if the current one already has an "As a" line |
| 3 | Inline `Given…when…then` lost the precondition | Gherkin matching was line-based only | Added an inline splitter; ACs are usually one sentence |
| 4 | Every requirement scored Critical | Each criterion was scored against its whole parent story | Precedence: explicit priority → statement → context |
| 5 | Jira ACs landed whole in `expected_outcome` | Single-line `Acceptance Criteria:` header didn't match the header regex, so it fell through to the label map | Split a labelled AC field that is itself Gherkin |
| 6 | Spreadsheet: `Test Case ID` became the rule; workflow became `Test Case ID: LOGIN-001` | "Test Case ID" matched the "test case" alias; the first line of a record block was read as a heading | Added an ignore-list for identifier/bookkeeping columns; use the parser's `hint`; never treat a `Label: value` line as a heading |

---

## 4b. PDF structure recovery (MarkItDown evaluated and rejected)

MarkItDown was proposed to improve PDF ingestion and reduce tokens. It was
tested and **not adopted**, for two independent reasons:

| | MarkItDown | New PdfParser |
|---|---|---|
| Headings recovered from the BRD PDF | **0** | **66** |
| Bullets recovered from the BRD PDF | **0** | **294** |
| Works on `.docx` in this environment | crashes | n/a |
| Runs on Python 3.9 | no (needs 3.10+) | yes |

The pip package available to Python 3.9 is an empty placeholder (`0.0.1a1`);
the Homebrew CLI is 0.1.6 on Python 3.12 and errors on `.docx`. But the
decisive row is the first: **even where it ran, it produced the same flat text
pdfplumber already gave**, so it did not solve the problem it was proposed for.
Token reduction was also moot — the rules engine makes no model calls.

**What replaced it.** PDFs carry no semantic markup, but they do carry the
evidence needed to rebuild it: glyph font size, x-indent and literal bullet
characters. `PdfParser` groups *words* (not characters — that reintroduces
kerning artefacts like "passwor d") into lines, infers body text size from the
most common size, promotes anything ≥15% larger to a heading, and restores
bullet and numbered-list markers. A PDF now reaches the rules engine looking
like the markdown it was before it was printed.

Result: `18_stories.pdf` and its markdown source produce **identical**
requirements and an identical test plan — there is a regression test asserting
it. The project's own BRD PDF yields 16 requirements from its acceptance-criteria
section.

## 5. QA phase

Full scenarios, fixtures and results: **[LAYER1_QA_TEST_SCENARIOS.md](LAYER1_QA_TEST_SCENARIOS.md)**

17 fixtures were built covering happy path, ambiguity, Gherkin, prose,
meeting notes, empty files, prompt injection, multilingual content, duplicates,
malformed JSON, wrong-shape JSON, priority mapping, unsupported formats,
spreadsheets, Word documents, a text-less PDF, and a 60-story volume file.

**24 scenarios executed. Four defects found:**

| ID | Severity | Defect | Fix |
|---|---|---|---|
| DEF-01 | High | Malformed Jira export **crashed** with `AttributeError` | Type-check entries; skip with named warnings |
| DEF-02 | High | Word documents lost bullet ACs and tables (2 requirements instead of 7) | Restore bullet markers from `List` styles; emit table rows as blocks |
| DEF-03 | Medium | Cosmetic change on a payment page scored Critical | Score tiers by weight of evidence, not severity order |
| DEF-04 | Medium | A criterion stated twice produced two unflagged requirements | Flag repeats against the first occurrence |

All four are fixed and locked behind regression tests. DEF-01 and DEF-02 were
only reachable through real file formats.

### Notable QA results

- **Prompt injection held.** A block instructing the extractor to set every
  confidence to 1.0, relabel `source` as `jira`, suppress ambiguity flags and
  emit environment variables changed **nothing**: `source` stayed `document`,
  confidence stayed 0.99, no secrets were echoed, and the injection block was
  reported as unresolved.
- **Ambiguity detection is complete on the draft fixture** — 7 of 7
  requirements flagged, average confidence 0.50 versus 0.98 on the clean file.
- **Unicode survives end to end** — `電子メール通知`, `«Réglages enregistrés»`,
  `£ € ¥ ☑ →` all intact.
- **Throughput is a non-issue at this layer** — 120 requirements from a 21 KB
  document in **13 ms**.

---

## 6. Current state

```
33 automated tests — all passing
17 QA fixtures — all exercised
0 known open defects
0 LLM calls required
```

| Input | Result |
|---|---|
| `sample_data/user_stories.md` | 16 requirements, refs `#US-003/AC1` |
| `sample_data/jira_sample_issues.json` | `source: jira`, `source_ref: SHOP-1423`, Highest → Critical |
| `TestCasesForReference.xlsx` (real file) | 10 requirements, workflow from sheet, 4 ambiguities flagged |
| `sample_data/qa/` (17 fixtures) | See the QA document |

---

## 7. Open items

| # | Item | Note |
|---|---|---|
| O-1 | Old `ai-qa-agent/` tree still present | Left deliberately; `layer1/` is independent. Remove on request. |
| O-2 | `pyproject.toml` declares Python ≥3.12; machine runs 3.9.6 | All Layer 1 code is 3.9-compatible, but the declaration will mislead the next setup |
| O-3 | LLM path is written and schema-bound but **unexercised** | No credentials on this machine. Needs one run against a real key before it can be claimed as working. |
| O-4 | Actor inference is keyword-based and can pick the wrong role | Known limitation L-2 in the QA document |
| O-5 | Rules-vs-LLM split measured only on our own fixtures | The real number needs a corpus of genuine customer documents |

---

## 8. Next

Layer 2 — Black Box Intelligence (crawl coordination, page analysis, journey
inference, safety governor), or widen Layer 1's corpus first with real customer
documents to get a true rules-vs-LLM split.
