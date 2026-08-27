# Layer 2 — Black Box Intelligence: Development Log

**Date:** 26 August 2026
**Scope:** Layer 2 (HLD §4.2) and its integration into Layer 3
**Status:** Built, 27 Layer 2 tests + 6 integration tests passing (91 total), zero model calls

---

## 1. What it does

`URL (+ optional credentials) → ApplicationMap + Requirement[]`

It drives a real Chromium through the application, inventories what it finds,
and emits **the same `Requirement` contract Layer 1 produces** — tagged
`source = discovered`. That is HLD §3.4 made real: documents and discovery are
two ingestion strategies, not two pipelines. Layer 3 never needs to know which
one a requirement came from.

## 2. Modules

| File | Role |
|---|---|
| `contracts.py` | `Page`, `Element`, `Form`, `Journey`, `ApplicationMap`, `CrawlBudget` |
| `safety.py` | **Safety Governor** — deterministic deny-list, below the agent (ADR-011) |
| `auth.py` | `IAuthAdapter` seam + `FormLogin` |
| `analyse.py` | One in-page evaluation → elements, forms, locator chains, page signature |
| `crawler.py` | Bounded, polite, signature-deduplicated BFS |
| `infer.py` | Observed behaviour → `Requirement[]` (`source=discovered`) |
| `pipeline.py` / `cli.py` | `python3 -m layer2 <url>` |

Plus `demo_app/app.py` — a bank-like target built to exercise the hard parts.

## 3. The three decisions that shaped it

**The Safety Governor is deterministic and sits below everything.** No model is
involved, so no prompt can talk past it. It blocks by *element kind*, which is
the subtle part: the `/transfer` **link** is allowed (discovery must be able to
open the payments area) while the **"Send transfer" button** is blocked (it
moves real money). Getting that distinction wrong in either direction makes the
product either useless or dangerous.

**Discovery navigates and reads; it never submits.** So form success outcomes
are genuinely unobserved, and every affected requirement says so rather than
claiming a result we never saw.

**Everything is bounded before it starts.** `max_pages`, `max_depth`, per-page
timeout, politeness delay, `scope_deny`. Pages are deduplicated by structural
**signature**, not URL, so `/orders/1` and `/orders/2` count once.

## 4. Integration into Layer 3

`layer3/binder.py` attaches real page paths and locators to test steps:

- A discovered requirement already names its page — exact match, no guessing.
- Otherwise the workflow name is matched against page titles and headings, with a threshold.
- **Unmatched steps keep their business language.** A plausible-looking wrong
  selector is worse than an honest gap, because it fails for reasons that have
  nothing to do with the product.

Result on the demo target: document (PDF) 10 requirements + discovery 18 = 28
requirements → **52 tests, 35 fully bound, 11 partially, 6 business-language**.

## 5. Bugs found and fixed

| # | Bug | Fix |
|---|---|---|
| 1 | `"Send transfer"` was allowed — money-word patterns needed a following noun | Split rules into always-block vs action-only; made the governor element-kind aware |
| 2 | Demo app `/statements/download` returned `ERR_EMPTY_RESPONSE` | Passed the session dict where the HTTP status was expected. **Found by the crawler on its first real run.** |
| 3 | Character-level line grouping produced `"passwor d"` | Group *words*, not characters |

## 6. Current state

```
91 tests passing (33 Layer 1, 27 Layer 2, 31 Layer 3)
0 model calls
```

On the demo target, authenticated as a customer with `--probe /admin`:
9 pages, 4 forms, 57 elements, 3 journeys, **8 destructive actions blocked**,
18 discovered requirements — including `/admin` returning 403, detected as
access-denied and raised as a Critical requirement at confidence 0.88.

## 7. Known limitations

See [LAYER2_LAYER3_QA_TEST_SCENARIOS.md](LAYER2_LAYER3_QA_TEST_SCENARIOS.md) §6.
The two that matter: form success outcomes are unobserved (because we do not
submit), and single-page applications are untested — the demo target is
server-rendered, and SPA discovery is the HLD's own AR-03 risk.

## 8. Next

Layer 4 — Execution. The bound tests are now directly runnable, and running them
is what replaces Layer 3's estimated defect-likelihood priors with measured
yield.
