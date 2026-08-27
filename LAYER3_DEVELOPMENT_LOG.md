# Layer 3 — Test Intelligence: Development Log

**Date:** 26 August 2026
**Scope:** Layer 3 of the nine-layer reference architecture (HLD §4.3)
**Status:** Built, 25 tests passing (58 across Layers 1 and 3), zero model calls

---

## 1. What it delivers

`document → [Layer 1] Requirement[] → TestPlan`, carrying all five HLD §4.3 outputs:

| Output | Where |
|---|---|
| Test Strategy | `TestStrategy` — scope, risk approach, formula, assumptions, limitations |
| `TestCase[]` with steps and expected results | `TestCase` + `TestStep` |
| Coverage map | `CoverageMap` — by workflow, confirmed vs inferred |
| Prioritised execution plan | `ExecutionPlan` — ranked, budget-fitted |
| Test data requirements | `TestDataRequirement` — fixtures, linked to tests |

Deterministic, offline, no API key.

## 2. Generation rules

From each requirement, mechanically: positive (always), boundary (from a stated
threshold), negative (from a nameable negation), required-field, permission,
precondition-unmet.

**The rule that matters most is the one about not generating.** Where a
requirement carries blocking ambiguity flags, Layer 3 emits a *clarification
request* naming the questions, instead of inventing an expected result — and
that requirement is **not counted as covered**. On the ambiguous fixture this
gives 7 requirements → 5 items, 4 of them questions, and coverage of **14.3%**
rather than a flattering 100%.

## 3. Scoring

```
score = 100 × (0.50·criticality + 0.30·defect_likelihood + 0.20·coverage_gap)
```

Every test publishes `score_breakdown` term by term. Three HLD terms are
declared unavailable rather than faked: `change_impact` (Layer 6),
`failure_history` and `recency_decay` (Layer 4).

**Defect-likelihood values are starting priors, not measured yield** — boundary
0.95, negative 0.90, positive 0.50. They become evidence-based once Layer 4
reports outcomes. This is the point where the product stops guessing.

## 4. Bugs found and fixed during the build

| # | Bug | Fix |
|---|---|---|
| 1 | `"a incorrect"` after word substitution | a/an agreement repair |
| 2 | Garbled negative expectation: *"The accounts overview is displayed does not happen"* | Reworded to *"The success outcome must NOT occur: …"* |
| 3 | Double negative — *"an email that is not unregistered"* | Skip negation when the rule is already negative |
| 4 | Duplicate permission tests from sibling criteria | Dedup on (category, workflow, title), merging traceability |
| 5 | Dedup was **too** aggressive — distinct precondition tests collapsed | Titles now name the precondition |
| 6 | **No P1 tests at all**; `1 − confidence` ranked well-written requirements *lower* | Removed confidence from scoring; weights redistributed to 0.50/0.30/0.20. Regression test added. |

Bug 6 is the instructive one: the formula was defensible on paper and wrong in
practice. It only showed up because the output was inspected, not just asserted.

## 5. Current state

```
58 tests passing (33 Layer 1 + 25 Layer 3)
0 model calls
```

`18_stories.pdf` → 10 requirements → **21 tests**, 100% coverage, 5 data
fixtures, 11 P1 / 10 P2, 7 tests fitting a 12-minute budget. The PDF and its
markdown source produce **identical** plans.

Top-ranked tests are permission bypass, account-lockout boundary, and negative
authentication — which is what a QA lead would choose.

## 6. Known limitation

Test steps are **business language**, not bound to page elements. They become
executable when Layer 2 supplies the application map. Every generated strategy
states this rather than leaving it to be discovered at execution time.

## 7. Next

Layer 2 — Black Box Intelligence. Playwright and Chromium are already installed.
Once it lands, `binding` flips from `business-language` to `bound`, and the same
plan becomes directly executable.
