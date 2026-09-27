# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:10
- **Model:** claude-sonnet-5
- **Stories:** 1 · **Test cases:** 8
- **Status:** every test case is Draft until a QA engineer reviews it

## US-2 — Add Product to Cart

> As a logged-in user
> I want to add a product to my shopping cart
> So that I can purchase the selected product.

| Test ID | Source | Objective | Preconditions | Steps | Test Data | Expected Result | Risk | Priority | Evidence Requirements | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-CART-001 | US-2 · stated (positive) | Add a single product to the cart | User is logged in with a valid account<br>User is on the Products page | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for `<product name>`<br>3. Verify the cart icon badge shows a count of `1`<br>4. Click the cart icon<br>5. Verify `<product name>` appears in the cart | product name = `<product name>` | The selected product is added to the cart and the cart badge reflects the correct count | Critical | P1 | Screenshot of the cart badge showing the count<br>Screenshot of the cart page listing the product | Draft |
| TC-CART-002 | US-2 · derived (state-transition) | Add-to-cart button changes to Remove after adding a product | User is logged in with a valid account<br>User is on the Products page<br>`<product name>` has not been added to the cart | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for `<product name>`<br>3. Verify the button for `<product name>` now reads `Remove` | product name = `<product name>` | After adding the product, its button label changes from `Add to cart` to `Remove` | Medium | P2 | Screenshot of the button showing `Remove` | Draft |
| TC-CART-003 | US-2 · derived (positive) | Add multiple different products to the cart | User is logged in with a valid account<br>User is on the Products page | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for `<product name 1>`<br>3. Click the `Add to cart` button for `<product name 2>`<br>4. Verify the cart icon badge shows a count of `2`<br>5. Click the cart icon<br>6. Verify both `<product name 1>` and `<product name 2>` appear in the cart | product name 1 = `<product name 1>`<br>product name 2 = `<product name 2>` | Both products are added to the cart and the cart badge count matches the number of items added | High | P1 | Screenshot of the cart badge showing the count<br>Screenshot of the cart page listing both products | Draft |
| TC-CART-004 | US-2 · derived (boundary) | Add all available products to the cart | User is logged in with a valid account<br>User is on the Products page<br>No products are currently in the cart | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for every product listed on the page<br>3. Verify the cart icon badge shows a count equal to the total number of products on the page<br>4. Click the cart icon<br>5. Verify every product appears in the cart | — | All products on the page are added to the cart and the cart badge count equals the total number of products | Medium | P2 | Screenshot of the cart badge showing the total count<br>Screenshot of the cart page listing all products | Draft |
| TC-CART-005 | US-2 · derived (state-transition) | Remove a product from the cart after adding it | User is logged in with a valid account<br>`<product name>` has already been added to the cart | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Remove` button for `<product name>`<br>3. Verify the cart icon badge count decreases by `1`<br>4. Click the cart icon<br>5. Verify `<product name>` no longer appears in the cart | product name = `<product name>` | The product is removed from the cart and the cart badge count updates accordingly | High | P2 | Screenshot of the updated cart badge<br>Screenshot of the cart page confirming the product is absent | Draft |
| TC-CART-006 | US-2 · derived (ui) | Cart badge does not display when the cart is empty | User is logged in with a valid account<br>No products have been added to the cart | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Verify the cart icon does not show a badge or shows a count of `0` | — | The cart icon shows no badge or a zero count when the cart is empty | Low | P3 | Screenshot of the cart icon with no items in the cart | Draft |
| TC-CART-007 | US-2 · derived (permission) | Prevent adding a product to the cart without being logged in | User is not logged in | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Verify the Products page is not displayed<br>3. Verify the user is redirected to the login page or access is denied | url = `https://www.saucedemo.com/inventory.html` | User cannot access the Products page or add items to the cart without logging in | Critical | P1 | Screenshot of the resulting page<br>Final page URL | Draft |
| TC-CART-008 | US-2 · derived (state-transition) | Cart contents persist after navigating away and back to the Products page | User is logged in with a valid account<br>`<product name>` has been added to the cart | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the `Add to cart` button for `<product name>`<br>3. Click the cart icon to view the cart<br>4. Navigate back to the Products page<br>5. Verify the cart icon badge still shows a count of `1` | product name = `<product name>` | The added product remains in the cart after navigating between pages | Medium | P3 | Screenshot of the cart badge after navigation | Draft |

**Check before running**

- TC-CART-001 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-002 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-002 — grounding: step uses `Remove`, which is not in the story or the examples
- TC-CART-003 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-004 — grounding: step uses `Add to cart`, which is not in the story or the examples
- TC-CART-005 — grounding: step uses `Remove`, which is not in the story or the examples
- TC-CART-008 — grounding: step uses `Add to cart`, which is not in the story or the examples
