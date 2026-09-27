# Model evaluation — test case generator

Run 27 Sep 2026 14:14. Leave-one-out over the two example stories in `sample_data/fewshot/Sample-US-TC.xlsx`, 2 run(s) per story per model.

**Pass criteria (fixed before running):** every run parses · mean coverage ≥ 0.75 · mean grounding issues ≤ 1.0 per run. The cheapest passing model is recommended.

| Model | Coverage | Grounding issues / run | Format flags / run | Test cases / run | Cost / story | Time / story | Pass |
|---|---|---|---|---|---|---|---|
| claude-haiku-4-5 | 71% | 0.0 | 1.0 | 8.2 | $0.0097 | 10.8s | ✗ |
| claude-sonnet-5 | 74% | 0.5 | 0.0 | 8.0 | $0.0314 | 26.9s | ✗ |
| claude-opus-5 | 97% | 0.0 | 0.0 | 13.2 | $0.1057 | 34.7s | ✓ |

**Recommended: claude-opus-5** — the cheapest model that passed.

## Detail

### claude-haiku-4-5 · US-1 · run 1

Coverage 62% · 9 test cases (8 derived) · $0.0097 · 12.9s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-002 |
| TC-LOGIN-003 invalid username | TC-LOGIN-003 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-004 |
| TC-LOGIN-005 password masking | **missing** |
| TC-LOGIN-006 locked-out user | **missing** |
| TC-LOGIN-007 no access without login | **missing** |
| TC-LOGIN-008 SQL injection | TC-LOGIN-008 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-005 (derived, required-field): Reject login with empty password field
- TC-LOGIN-006 (derived, required-field): Reject login with both username and password empty
- TC-LOGIN-007 (derived, state-transition): Remain on login page after failed login attempt
- TC-LOGIN-009 (derived, security): Prevent SQL injection via password field

### claude-haiku-4-5 · US-1 · run 2

Coverage 62% · 9 test cases (8 derived) · $0.0087 · 10.8s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-006 |
| TC-LOGIN-003 invalid username | TC-LOGIN-005 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-002 |
| TC-LOGIN-005 password masking | **missing** |
| TC-LOGIN-006 locked-out user | **missing** |
| TC-LOGIN-007 no access without login | **missing** |
| TC-LOGIN-008 SQL injection | TC-LOGIN-007 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-003 (derived, negative): Login fails with empty password field
- TC-LOGIN-004 (derived, negative): Login fails with both username and password empty
- TC-LOGIN-008 (derived, security): SQL injection attack in password field is rejected
- TC-LOGIN-009 (derived, navigation): Login page is accessible without authentication

### claude-haiku-4-5 · US-2 · run 1

Coverage 80% · 8 test cases (7 derived) · $0.0101 · 10.3s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-001 |
| TC-CART-002 add multiple products | TC-CART-002 |
| TC-CART-003 product details in cart | **missing** |
| TC-CART-004 remove product | TC-CART-004 |
| TC-CART-005 persists after navigating | TC-CART-004 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-003 (derived, boundary): Add the same product to the cart multiple times
- TC-CART-005 (derived, permission): Require login to add products to the cart
- TC-CART-006 (derived, state-transition): Preserve cart contents when navigating away from the Products page
- TC-CART-007 (derived, ui): Display feedback when a product is added to the cart
- TC-CART-008 (derived, boundary): Handle adding a product when the cart is already at capacity

### claude-haiku-4-5 · US-2 · run 2

Coverage 80% · 7 test cases (6 derived) · $0.0103 · 9.1s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-001 |
| TC-CART-002 add multiple products | TC-CART-004 |
| TC-CART-003 product details in cart | **missing** |
| TC-CART-004 remove product | TC-CART-003 |
| TC-CART-005 persists after navigating | TC-CART-006 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-002 (derived, ui): Update the cart count when a product is added
- TC-CART-005 (derived, boundary): Add the same product multiple times to the cart
- TC-CART-007 (derived, security): Allow an unauthenticated user to attempt adding a product

### claude-sonnet-5 · US-1 · run 1

Coverage 75% · 10 test cases (9 derived) · $0.0406 · 45.0s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-003 |
| TC-LOGIN-003 invalid username | TC-LOGIN-002 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-004 |
| TC-LOGIN-005 password masking | **missing** |
| TC-LOGIN-006 locked-out user | TC-LOGIN-007 |
| TC-LOGIN-007 no access without login | **missing** |
| TC-LOGIN-008 SQL injection | TC-LOGIN-008 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-005 (derived, required-field): Reject login when the password field is empty
- TC-LOGIN-006 (derived, required-field): Reject login when both username and password fields are empty
- TC-LOGIN-009 (derived, security): Reject login attempt using SQL injection payload in the password field
- TC-LOGIN-010 (derived, boundary): Verify username field is case sensitive or handled per application rules

### claude-sonnet-5 · US-1 · run 2

Coverage 62% · 7 test cases (6 derived) · $0.0218 · 17.3s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-002 |
| TC-LOGIN-003 invalid username | TC-LOGIN-003 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-004 |
| TC-LOGIN-005 password masking | **missing** |
| TC-LOGIN-006 locked-out user | **missing** |
| TC-LOGIN-007 no access without login | **missing** |
| TC-LOGIN-008 SQL injection | TC-LOGIN-007 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-005 (derived, required-field): Reject login when the password field is left empty
- TC-LOGIN-006 (derived, required-field): Reject login when both username and password fields are left empty

### claude-sonnet-5 · US-2 · run 1

Coverage 80% · 8 test cases (7 derived) · $0.0380 · 23.1s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-001 |
| TC-CART-002 add multiple products | TC-CART-003 |
| TC-CART-003 product details in cart | **missing** |
| TC-CART-004 remove product | TC-CART-002 |
| TC-CART-005 persists after navigating | TC-CART-008 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-004 (derived, boundary): Add all available products to the cart
- TC-CART-005 (derived, state-transition): Remove a product from the cart after adding it
- TC-CART-006 (derived, ui): Cart badge does not display when the cart is empty
- TC-CART-007 (derived, permission): Prevent adding a product to the cart without being logged in

Grounding issues (values not in the story or the example shown):

- grounding: step uses `Add to cart`, which is not in the story or the examples
- grounding: step uses `Remove`, which is not in the story or the examples

### claude-sonnet-5 · US-2 · run 2

Coverage 80% · 7 test cases (6 derived) · $0.0251 · 22.1s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-001 |
| TC-CART-002 add multiple products | TC-CART-002 |
| TC-CART-003 product details in cart | **missing** |
| TC-CART-004 remove product | TC-CART-004 |
| TC-CART-005 persists after navigating | TC-CART-005 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-003 (derived, positive): Verify an added product appears in the cart page
- TC-CART-006 (derived, permission): Prevent adding a product to the cart without being logged in
- TC-CART-007 (derived, boundary): Verify adding the same product twice does not duplicate it in the cart

### claude-opus-5 · US-1 · run 1

Coverage 100% · 14 test cases (13 derived) · $0.1151 · 35.6s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-002 |
| TC-LOGIN-003 invalid username | TC-LOGIN-003 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-004 |
| TC-LOGIN-005 password masking | TC-LOGIN-009 |
| TC-LOGIN-006 locked-out user | TC-LOGIN-012 |
| TC-LOGIN-007 no access without login | TC-LOGIN-012 |
| TC-LOGIN-008 SQL injection | TC-LOGIN-010 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-005 (derived, required-field): Reject login when the password field is empty
- TC-LOGIN-006 (derived, required-field): Reject login when both credential fields are empty
- TC-LOGIN-007 (derived, boundary): Verify credentials are treated as case sensitive
- TC-LOGIN-008 (derived, boundary): Verify surrounding whitespace in the username does not grant access unexpectedly
- TC-LOGIN-011 (derived, security): Verify script input in credential fields is not executed
- TC-LOGIN-013 (derived, permission): Verify a blocked or disabled account cannot log in
- TC-LOGIN-014 (derived, state-transition): Verify the error message is cleared or updated when credentials are corrected after a failed attempt

### claude-opus-5 · US-1 · run 2

Coverage 88% · 15 test cases (14 derived) · $0.1026 · 37.8s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-002 |
| TC-LOGIN-003 invalid username | TC-LOGIN-003 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-004 |
| TC-LOGIN-005 password masking | TC-LOGIN-010 |
| TC-LOGIN-006 locked-out user | TC-LOGIN-009 |
| TC-LOGIN-007 no access without login | **missing** |
| TC-LOGIN-008 SQL injection | TC-LOGIN-011 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-005 (derived, required-field): Reject login when the password field is empty
- TC-LOGIN-006 (derived, required-field): Reject login when both fields are empty
- TC-LOGIN-007 (derived, negative): Reject credentials that differ only by letter case
- TC-LOGIN-008 (derived, boundary): Trim-free handling of credentials with leading and trailing spaces
- TC-LOGIN-012 (derived, security): Reject script injection input in the username field
- TC-LOGIN-013 (derived, security): Prevent access to the authenticated area after logging out via browser back
- TC-LOGIN-014 (derived, state-transition): Clear a previous login error after correcting the credentials
- TC-LOGIN-015 (derived, ui): Submit the login form with the keyboard

### claude-opus-5 · US-2 · run 1

Coverage 100% · 12 test cases (10 derived) · $0.1144 · 32.0s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-001 |
| TC-CART-002 add multiple products | TC-CART-004 |
| TC-CART-003 product details in cart | TC-CART-002 |
| TC-CART-004 remove product | TC-CART-005 |
| TC-CART-005 persists after navigating | TC-CART-007 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-003 (derived, positive): Add a product to the cart from the product detail page
- TC-CART-006 (derived, state-transition): Remove an added product and confirm the cart state reverts
- TC-CART-008 (derived, state-transition): Cart contents persist after a page refresh
- TC-CART-009 (derived, permission): Prevent access to the cart page without logging in
- TC-CART-010 (derived, security): Cart is emptied or not carried over to another user after logout
- TC-CART-011 (derived, negative): Adding a product does not change the product price or details shown
- TC-CART-012 (derived, navigation): Proceed from the cart towards purchasing the selected product

### claude-opus-5 · US-2 · run 2

Coverage 100% · 12 test cases (10 derived) · $0.0908 · 33.5s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-001 |
| TC-CART-002 add multiple products | TC-CART-004 |
| TC-CART-003 product details in cart | TC-CART-002 |
| TC-CART-004 remove product | TC-CART-005 |
| TC-CART-005 persists after navigating | TC-CART-006 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-003 (derived, positive): Add a product to the cart from the product detail page
- TC-CART-007 (derived, state-transition): Cart contents persist across logout and login for the same user
- TC-CART-008 (derived, permission): Prevent adding a product to the cart without being logged in
- TC-CART-009 (derived, security): Prevent access to the cart page without being logged in
- TC-CART-010 (derived, boundary): Adding the same product twice does not duplicate it in the cart
- TC-CART-011 (derived, boundary): Add all available products to the cart and verify the count
- TC-CART-012 (derived, ui): Add to cart works after changing the product sort order

## Limits of this evaluation

- Two stories on one site. It shows which model is adequate on your own examples, not in general.
- Coverage is judged by keyword rules (`REFERENCE` in `tcgen/evaluate.py`). The per-run tables show exactly which case matched which reference, so a misjudged match can be checked.
- A test case beyond the reference isn't automatically good or bad; it needs a person to judge whether it follows from the story.
- Prices are list prices per million tokens as configured in `tcgen/llm.py`.
