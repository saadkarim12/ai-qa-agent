# Model evaluation — test case generator

Run 27 Sep 2026 14:05. Leave-one-out over the two example stories in `sample_data/fewshot/Sample-US-TC.xlsx`, 2 run(s) per story per model.

**Pass criteria (fixed before running):** every run parses · mean coverage ≥ 0.75 · mean grounding issues ≤ 1.0 per run. The cheapest passing model is recommended.

| Model | Coverage | Grounding issues / run | Format flags / run | Test cases / run | Cost / story | Time / story | Pass |
|---|---|---|---|---|---|---|---|
| claude-haiku-4-5 | 66% | 0.5 | 1.8 | 8.5 | $0.0093 | 10.2s | ✗ |
| claude-sonnet-5 | 94% | 7.2 | 0.0 | 9.5 | $0.0342 | 23.7s | ✗ |
| claude-opus-5 | 97% | 3.8 | 0.0 | 10.5 | $0.0861 | 28.5s | ✗ |

**No model passed.** Best result: claude-opus-5. Don't rely on it without review.

## Detail

### claude-haiku-4-5 · US-1 · run 1

Coverage 62% · 9 test cases (8 derived) · $0.0090 · 12.8s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-003 |
| TC-LOGIN-003 invalid username | TC-LOGIN-002 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-005 |
| TC-LOGIN-005 password masking | TC-LOGIN-008 |
| TC-LOGIN-006 locked-out user | **missing** |
| TC-LOGIN-007 no access without login | **missing** |
| TC-LOGIN-008 SQL injection | **missing** |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-004 (derived, negative): Display error message when both credentials are invalid
- TC-LOGIN-006 (derived, required-field): Display error message when password field is empty
- TC-LOGIN-007 (derived, required-field): Display error message when both fields are empty
- TC-LOGIN-009 (derived, positive): Log in as a different user account

Grounding issues (values not in the story or the example shown):

- grounding: test data username = `problem_user` is not in the story or the examples

### claude-haiku-4-5 · US-1 · run 2

Coverage 62% · 8 test cases (7 derived) · $0.0085 · 7.7s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-003 |
| TC-LOGIN-003 invalid username | TC-LOGIN-002 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-004 |
| TC-LOGIN-005 password masking | **missing** |
| TC-LOGIN-006 locked-out user | TC-LOGIN-008 |
| TC-LOGIN-007 no access without login | **missing** |
| TC-LOGIN-008 SQL injection | **missing** |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-005 (derived, required-field): Reject login with missing password
- TC-LOGIN-006 (derived, required-field): Reject login with both username and password missing
- TC-LOGIN-007 (derived, ui): Clear username field without affecting password

Grounding issues (values not in the story or the example shown):

- grounding: test data username = `locked_out_user` is not in the story or the examples

### claude-haiku-4-5 · US-2 · run 1

Coverage 60% · 8 test cases (7 derived) · $0.0094 · 9.7s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | **missing** |
| TC-CART-002 add multiple products | TC-CART-002 |
| TC-CART-003 product details in cart | TC-CART-008 |
| TC-CART-004 remove product | **missing** |
| TC-CART-005 persists after navigating | TC-CART-006 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-001 (stated, positive): Add a product to the shopping cart
- TC-CART-003 (derived, positive): Add the same product to the shopping cart multiple times
- TC-CART-004 (derived, ui): Verify Add to Cart button changes after adding a product
- TC-CART-005 (derived, permission): Prevent adding a product to cart when not logged in
- TC-CART-007 (derived, navigation): Add a product to cart and view cart contents

### claude-haiku-4-5 · US-2 · run 2

Coverage 80% · 9 test cases (8 derived) · $0.0103 · 10.4s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-004 |
| TC-CART-002 add multiple products | TC-CART-002 |
| TC-CART-003 product details in cart | **missing** |
| TC-CART-004 remove product | TC-CART-003 |
| TC-CART-005 persists after navigating | TC-CART-007 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-001 (stated, positive): Add a product to the shopping cart
- TC-CART-005 (derived, permission): Prevent adding a product when not logged in
- TC-CART-006 (derived, positive): Add the same product to cart multiple times
- TC-CART-008 (derived, boundary): Add a product with special characters or edge case names
- TC-CART-009 (derived, ui): Verify Add to Cart button is only available on the Products page

### claude-sonnet-5 · US-1 · run 1

Coverage 88% · 11 test cases (10 derived) · $0.0353 · 21.0s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-002 |
| TC-LOGIN-003 invalid username | TC-LOGIN-003 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-005 |
| TC-LOGIN-005 password masking | TC-LOGIN-010 |
| TC-LOGIN-006 locked-out user | TC-LOGIN-008 |
| TC-LOGIN-007 no access without login | **missing** |
| TC-LOGIN-008 SQL injection | TC-LOGIN-009 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-004 (derived, negative): Reject login with both invalid username and password
- TC-LOGIN-006 (derived, required-field): Reject login attempt with empty password field
- TC-LOGIN-007 (derived, required-field): Reject login attempt with both fields empty
- TC-LOGIN-011 (derived, boundary): Reject login with excessively long username input

Grounding issues (values not in the story or the example shown):

- grounding: test data username = `locked_out_user` is not in the story or the examples
- grounding: test data username = `' OR '1'='1` is not in the story or the examples
- grounding: test data password = `' OR '1'='1` is not in the story or the examples

### claude-sonnet-5 · US-1 · run 2

Coverage 88% · 12 test cases (11 derived) · $0.0348 · 26.3s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-003 |
| TC-LOGIN-003 invalid username | TC-LOGIN-002 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-005 |
| TC-LOGIN-005 password masking | TC-LOGIN-012 |
| TC-LOGIN-006 locked-out user | TC-LOGIN-008 |
| TC-LOGIN-007 no access without login | **missing** |
| TC-LOGIN-008 SQL injection | TC-LOGIN-009 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-004 (derived, negative): Reject login with both invalid username and password
- TC-LOGIN-006 (derived, required-field): Reject login with empty password field
- TC-LOGIN-007 (derived, required-field): Reject login with both username and password fields empty
- TC-LOGIN-010 (derived, boundary): Reject login attempt with excessively long username input
- TC-LOGIN-011 (derived, ui): Verify presence and labeling of login page elements

Grounding issues (values not in the story or the example shown):

- grounding: test data username = `locked_out_user` is not in the story or the examples
- grounding: test data username = `' OR '1'='1` is not in the story or the examples

### claude-sonnet-5 · US-2 · run 1

Coverage 100% · 8 test cases (6 derived) · $0.0366 · 21.5s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-001 |
| TC-CART-002 add multiple products | TC-CART-002 |
| TC-CART-003 product details in cart | TC-CART-005 |
| TC-CART-004 remove product | TC-CART-001 |
| TC-CART-005 persists after navigating | TC-CART-004 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-003 (stated, positive): Verify cart contents match the products added
- TC-CART-006 (derived, positive): Add a product to the cart directly from the product details page
- TC-CART-007 (derived, permission): Prevent unauthenticated users from adding products to the cart
- TC-CART-008 (derived, ui): Verify cart badge does not display when cart is empty

Grounding issues (values not in the story or the example shown):

- grounding: step uses `Add to cart`, which is not in the story or the examples
- grounding: step uses `Remove`, which is not in the story or the examples
- grounding: step uses `Add to cart`, which is not in the story or the examples
- grounding: step uses `Add to cart`, which is not in the story or the examples
- grounding: step uses `Add to cart`, which is not in the story or the examples
- grounding: step uses `Remove`, which is not in the story or the examples
- grounding: step uses `Add to cart`, which is not in the story or the examples
- grounding: step uses `Remove`, which is not in the story or the examples
- grounding: step uses `Add to cart`, which is not in the story or the examples

### claude-sonnet-5 · US-2 · run 2

Coverage 100% · 7 test cases (6 derived) · $0.0303 · 26.1s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-001 |
| TC-CART-002 add multiple products | TC-CART-002 |
| TC-CART-003 product details in cart | TC-CART-005 |
| TC-CART-004 remove product | TC-CART-001 |
| TC-CART-005 persists after navigating | TC-CART-006 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-003 (derived, state-transition): Remove a product from the cart using the Remove button on the Products page
- TC-CART-004 (derived, navigation): Add a product to the cart from the product detail page
- TC-CART-007 (derived, boundary): Verify cart icon badge is absent when the cart is empty

Grounding issues (values not in the story or the example shown):

- grounding: test data product = `Sauce Labs Backpack` is not in the story or the examples
- grounding: step uses `Add to cart`, which is not in the story or the examples
- grounding: step uses `Remove`, which is not in the story or the examples
- grounding: test data product1 = `Sauce Labs Backpack` is not in the story or the examples
- grounding: test data product2 = `Sauce Labs Bike Light` is not in the story or the examples
- grounding: step uses `Add to cart`, which is not in the story or the examples
- grounding: test data product = `Sauce Labs Backpack` is not in the story or the examples
- grounding: step uses `Remove`, which is not in the story or the examples
- grounding: step uses `Add to cart`, which is not in the story or the examples
- grounding: test data product = `Sauce Labs Backpack` is not in the story or the examples
- grounding: step uses `Add to cart`, which is not in the story or the examples
- grounding: step uses `Remove`, which is not in the story or the examples
- grounding: test data product = `Sauce Labs Backpack` is not in the story or the examples
- grounding: test data product = `Sauce Labs Backpack` is not in the story or the examples
- grounding: step uses `Remove`, which is not in the story or the examples

### claude-opus-5 · US-1 · run 1

Coverage 88% · 12 test cases (11 derived) · $0.1008 · 31.4s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-002 |
| TC-LOGIN-003 invalid username | TC-LOGIN-003 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-004 |
| TC-LOGIN-005 password masking | TC-LOGIN-009 |
| TC-LOGIN-006 locked-out user | **missing** |
| TC-LOGIN-007 no access without login | TC-LOGIN-011 |
| TC-LOGIN-008 SQL injection | TC-LOGIN-010 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-005 (derived, required-field): Reject login when the password field is left empty
- TC-LOGIN-006 (derived, required-field): Reject login when both fields are left empty
- TC-LOGIN-007 (derived, negative): Treat credentials as case-sensitive
- TC-LOGIN-008 (derived, boundary): Reject login when credentials are padded with leading and trailing spaces
- TC-LOGIN-012 (derived, state-transition): Prevent returning to an authenticated page with the browser back button after logout

Grounding issues (values not in the story or the example shown):

- grounding: test data username = `STANDARD_USER` is not in the story or the examples
- grounding: test data password = `SECRET_SAUCE` is not in the story or the examples
- grounding: test data username = `' OR '1'='1` is not in the story or the examples
- grounding: test data password = `' OR '1'='1` is not in the story or the examples
- grounding: test data protected URL = `https://www.saucedemo.com/inventory.html` is not in the story or the examples
- grounding: URL https://www.saucedemo.com/inventory.html is not in the story or the examples

### claude-opus-5 · US-1 · run 2

Coverage 100% · 12 test cases (11 derived) · $0.0766 · 28.5s

| Reference test case | Reproduced by |
|---|---|
| TC-LOGIN-001 valid credentials | TC-LOGIN-001 |
| TC-LOGIN-002 invalid password | TC-LOGIN-002 |
| TC-LOGIN-003 invalid username | TC-LOGIN-003 |
| TC-LOGIN-004 empty credentials | TC-LOGIN-004 |
| TC-LOGIN-005 password masking | TC-LOGIN-008 |
| TC-LOGIN-006 locked-out user | TC-LOGIN-011 |
| TC-LOGIN-007 no access without login | TC-LOGIN-011 |
| TC-LOGIN-008 SQL injection | TC-LOGIN-009 |

Beyond the reference (check these are sensible, not invented):

- TC-LOGIN-005 (derived, required-field): Reject login when the password field is left empty
- TC-LOGIN-006 (derived, required-field): Reject login when both fields are left empty
- TC-LOGIN-007 (derived, negative): Verify credentials are treated as case sensitive
- TC-LOGIN-010 (derived, security): Verify script input in the login fields is not executed
- TC-LOGIN-012 (derived, state-transition): Verify the user can log out after a successful login

Grounding issues (values not in the story or the example shown):

- grounding: test data username = `STANDARD_USER` is not in the story or the examples
- grounding: test data password = `SECRET_SAUCE` is not in the story or the examples
- grounding: test data username = `' OR '1'='1` is not in the story or the examples
- grounding: test data password = `' OR '1'='1` is not in the story or the examples
- grounding: test data username = `<script>alert(1)</script>` is not in the story or the examples
- grounding: test data password = `<script>alert(1)</script>` is not in the story or the examples

### claude-opus-5 · US-2 · run 1

Coverage 100% · 10 test cases (8 derived) · $0.0976 · 27.6s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-001 |
| TC-CART-002 add multiple products | TC-CART-003 |
| TC-CART-003 product details in cart | TC-CART-002 |
| TC-CART-004 remove product | TC-CART-005 |
| TC-CART-005 persists after navigating | TC-CART-005 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-004 (derived, positive): Add a product from the product detail page
- TC-CART-006 (derived, state-transition): Cart contents persist while browsing back to the Products page
- TC-CART-007 (derived, state-transition): Cart contents persist after a page refresh
- TC-CART-008 (derived, permission): Prevent access to the cart page without being logged in
- TC-CART-009 (derived, boundary): Cart is empty for a newly logged-in session with no products added
- TC-CART-010 (derived, negative): Add a product using an account known to have degraded behaviour

Grounding issues (values not in the story or the example shown):

- grounding: test data username = `problem_user` is not in the story or the examples

### claude-opus-5 · US-2 · run 2

Coverage 100% · 8 test cases (6 derived) · $0.0693 · 26.5s

| Reference test case | Reproduced by |
|---|---|
| TC-CART-001 add single product | TC-CART-002 |
| TC-CART-002 add multiple products | TC-CART-004 |
| TC-CART-003 product details in cart | TC-CART-002 |
| TC-CART-004 remove product | TC-CART-001 |
| TC-CART-005 persists after navigating | TC-CART-006 |

Beyond the reference (check these are sensible, not invented):

- TC-CART-003 (derived, positive): Add a product to the cart from the product detail page
- TC-CART-005 (derived, state-transition): Remove a previously added product from the Products page
- TC-CART-007 (derived, ui): Cart badge is not displayed when the cart is empty
- TC-CART-008 (derived, permission): Prevent access to the cart page without being logged in

Grounding issues (values not in the story or the example shown):

- grounding: test data url = `https://www.saucedemo.com/cart.html` is not in the story or the examples
- grounding: URL https://www.saucedemo.com/cart.html is not in the story or the examples

## Limits of this evaluation

- Two stories on one site. It shows which model is adequate on your own examples, not in general.
- Coverage is judged by keyword rules (`REFERENCE` in `tcgen/evaluate.py`). The per-run tables show exactly which case matched which reference, so a misjudged match can be checked.
- A test case beyond the reference isn't automatically good or bad; it needs a person to judge whether it follows from the story.
- Prices are list prices per million tokens as configured in `tcgen/llm.py`.
