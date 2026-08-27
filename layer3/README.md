# Layer 3 — Test Intelligence

Turns Layer 1's `Requirement[]` into the five outputs HLD §4.3 specifies:

1. **Test Strategy** — scope, risk approach, scoring formula, assumptions, limitations
2. **`TestCase[]`** — steps and expected results, traced back to requirements
3. **Coverage map** — by workflow, confirmed vs inferred (BR-03)
4. **Prioritised execution plan** — ranked by score, fitted to a run budget
5. **Test data requirements** — fixtures each test needs

## Run it

```bash
python3 -m layer3 sample_data/qa/18_stories.pdf --budget 12
```

```bash
python3 -m layer3 requirements.pdf --budget 30 --json plan.json
```

Or use the UI (`python3 -m layer1.web`) — the **Test Plan** tab.

Deterministic and offline. No model calls.

## How tests are generated

From each requirement, mechanically:

| Trigger in the requirement | Test produced |
|---|---|
| always | **positive** — the stated happy path |
| a threshold ("at least 12 characters", "five times") | **boundary** — on the limit, and just under |
| a nameable negation ("valid", "correct", "without") | **negative** |
| "mandatory", "required", "without X" | **required_field** |
| access/role/permission wording + a role actor | **permission** |
| a stated precondition | **precondition** not met |
| blocking ambiguity flags | **clarification** — a question, not a test |

That last row is the important one. Where a requirement is too vague to test,
this emits the questions that need answering rather than inventing an expected
result. A confident test built on a guess is worse than no test.

## Scoring

```
score = 100 × (0.50·criticality + 0.30·defect_likelihood + 0.20·coverage_gap)
```

Every test carries its `score_breakdown` term by term, so the ordering can be
shown to a customer, argued with, and corrected by changing an input.

Three terms from the HLD formula are **not** scored yet, and the strategy says so:
`change_impact` needs source control (Layer 6); `failure_history` and
`recency_decay` need executed runs (Layer 4).

Extraction confidence is deliberately **not** a scoring term — an earlier
revision scored `1 − confidence`, which ranked well-written requirements
*lower* than badly-written ones. There's a regression test for it.

## Known limitation

Test steps are **business language**, not bound to page elements. They become
executable when Layer 2 supplies the application map. This is stated in every
generated strategy rather than left to be discovered at execution time.

## Tests

```bash
python3 -m pytest tests/ -q
```
