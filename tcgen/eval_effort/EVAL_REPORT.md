# Model evaluation — test case generator

Run 27 Sep 2026 14:27. Leave-one-out over the two example stories in `sample_data/fewshot/Sample-US-TC.xlsx`, 2 run(s) per story per model.

**Pass criteria (fixed before running):** every run parses · mean coverage ≥ 0.75 · mean grounding issues ≤ 1.0 per run. The cheapest passing model is recommended.

| Model | Coverage | Grounding issues / run | Format flags / run | Test cases / run | Cost / story | Time / story | Pass |
|---|---|---|---|---|---|---|---|
| claude-opus-5 | 97% | 0.0 | 0.0 | 9.8 | $0.0635 | 20.2s | ✓ |

**Recommended: claude-opus-5** — the cheapest model that passed.

## Detail

### claude-opus-5 · US-1 · run 1

Coverage 100% · 9 test cases (8 derived) · $0.0513 · 18.6s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-002 |
| TC-LOGIN-003 invalid username | TC-LOGIN-003 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-004 |
| TC-LOGIN-005 password masking | TC-LOGIN-007 |
| TC-LOGIN-006 locked-out user | TC-LOGIN-004 |
| TC-LOGIN-007 no access without login | TC-LOGIN-009 |
| TC-LOGIN-008 SQL injection | TC-LOGIN-008 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-005 (derived, required-field): Require the password field
- TC-LOGIN-006 (derived, boundary): Verify credentials are case sensitive

### claude-opus-5 · US-1 · run 2

Coverage 88% · 11 test cases (10 derived) · $0.0677 · 23.1s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-002 |
| TC-LOGIN-003 invalid username | TC-LOGIN-003 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-004 |
| TC-LOGIN-005 password masking | TC-LOGIN-007 |
| TC-LOGIN-006 locked-out user | **missing** |
| TC-LOGIN-007 no access without login | TC-LOGIN-010 |
| TC-LOGIN-008 SQL injection | TC-LOGIN-008 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-005 (derived, required-field): Reject login when the password is empty
- TC-LOGIN-006 (derived, required-field): Reject login when both fields are empty
- TC-LOGIN-009 (derived, negative): Verify credentials are case-sensitive
- TC-LOGIN-011 (derived, ui): Verify the error message can be dismissed or cleared on a new attempt

### claude-opus-5 · US-2 · run 1

Coverage 100% · 9 test cases (7 derived) · $0.0771 · 18.2s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-001 |
| TC-CART-002 add multiple products | TC-CART-003 |
| TC-CART-003 product details in cart | TC-CART-002 |
| TC-CART-004 remove product | TC-CART-001 |
| TC-CART-005 persists after navigating | TC-CART-006 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-004 (derived, positive): Add a product to the cart from the product detail page
- TC-CART-005 (derived, state-transition): Remove a product that was added to the cart
- TC-CART-007 (derived, boundary): Adding the same product does not create duplicate entries
- TC-CART-008 (derived, permission): Cart page is not accessible without being logged in
- TC-CART-009 (derived, navigation): Proceed to checkout with a product in the cart

### claude-opus-5 · US-2 · run 2

Coverage 100% · 10 test cases (7 derived) · $0.0581 · 21.1s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-001 |
| TC-CART-002 add multiple products | TC-CART-003 |
| TC-CART-003 product details in cart | TC-CART-002 |
| TC-CART-004 remove product | TC-CART-001 |
| TC-CART-005 persists after navigating | TC-CART-006 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-004 (derived, positive): Add a product to the cart from the product detail page
- TC-CART-005 (derived, state-transition): Remove a previously added product from the Products page
- TC-CART-007 (derived, state-transition): Cart contents persist after logout and login again
- TC-CART-008 (derived, permission): Prevent access to the cart page without being logged in
- TC-CART-009 (derived, boundary): Adding the same product twice is not possible from the Products page
- TC-CART-010 (stated, navigation): Proceed to checkout from a cart containing a product

## Limits of this evaluation

- Two stories on one site. It shows which model is adequate on your own examples, not in general.
- Coverage is judged by keyword rules (`REFERENCE` in `tcgen/evaluate.py`). The per-run tables show exactly which case matched which reference, so a misjudged match can be checked.
- A test case beyond the reference isn't automatically good or bad; it needs a person to judge whether it follows from the story.
- Prices are list prices per million tokens as configured in `tcgen/llm.py`.
