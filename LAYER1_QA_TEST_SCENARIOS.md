# Layer 1 — Requirements Intelligence: QA Test Scenarios

**Component under test:** Layer 1, Requirements Intelligence (HLD §4.1)
**Build tested:** `layer1/` — rules engine, offline mode (`--no-llm`)
**Date executed:** 26 August 2026
**Result:** 24 scenarios executed — **24 passed**, 4 defects found and fixed, 33 automated tests green

This is Layer 1 tested as a product, not as a library. Every scenario has a real
input file under `sample_data/qa/`, a stated expected result, and a recorded
actual result. Where actual diverged from expected, a defect was raised, fixed,
and locked behind a regression test.

---

## 1. What is being tested

Layer 1 ingests a document containing stories/requirements and emits validated
`Requirement[]` records with exactly these fields (HLD §4.1):

```
{actor, workflow, rule, precondition, expected_outcome,
 risk, source, source_ref, confidence, ambiguity_flags}
```

The acceptance bar for this layer:

| # | Criterion | Traces to |
|---|---|---|
| AC-1 | Output validates against the contract; no extra or missing fields | ADR-005 |
| AC-2 | Every requirement is traceable to its origin via `source` + `source_ref` | BR-02 |
| AC-3 | `source` is typed; discovered content can never present as confirmed | BR-03, C-06 |
| AC-4 | Vague or untestable wording is flagged, not silently accepted | HLD §4.1 Ambiguity Detector |
| AC-5 | Unparseable input degrades visibly; it never fails silently | HLD §4.1 design note |
| AC-6 | Offline runs are reproducible byte-for-byte | ADR-006, ADR-012 |
| AC-7 | Confidence is earned from evidence found, and is not evidence | BR-09 |
| AC-8 | Document content is data, never instruction | QA-08, HLD §5.4 |

---

## 2. Test fixtures

All under [`sample_data/qa/`](sample_data/qa/). They are deliberately uneven —
half of them are documents a QA team would be unhappy to receive.

| File | Represents | Why it exists |
|---|---|---|
| `01_happy_path_stories.md` | 4 clean user stories, 10 acceptance criteria | Baseline extraction quality |
| `02_ambiguous_requirements.md` | 4 unreviewed draft stories | Every ambiguity class in one file |
| `03_gherkin_only.md` | 3 Given/When/Then scenarios, no story form | Gherkin without user-story framing |
| `04_prose_no_structure.md` | Narrative platform notes | Rules must decline, not invent |
| `05_no_requirements.md` | Retrospective meeting notes | Document with genuinely nothing to extract |
| `06_empty.md` | Empty file | Degenerate input |
| `07_prompt_injection.md` | Stories with an embedded "ignore all previous instructions" block | Untrusted-content handling |
| `08_unicode_multilingual.md` | French, Japanese, currency and arrow symbols | Encoding integrity |
| `09_duplicates.md` | Same acceptance criterion stated twice | Requirements-quality detection |
| `10_malformed.json` | Jira export with a string, a missing key, an empty summary | Hostile structured input |
| `11_wrong_json_shape.json` | Valid JSON, no `issues` array | Wrong-shape input |
| `12_priority_mapping.json` | Blocker / Major / Normal / Trivial / unset | Deterministic risk mapping |
| `13_unsupported.rtf` | Rich Text Format | Unsupported format handling |
| `14_test_cases.xlsx` | 2 sheets, 8 test cases, real QA column layout | Spreadsheet ingestion |
| `15_requirements.docx` | Word doc: headings, bullet ACs, a requirements table | Word structure and tables |
| `16_scanned_no_text.pdf` | Valid PDF with no text layer | Scanned-document handling |
| `17_large_volume.md` | 60 stories, 120 acceptance criteria (21 KB) | Volume and throughput |

Reproduce any scenario with:

```bash
python3 -m layer1 sample_data/qa/01_happy_path_stories.md --no-llm
```

---

## 3. Scenario results

Legend: **P** pass · **D** defect found (all four since fixed and regression-tested).

### 3.1 Positive / happy path

| ID | Scenario | Fixture | Expected | Actual | |
|---|---|---|---|---|---|
| QA-101 | Well-formed stories with acceptance criteria extract cleanly | `01` | One requirement per criterion, no ambiguity flags, high confidence | 10 requirements, 0 flagged, avg confidence **0.98** | P |
| QA-102 | Each acceptance criterion becomes an independently testable requirement | `01` | 4 stories → 10 requirements | 10 requirements, refs `#US-101/AC1` … `#US-104/AC2` | P |
| QA-103 | Inline `Given…when…then` splits into three fields | `01` | `precondition` / `rule` / `expected_outcome` populated separately | Split correctly on all 10 | P |
| QA-104 | Gherkin without user-story framing is handled | `03` | 3 requirements with preconditions | 3 requirements, avg confidence **0.99** | P |
| QA-105 | Spreadsheet test cases ingest with sheet name as workflow | `14` | 8 requirements across 2 sheets | 8 requirements, workflows `Authentication` / `Payments` | P |
| QA-106 | Word document headings, bullet ACs and tables all extract | `15` | ≥ 6 requirements including table rows | **2 requirements** — bullets and tables lost | **D — DEF-02** |
| QA-106r | *(after fix)* | `15` | ≥ 6 | 7 requirements, incl. `#table1!row2` | P |

### 3.2 Requirements-quality detection

| ID | Scenario | Fixture | Expected | Actual | |
|---|---|---|---|---|---|
| QA-201 | Vague wording is flagged on every affected requirement | `02` | 100% flagged, confidence materially lower | 7/7 flagged, avg confidence **0.50** | P |
| QA-202 | Specific ambiguity classes are named, not just "ambiguous" | `02` | Named reasons per flag | e.g. `unquantified performance term 'fast'`, `subjective term 'user-friendly'`, `open-ended list 'etc'`, `non-committal modality` | P |
| QA-203 | A story with no acceptance criteria is flagged as not yet testable | `01`,`02` | Flag raised, outcome not fabricated | Flag: *"no acceptance criteria — expected outcome derived from the story's 'so that' benefit"* | P |
| QA-204 | A criterion repeated verbatim is flagged | `09` | Second occurrence flagged as duplicate | **Not detected** — three requirements emitted, none flagged | **D — DEF-04** |
| QA-204r | *(after fix)* | `09` | Duplicate named with its first occurrence | `duplicates …#US-601/AC1 — the same criterion is stated more than once` | P |
| QA-205 | Clean requirements carry no flags | `01` | Zero false-positive flags | 0 of 10 flagged | P |

### 3.3 Risk scoring

| ID | Scenario | Fixture | Expected | Actual | |
|---|---|---|---|---|---|
| QA-301 | An explicit priority field always wins over keywords | `12` | Blocker→Critical, Major→High, Normal→Medium, Trivial→Low | Exactly as expected | P |
| QA-302 | Cosmetic change on a sensitive page is scored cosmetic | `12` (PRI-5) | Low — "footer colour" is the subject, "payment" only the location | **Critical** — severity-ordered keyword match | **D — DEF-03** |
| QA-302r | *(after fix)* | `12` | Low | **Low** — tier now chosen by weight of evidence | P |
| QA-303 | Auth, payment and permission requirements score Critical | `01` | Critical for sign-in and audit-access rules | Critical on both | P |

### 3.4 Negative, edge and degenerate input

| ID | Scenario | Fixture | Expected | Actual | |
|---|---|---|---|---|---|
| QA-401 | Narrative prose yields nothing rather than invented requirements | `04` | 0 requirements + visible warning | 0 requirements, warning names the unresolved block | P |
| QA-402 | A document with no requirements yields none | `05` | 0 requirements, no crash | 0 requirements | P |
| QA-403 | Empty file is reported, not silently empty | `06` | Explicit warning | `document produced no readable blocks` | P |
| QA-404 | Malformed Jira export degrades to what is usable | `10` | Extract the valid issue, warn on the rest | **AttributeError crash** on the string entry | **D — DEF-01** |
| QA-404r | *(after fix)* | `10` | Valid issue extracted, others warned | 1 requirement + warnings naming each bad entry | P |
| QA-405 | Valid JSON of the wrong shape is rejected cleanly | `11` | Warning, no crash | `unrecognised JSON shape; expected a list of issues` | P |
| QA-406 | Unsupported format fails with an actionable message | `13` | Named error listing supported formats | `No parser registered for '.rtf'. Supported: .docx, .json, .markdown, .md, .pdf, .txt, .xlsm, .xlsx` — CLI exit code 2 | P |
| QA-407 | PDF with no text layer points at the real cause | `16` | Warning naming OCR | `no extractable text (scanned PDF? OCR not enabled)` | P |

### 3.5 Integrity, security and reproducibility

| ID | Scenario | Fixture | Expected | Actual | |
|---|---|---|---|---|---|
| QA-501 | Embedded instructions cannot alter traceability or scoring | `07` | `source` unchanged, confidence unchanged, no secrets echoed | `source=document` on both; confidence 0.99 (not the demanded 1.0); injection block left unresolved; no env content emitted | P |
| QA-502 | Jira origin is preserved exactly | `12` | `source=jira`, `source_ref` = issue key | `source=jira`, refs `PRI-1`…`PRI-5` | P |
| QA-503 | Document origin is never labelled as Jira | `01` | `source=document` throughout | All 10 `document` | P |
| QA-504 | Output contains exactly the contract fields | all | 10 fields, no more, no fewer | Verified via `--json` on every fixture | P |
| QA-505 | Offline runs are byte-identical across runs | `01` | Repeat runs match exactly | Identical (automated test) | P |
| QA-506 | Unicode survives end to end | `08` | Japanese, French accents, currency/arrow symbols intact | `電子メール通知`, `«Réglages enregistrés»`, `£ € ¥ ☑ →` all preserved | P |
| QA-507 | No LLM call is made in offline mode | all | `extractor == "rules"`, zero cost | `extracted by: rules` on all 17 fixtures; no network | P |

### 3.6 Volume

| ID | Scenario | Fixture | Expected | Actual | |
|---|---|---|---|---|---|
| QA-601 | Large document extracts completely | `17` | 60 stories × 2 criteria = 120 requirements | **120** requirements, none dropped | P |
| QA-602 | Throughput is not a bottleneck at this layer | `17` | Sub-second | **13 ms** for 21 KB / 120 requirements (1 ms for the 4-story file) | P |

---

## 4. Defects found and fixed

| ID | Severity | Defect | Root cause | Fix | Regression test |
|---|---|---|---|---|---|
| DEF-01 | **High** | Malformed Jira export crashed the run with `AttributeError` | `issue.get()` called on a JSON array element that was a string | Type-check each entry; skip with a named warning | `test_def01_malformed_jira_export_degrades_instead_of_crashing` |
| DEF-02 | **High** | Word documents lost acceptance criteria and tables (2 requirements instead of 7) | `python-docx` stores bullets as list *formatting*, so `.text` has no marker; tables were flattened into the previous block | Restore the `- ` marker for `List` styles; emit each table row as its own block with header labels | `test_def02_docx_bullets_and_tables_are_extracted` |
| DEF-03 | **Medium** | Cosmetic change on a payment page scored Critical | Risk keywords were matched in severity order, so any Critical keyword anywhere won | Score every tier by number of matches and take the best-evidenced; ties break to higher severity | `test_def03_cosmetic_change_outranks_domain_keyword` |
| DEF-04 | **Medium** | A criterion stated twice produced two unflagged requirements | No duplicate detection existed | Flag repeats against the first occurrence's `source_ref` | `test_def04_repeated_criterion_is_flagged` |

Two of the four (DEF-01, DEF-02) were only reachable through real file formats —
they would not have surfaced from unit tests over synthetic strings.

---

## 5. Known limitations (accepted, not defects)

These are recorded so nobody re-raises them as bugs:

| # | Limitation | Why it is acceptable |
|---|---|---|
| L-1 | Narrative prose yields no requirements in offline mode | Correct behaviour: the rules decline to invent. The LLM enricher exists for this and reports the unresolved count. |
| L-2 | Actor inference can pick the wrong role in mixed-role text (e.g. "Administrator" where the criterion concerns a standard user) | Keyword heuristic. Flagged as a Layer 1 accuracy item; LLM enrichment or an explicit `Actor:` field resolves it. |
| L-3 | `workflow` falls back to the story heading, which is a title rather than a domain workflow | Traceable and readable; Layer 3 normalises workflows across a project. |
| L-4 | Scanned PDFs produce nothing | OCR is deliberately out of scope for this build; the warning names the cause. |
| L-5 | No semantic deduplication — only verbatim repeats are flagged | Semantic dedup belongs to the Suite Optimiser in Layer 3 (HLD §4.3). |

---

## 6. Coverage against the acceptance bar

| Criterion | Scenarios | Status |
|---|---|---|
| AC-1 contract validity | QA-504 | Met |
| AC-2 traceability | QA-102, QA-502, QA-503 | Met |
| AC-3 typed source | QA-501, QA-503 | Met |
| AC-4 ambiguity detection | QA-201 → QA-205 | Met |
| AC-5 visible degradation | QA-401 → QA-407 | Met |
| AC-6 reproducibility | QA-505, QA-507 | Met |
| AC-7 earned confidence | QA-101, QA-201 | Met |
| AC-8 content-as-data | QA-501 | Met |

---

## 7. How to re-run

```bash
python3 -m pytest tests/test_layer1.py -q
```

```bash
for f in sample_data/qa/*; do echo "== $f"; python3 -m layer1 "$f" --no-llm --no-colour; done
```

**Current state:** 33 automated tests, all passing. 17 fixtures, all exercised.
