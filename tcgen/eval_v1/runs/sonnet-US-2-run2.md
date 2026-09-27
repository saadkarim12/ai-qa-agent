# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:03
- **Model:** claude-sonnet-5
- **Stories:** 1 · **Test cases:** 7
- **Status:** every test case is Draft until a QA engineer reviews it

## US-2 — Add Product to Cart

> As a logged-in user
> I want to add a product to my shopping cart
> So that I can purchase the selected product.

| Test ID | Source | Objective | Preconditions | Steps | Test Data | Expected Result | Risk | Priority | Evidence Requirements | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-CART-001 | US-2 · stated (positive) | Add a single product to the cart from the Products page | User is logged in as `standard_user`<br>User is on the Products page | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for `Sauce Labs Backpack`<br>3. Verify the button changes to `Remove`<br>4. Verify the cart icon shows a badge with count `1` | product = `Sauce Labs Backpack` | The selected product is added to the cart and the cart badge reflects the updated count | Critical | P1 | Screenshot of the Products page with the Remove button and cart badge | Draft |
| TC-CART-002 | US-2 · derived (positive) | Add multiple different products to the cart | User is logged in as `standard_user`<br>User is on the Products page<br>Cart is empty | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for `Sauce Labs Backpack`<br>3. Click the `Add to cart` button for `Sauce Labs Bike Light`<br>4. Verify the cart icon shows a badge with count `2`<br>5. Navigate to the cart page<br>6. Verify both products are listed in the cart | product1 = `Sauce Labs Backpack`<br>product2 = `Sauce Labs Bike Light` | Both products appear in the cart and the badge count matches the number of items added | High | P1 | Screenshot of the cart page listing both products<br>Screenshot of the badge count | Draft |
| TC-CART-003 | US-2 · derived (state-transition) | Remove a product from the cart using the Remove button on the Products page | User is logged in as `standard_user`<br>`Sauce Labs Backpack` has already been added to the cart | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Remove` button for `Sauce Labs Backpack`<br>3. Verify the button changes back to `Add to cart`<br>4. Verify the cart badge count decreases by one or disappears if cart is empty | product = `Sauce Labs Backpack` | The product is removed from the cart and the cart badge updates accordingly | High | P2 | Screenshot of the Products page showing the Add to cart button restored<br>Screenshot of the updated cart badge | Draft |
| TC-CART-004 | US-2 · derived (navigation) | Add a product to the cart from the product detail page | User is logged in as `standard_user`<br>User is on the Products page | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click on the product name `Sauce Labs Backpack` to open its detail page<br>3. Click the `Add to cart` button on the detail page<br>4. Verify the button changes to `Remove`<br>5. Verify the cart badge shows count `1` | product = `Sauce Labs Backpack` | The product is added to the cart from the detail page and the cart badge updates | Medium | P2 | Screenshot of the product detail page with the Remove button<br>Screenshot of the cart badge | Draft |
| TC-CART-005 | US-2 · derived (positive) | Verify the cart page displays correct product name, price and quantity after adding an item | User is logged in as `standard_user`<br>`Sauce Labs Backpack` has been added to the cart | 1. Navigate to the cart page<br>2. Verify the product name `Sauce Labs Backpack` is displayed<br>3. Verify the product price is displayed<br>4. Verify the quantity is `1` | product = `Sauce Labs Backpack`<br>quantity = `1` | The cart page accurately reflects the added product's name, price and quantity | High | P2 | Screenshot of the cart page with product details | Draft |
| TC-CART-006 | US-2 · derived (state-transition) | Verify the cart retains added products after navigating away and returning to the Products page | User is logged in as `standard_user`<br>`Sauce Labs Backpack` has been added to the cart | 1. Navigate to the cart page<br>2. Navigate back to the Products page<br>3. Verify the `Sauce Labs Backpack` button still shows `Remove`<br>4. Verify the cart badge still shows count `1` | product = `Sauce Labs Backpack` | The cart state persists across navigation within the session | Medium | P3 | Screenshot of the Products page after navigation showing persisted cart state | Draft |
| TC-CART-007 | US-2 · derived (boundary) | Verify cart icon badge is absent when the cart is empty | User is logged in as `standard_user`<br>Cart is empty | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Verify the cart icon does not display a badge or count | — | No badge/count is shown on the cart icon when there are no items in the cart | Low | P3 | Screenshot of the cart icon with no badge | Draft |

**Check before running**

- TC-CART-001 — grounding: test data product = `Sauce Labs Backpack` is not in the story or the examples
- TC-CART-001 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-001 — grounding: step uses `Remove`, which is not in the story or the examples
- TC-CART-002 — grounding: test data product1 = `Sauce Labs Backpack` is not in the story or the examples
- TC-CART-002 — grounding: test data product2 = `Sauce Labs Bike Light` is not in the story or the examples
- TC-CART-002 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-003 — grounding: test data product = `Sauce Labs Backpack` is not in the story or the examples
- TC-CART-003 — grounding: step uses `Remove`, which is not in the story or the examples
- TC-CART-003 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-004 — grounding: test data product = `Sauce Labs Backpack` is not in the story or the examples
- TC-CART-004 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-004 — grounding: step uses `Remove`, which is not in the story or the examples
- TC-CART-005 — grounding: test data product = `Sauce Labs Backpack` is not in the story or the examples
- TC-CART-006 — grounding: test data product = `Sauce Labs Backpack` is not in the story or the examples
- TC-CART-006 — grounding: step uses `Remove`, which is not in the story or the examples
