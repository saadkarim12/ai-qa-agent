# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:03
- **Model:** claude-sonnet-5
- **Stories:** 1 · **Test cases:** 8
- **Status:** every test case is Draft until a QA engineer reviews it

## US-2 — Add Product to Cart

> As a logged-in user
> I want to add a product to my shopping cart
> So that I can purchase the selected product.

| Test ID | Source | Objective | Preconditions | Steps | Test Data | Expected Result | Risk | Priority | Evidence Requirements | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-CART-001 | US-2 · stated (positive) | Add a single product to the cart from the products page | User is logged in with valid credentials<br>User is on the Products page | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for `<product name>`<br>3. Verify the cart icon shows a count of `1`<br>4. Verify the button for `<product name>` changes to `Remove` | product name = `<product name>` | The selected product is added to the cart and the cart icon reflects the updated count | Critical | P1 | Screenshot of the cart icon with count<br>Screenshot of the product row showing the Remove button | Draft |
| TC-CART-002 | US-2 · derived (positive) | Add multiple different products to the cart | User is logged in with valid credentials<br>User is on the Products page<br>Cart is empty | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for `<product name 1>`<br>3. Click the `Add to cart` button for `<product name 2>`<br>4. Verify the cart icon shows a count of `2` | product name 1 = `<product name 1>`<br>product name 2 = `<product name 2>` | Both selected products are added to the cart and the cart icon shows the correct total count | High | P1 | Screenshot of the cart icon with count<br>Screenshot of both product rows showing the Remove button | Draft |
| TC-CART-003 | US-2 · stated (positive) | Verify cart contents match the products added | User is logged in with valid credentials<br>User is on the Products page<br>At least one product has been added to the cart | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for `<product name>`<br>3. Click the cart icon<br>4. Verify the cart page displays `<product name>` | product name = `<product name>` | The cart page displays exactly the product(s) that were added | Critical | P1 | Screenshot of the cart page listing the added product | Draft |
| TC-CART-004 | US-2 · derived (boundary) | Verify cart count does not increase when the same product is added only once | User is logged in with valid credentials<br>User is on the Products page<br>Cart is empty | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for `<product name>`<br>3. Verify the cart icon shows a count of `1`<br>4. Verify the button label changes to `Remove` and no `Add to cart` button remains for that product | product name = `<product name>` | Adding a product only registers it once in the cart, preventing duplicate entries | Medium | P2 | Screenshot of the product row and cart icon count | Draft |
| TC-CART-005 | US-2 · derived (state-transition) | Verify cart contents persist after navigating to product details and back | User is logged in with valid credentials<br>User is on the Products page | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for `<product name>`<br>3. Click on `<product name>` to open its details page<br>4. Navigate back to the Products page<br>5. Verify the cart icon still shows a count of `1`<br>6. Verify the button for `<product name>` still shows `Remove` | product name = `<product name>` | The cart retains the added product across navigation within the application | Medium | P2 | Screenshot of the cart icon count after navigation<br>Screenshot of the product row showing Remove button | Draft |
| TC-CART-006 | US-2 · derived (positive) | Add a product to the cart directly from the product details page | User is logged in with valid credentials<br>User is on a product details page | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click on `<product name>` to open its details page<br>3. Click the `Add to cart` button on the details page<br>4. Verify the cart icon shows a count of `1` | product name = `<product name>` | The product is added to the cart from the details page and the cart icon updates accordingly | Medium | P2 | Screenshot of the details page with the Remove button<br>Screenshot of the cart icon with count | Draft |
| TC-CART-007 | US-2 · derived (permission) | Prevent unauthenticated users from adding products to the cart | User is not logged in | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Verify the user is redirected to the login page or access is denied | url = `https://www.saucedemo.com/inventory.html` | Unauthenticated users cannot access the Products page or add items to the cart | Critical | P1 | Screenshot of the resulting page<br>Final page URL | Draft |
| TC-CART-008 | US-2 · derived (ui) | Verify cart badge does not display when cart is empty | User is logged in with valid credentials<br>Cart is empty | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Verify the cart icon shows no count badge | — | The cart icon shows no badge/count when there are no items in the cart | Low | P3 | Screenshot of the cart icon with no badge | Draft |

**Check before running**

- TC-CART-001 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-001 — grounding: step uses `Remove`, which is not in the story or the examples
- TC-CART-002 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-003 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-004 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-004 — grounding: step uses `Remove`, which is not in the story or the examples
- TC-CART-005 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-005 — grounding: step uses `Remove`, which is not in the story or the examples
- TC-CART-006 — grounding: step uses `Add to cart`, which is not in the story or the examples
