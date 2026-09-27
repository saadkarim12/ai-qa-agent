# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:08
- **Model:** claude-haiku-4-5
- **Stories:** 1 · **Test cases:** 8
- **Status:** every test case is Draft until a QA engineer reviews it

## US-2 — Add Product to Cart

> As a logged-in user
> I want to add a product to my shopping cart
> So that I can purchase the selected product.

| Test ID | Source | Objective | Preconditions | Steps | Test Data | Expected Result | Risk | Priority | Evidence Requirements | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-CART-001 | US-2 · stated (positive) | Add a product to the shopping cart | User is logged in<br>User is on the Products page | 1. Click the button that adds the first product to the cart<br>2. Verify the product is added to the shopping cart<br>3. Verify the cart counter increments | product = `<first product on the page>` | Product is successfully added to the cart and the cart counter updates | Critical | P1 | Screenshot of the cart counter showing the updated count<br>Screenshot of the cart contents showing the added product | Draft |
| TC-CART-002 | US-2 · derived (positive) | Add multiple different products to the shopping cart | User is logged in<br>User is on the Products page | 1. Click the button that adds the first product to the cart<br>2. Click the button that adds the second product to the cart<br>3. Click the button that adds the third product to the cart<br>4. Verify all three products are in the shopping cart<br>5. Verify the cart counter shows 3 | product_1 = `<first product>`<br>product_2 = `<second product>`<br>product_3 = `<third product>` | All three products are successfully added to the cart with the correct count | High | P1 | Screenshot of the cart contents showing all three products<br>Screenshot of the cart counter showing 3 | Draft |
| TC-CART-003 | US-2 · derived (boundary) | Add the same product to the cart multiple times | User is logged in<br>User is on the Products page | 1. Click the button that adds the first product to the cart<br>2. Click the button that adds the first product to the cart again<br>3. Verify the first product is in the cart<br>4. Verify the cart counter shows 2 | product = `<first product>` | The same product is added multiple times and the cart counter reflects the total quantity | High | P2 | Screenshot of the cart contents showing the product with quantity 2<br>Screenshot of the cart counter | Draft |
| TC-CART-004 | US-2 · derived (ui) | Display the add-to-cart button in the correct state for each product | User is logged in<br>User is on the Products page | 1. Verify each product displays an add-to-cart button<br>2. Click the button that adds the first product to the cart<br>3. Verify the button changes to a remove or different state for the first product<br>4. Verify the add-to-cart button remains available for other products | product = `<first product>` | The add-to-cart button changes state for the added product while remaining available for other products | Medium | P2 | Screenshot of the button state before adding a product<br>Screenshot of the button state after adding a product | Draft |
| TC-CART-005 | US-2 · derived (permission) | Require login to add products to the cart | User is not logged in | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Verify the Products page is not accessible or the user is redirected to login | url = `https://www.saucedemo.com/inventory.html` | User cannot access the Products page without logging in first | Critical | P1 | Screenshot of the resulting page<br>Final page URL | Draft |
| TC-CART-006 | US-2 · derived (state-transition) | Preserve cart contents when navigating away from the Products page | User is logged in<br>User has added products to the cart | 1. Click the button that adds a product to the cart<br>2. Navigate to a different page or section<br>3. Return to the Products page<br>4. Verify the product remains in the cart | product = `<any product>` | Cart contents are preserved after navigation | High | P2 | Screenshot of the cart before navigation<br>Screenshot of the cart after returning to the Products page | Draft |
| TC-CART-007 | US-2 · derived (ui) | Display feedback when a product is added to the cart | User is logged in<br>User is on the Products page | 1. Click the button that adds a product to the cart<br>2. Verify visual or textual feedback is displayed | product = `<any product>` | Appropriate feedback is displayed confirming the product was added to the cart | Low | P3 | Screenshot showing the feedback message or visual indicator | Draft |
| TC-CART-008 | US-2 · derived (boundary) | Handle adding a product when the cart is already at capacity | User is logged in<br>The shopping cart has a defined maximum capacity | 1. Add products to the cart until it reaches maximum capacity<br>2. Attempt to add another product<br>3. Verify the application handles this state appropriately | max_items = `<maximum cart capacity>` | The application either prevents adding beyond capacity or displays an appropriate message | Medium | P3 | Screenshot of the cart state at maximum capacity<br>Screenshot of any error or warning message | Draft |

**Check before running**

- TC-CART-006 — format: step 3 starts with 'Return', not a recognised action verb
- TC-CART-008 — format: step 1 starts with 'Add', not a recognised action verb
- TC-CART-008 — format: step 2 starts with 'Attempt', not a recognised action verb
