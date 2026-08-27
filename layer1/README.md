# Layer 1 — Requirements Intelligence

Ingests a document containing stories/requirements and emits validated
`Requirement[]` records, exactly as specified in HLD §4.1:

```
{actor, workflow, rule, precondition, expected_outcome,
 risk, source, source_ref, confidence, ambiguity_flags}
```

## Run the UI

```bash
python3 -m layer1.web
```

Opens `http://127.0.0.1:8010` (next free port if that one is taken). Pick any of
the 19 bundled documents from the sidebar, or drop in your own, and inspect
every field of the extracted `Requirement[]`. The **Contract JSON** tab shows
the raw records so you can check them against HLD §4.1.

Standard library only — no FastAPI, no uvicorn, nothing to install.

## Run the CLI

```bash
python3 -m layer1 sample_data/user_stories.md --no-llm
```

```bash
python3 -m layer1 sample_data/jira_sample_issues.json --no-llm --json requirements.json
```

`--no-llm` is fully offline: no API key, no network, no cost, and the same
document always produces byte-identical output.

## Design

**Rules first, AI second.** A deterministic engine handles every document shape
with recognisable structure — Jira fields, spreadsheet rows, `As a / I want`,
`Given/When/Then`, acceptance-criteria bullets. Only blocks it cannot crack are
offered to the LLM, under a block budget. The CLI reports the split
(`extracted by: rules 16`), so AI dependency is measured rather than assumed.

| Module | Role |
|---|---|
| `contracts.py` | The `Requirement` contract. Enforces BR-03 (source is typed) and ADR-005 (schema-validated). |
| `parsers.py` | `IDocumentParser` seam + registry: markdown, docx, pdf, xlsx, Jira JSON. |
| `rules.py` | Deterministic extraction, risk scoring, ambiguity detection, confidence. |
| `llm.py` | Optional enricher. Never sets `source`/`source_ref`; runs under a budget. |
| `pipeline.py` | `document → parse → rules → (LLM leftovers) → Requirement[]`. |
| `cli.py` | Demo output + `--json` contract export. |

**Confidence is earned, not asserted.** It accumulates from what was actually
found — explicit actor, explicit outcome, stated precondition — and is reduced
per ambiguity flag. It is extraction confidence, never evidence (BR-09).

**Failure is visible.** An unparseable PDF page or an unrecognisable block
becomes a warning on the result, never a silently missing requirement.

## Tests

```bash
python3 -m pytest tests/test_layer1.py -q
```

## Adding a format

Implement `IDocumentParser`, set `extensions`, call `register()`. No changes to
extraction or the pipeline (HLD §8.4, QA-10).
