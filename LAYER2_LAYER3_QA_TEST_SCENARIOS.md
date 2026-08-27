# Layers 2 & 3 — QA Test Scenarios

**Components under test:** Layer 2 (Black Box Intelligence, HLD §4.2) and Layer 3 (Test Intelligence, HLD §4.3), including the Layer 2 → Layer 3 binding.
**Date executed:** 26 August 2026
**Result:** 30 scenarios executed — **30 passed**, 0 open defects. **91 automated tests green** (33 Layer 1, 27 Layer 2, 31 Layer 3).

Layer 2 drives a live application with real credentials, so the scenarios that
matter most are not about coverage — they are about proving it refuses to do
damage, degrades honestly when things go wrong, and never presents a guess as a
fact.

---

## 1. Test target

Layer 2 needs something real to crawl, so the repo ships one:
[`demo_app/app.py`](demo_app/app.py) — "Northwind Bank", a small application
built specifically to exercise the hard parts.

```bash
python3 -m demo_app.app        # 127.0.0.1:8020
```

| It contains | So that we can test |
|---|---|
| Form login + session cookie | The auth adapter |
| `/admin` returning **403** to a customer | Access-denied detection |
| Required fields on `/transfer` and `/settings` | Required-field inference |
| A `<select>` with fixed options | Input-domain inference |
| **"Close account permanently"** (styled danger) | Safety Governor |
| **"Send transfer"** (moves money) | Action-vs-navigation distinction |
| **"Sign out"** | Session-ending protection |
| `/help`, `/statements/download` | Dead ends and leaf pages |
| Two roles (customer, admin) | Role-dependent discovery |

Credentials are in the demo app source. They are deliberately *not* realistic secrets.

---

## 2. Layer 2 — scenario results

### 2.1 Crawl and authentication

| ID | Scenario | Expected | Actual | |
|---|---|---|---|---|
| L2-101 | Anonymous crawl finds only public pages | Public pages only, not authenticated | 3 pages, `authenticated=False` | ✅ |
| L2-102 | Form login reaches protected pages | Authenticated, protected pages found | 9 pages, `authenticated=True`, incl. `/dashboard`, `/transfer`, `/settings` | ✅ |
| L2-103 | Wrong password **degrades**, does not fail | Warning + public-only crawl | `authenticated=False`, 1 warning, 3 pages still crawled | ✅ |
| L2-104 | Unreachable host does not crash | 0 pages + warning | 0 pages, 1 warning, no exception | ✅ |
| L2-105 | Admin role sees admin pages | `/admin` returns 200 | `/admin` 200 as admin | ✅ |
| L2-106 | A page that errors mid-crawl doesn't end the crawl | Warning, crawl continues | Confirmed (found a real bug in the demo app — see §5) | ✅ |

### 2.2 Budget and politeness — never DoS the customer

| ID | Scenario | Expected | Actual | |
|---|---|---|---|---|
| L2-201 | `max_pages=2` is enforced | Exactly 2 pages + budget warning | 2 pages, budget warning raised | ✅ |
| L2-202 | `max_depth=0` stops at the entry point | 1 page | 1 page | ✅ |
| L2-203 | `scope_deny` excludes paths | `/settings` never fetched | `settings_crawled=False`, 2 paths skipped | ✅ |
| L2-204 | Parameterised routes don't explode the frontier | Same structure → one page | Signature dedupe confirmed by unit test | ✅ |
| L2-205 | Politeness delay between requests | Delay applied | 120 ms default, configurable | ✅ |

### 2.3 Safety Governor — the scenarios that matter most

| ID | Scenario | Expected | Actual | |
|---|---|---|---|---|
| L2-301 | Destructive actions are blocked | Blocked with a stated reason | 7 blocked: Close account, Send transfer, Sign out (×5) | ✅ |
| L2-302 | Safe actions stay allowed | Not blocked | Sign in, Save changes, Download CSV all allowed | ✅ |
| L2-303 | **Navigation vs action** — the subtle one | `/transfer` *link* allowed; "Send transfer" *button* blocked | Exactly that | ✅ |
| L2-304 | Danger styling alone is enough | Blocked | `class="btn danger"` blocks | ✅ |
| L2-305 | Sign-out is protected | Blocked (would end the session) | Blocked on every page | ✅ |
| L2-306 | Opt-in works, and only when explicit | Off → 7 blocked; on → 0 blocked | `allow_destructive=False` → 7; `True` → 0 | ✅ |
| L2-307 | Nothing blocked is ever clicked | No destructive action performed | Discovery navigates and reads only; it never submits | ✅ |

### 2.4 Inference honesty (BR-03)

| ID | Scenario | Expected | Actual | |
|---|---|---|---|---|
| L2-401 | Everything discovered is typed `discovered` | 100% | 18/18, `is_confirmed=False` on all | ✅ |
| L2-402 | Nothing discovered claims full confidence | All < 1.0 | 0.50 – 0.88 | ✅ |
| L2-403 | Every discovered item says it was inferred | Flag on all | All carry the "inferred from observed behaviour" flag | ✅ |
| L2-404 | A 403 becomes a Critical requirement | Critical | `discovered:/admin#access`, Critical, confidence 0.88 | ✅ |
| L2-405 | Blocked actions still become requirements | Flagged for manual testing | Expected outcome reads *"Behaviour not verified — discovery refused to trigger this action"* | ✅ |
| L2-406 | Unobserved outcomes are not claimed | Form-submit outcome marked unobserved | Flag: *"the successful outcome was not observed — discovery does not submit forms"* | ✅ |
| L2-407 | **Credentials never reach any artefact** | Absent from map and requirements | `Passw0rd!23` not present in either | ✅ |

### 2.5 Element inventory

| ID | Scenario | Expected | Actual | |
|---|---|---|---|---|
| L2-501 | Required fields are detected | `Amount` on `/transfer` | Found, plus `Display name`, `Email address`, `Password` | ✅ |
| L2-502 | Locator chain is ordered by preference | role/label first, then test-id, css, structural | Confirmed; `get_by_label("Password")` preferred | ✅ |
| L2-503 | Select options are captured | Options listed | `Current`, `Savings` captured | ✅ |
| L2-504 | Journeys are genuinely reachable routes | Every path in the map, confidence < 1.0 | 3 journeys, all reachable, 0.75–0.85 | ✅ |

---

## 3. Layer 3 — scenario results (with Layer 2)

| ID | Scenario | Expected | Actual | |
|---|---|---|---|---|
| L3-601 | Document alone → readable but unbound plan | Tests built, nothing bound | 21 tests, 0 bound, 100% coverage | ✅ |
| L3-602 | **URL alone** → plan from discovery only | Plan built with no document | 18 discovered → **31 tests**, 23 fully bound | ✅ |
| L3-603 | **Document + URL** → merged | One plan, both sources | 28 requirements → **52 tests** | ✅ |
| L3-604 | Binding attaches real locators | Steps carry page + locator | 35 bound, 11 partial, 6 business-language | ✅ |
| L3-605 | Unmatched steps keep business language | No guessed selector | Confirmed — unbound steps have `locator=None` | ✅ |
| L3-606 | Confirmed and inferred counted separately (BR-03) | Split reported | confirmed 10 / inferred 18 | ✅ |
| L3-607 | Strategy limitation changes once bound | Wording flips | "not yet bound" disappears when a map is supplied | ✅ |
| L3-608 | Dead URL still yields a document plan | Degrade, don't fail | 21 tests built, discovery failure warned | ✅ |
| L3-609 | Vague document still produces questions | Clarifications, low coverage | 4 clarifications, 6 unclear refs | ✅ |
| L3-610 | Budget defers the lowest-ranked tests | Cut-off respected | 11/52 within 20 min | ✅ |
| L3-611 | Plan is deterministic | Identical across runs | Byte-identical | ✅ |
| L3-612 | No credentials in the test plan | Absent | `Passw0rd!23` not present | ✅ |

---

## 4. Coverage against the acceptance bar

| Criterion | Scenarios | Status |
|---|---|---|
| Discovery never performs a destructive action | L2-301 → L2-307 | Met |
| Discovery never degrades the target environment | L2-201 → L2-205 | Met |
| Observation is never presented as confirmed intent (BR-03) | L2-401 → L2-406, L3-606 | Met |
| Credentials never reach an artefact (C-05, BR-07) | L2-407, L3-612 | Met |
| Failure is visible, never silent (HLD §4.2) | L2-103, L2-104, L2-106, L3-608 | Met |
| Locator chain supports later healing (HLD §10.3) | L2-502 | Met |
| Two ingestion paths converge on one pipeline (HLD §3.4) | L3-602, L3-603 | Met |
| Binding is a match, never a guess | L3-604, L3-605 | Met |

---

## 5. Defects found

**One — in the demo app, not the product.** `/statements/download` passed the
session dict where the HTTP status code was expected, producing
`ERR_EMPTY_RESPONSE`. Layer 2 caught it, recorded a warning naming the path and
the error, and carried on crawling the other eight pages.

That is the behaviour the design asks for (HLD §4.2: failure is partial and
visible), and it is worth noting that **the crawler found a real bug on its
first run against a real application** — which is, after all, the product's
entire purpose.

No defects were found in Layer 2 or Layer 3 themselves during this pass.

---

## 6. Known limitations (accepted, not defects)

| # | Limitation | Why acceptable |
|---|---|---|
| L-1 | Discovery does not submit forms, so success outcomes are unobserved | Submitting is how you break a customer's data. Every affected requirement says the outcome was not observed. |
| L-2 | Role-gated pages are invisible without the role | A customer session genuinely cannot see the admin link. Use `--probe /admin` or crawl with each role. |
| L-3 | Workflow names from documents and discovery are not merged | "Customer Login" and "Sign in" may both appear. Merging automatically risks combining two genuinely different areas; it is left visible and declared in the strategy. |
| L-4 | Journeys are shortest reachable routes, not behavioural sequences | Real multi-step journeys need form submission (L-1). Confidence is capped at 0.85 to reflect this. |
| L-5 | Single-page applications are untested | The demo target is server-rendered. SPA wait strategies are a known risk (HLD AR-03). |
| L-6 | No OCR, no SPA hydration waits, no MFA | Out of scope for this build; adapters exist as seams. |

---

## 7. How to re-run

```bash
python3 -m pytest tests/ -q
```

```bash
python3 -m demo_app.app
```

```bash
python3 -m layer3 sample_data/qa/18_stories.pdf --url http://127.0.0.1:8020 --user customer@example.com --password 'Passw0rd!23' --probe /admin --budget 20
```

Or drive it all from the UI: `python3 -m layer1.web`, fill in the **Live
application** fields, and use the **App Map** and **Test Plan** tabs.
