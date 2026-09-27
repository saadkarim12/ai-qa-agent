# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:02
- **Model:** claude-haiku-4-5
- **Stories:** 1 · **Test cases:** 9
- **Status:** every test case is Draft until a QA engineer reviews it

## US-2 — Add Product to Cart

> As a logged-in user
> I want to add a product to my shopping cart
> So that I can purchase the selected product.

| Test ID | Source | Objective | Preconditions | Steps | Test Data | Expected Result | Risk | Priority | Evidence Requirements | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-CART-001 | US-2 · stated (positive) | Add a product to the shopping cart | User is logged in<br>User is on the Products page | 1. Click the Add to Cart button for a product<br>2. Verify the product is added to the shopping cart<br>3. Verify the cart counter displays the correct number | product = `<any product on the Products page>` | Product is successfully added to the shopping cart and the cart counter increments | Critical | P1 | Screenshot of the product added to cart<br>Screenshot of the cart counter | Draft |
| TC-CART-002 | US-2 · derived (positive) | Add multiple products to the shopping cart | User is logged in<br>User is on the Products page | 1. Click the Add to Cart button for the first product<br>2. Verify the first product is added<br>3. Click the Add to Cart button for a second product<br>4. Verify the second product is added<br>5. Verify the cart counter displays 2 | product_1 = `<first product>`<br>product_2 = `<second product>` | Both products are added to the cart and the counter shows the correct total | High | P2 | Screenshot of the cart counter showing 2 items | Draft |
| TC-CART-003 | US-2 · derived (state-transition) | Change Add to Cart button to Remove from Cart after adding a product | User is logged in<br>User is on the Products page | 1. Click the Add to Cart button for a product<br>2. Verify the button text changes to Remove from Cart | product = `<any product>` | The button label changes from Add to Cart to Remove from Cart | Medium | P2 | Screenshot of the button after adding the product | Draft |
| TC-CART-004 | US-2 · derived (navigation) | Access the shopping cart after adding a product | User is logged in<br>At least one product is in the shopping cart | 1. Click the shopping cart icon or cart counter<br>2. Verify the shopping cart page opens<br>3. Verify the added product is displayed in the cart | product = `<product in cart>` | Shopping cart page opens and displays the added product | High | P2 | Screenshot of the shopping cart page<br>URL of the cart page | Draft |
| TC-CART-005 | US-2 · derived (permission) | Prevent adding a product when not logged in | User is not logged in | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Verify the user is not on the Products page | url = `https://www.saucedemo.com/inventory.html` | User cannot access the Products page without logging in | Critical | P1 | Screenshot showing redirect to login page | Draft |
| TC-CART-006 | US-2 · derived (positive) | Add the same product to cart multiple times | User is logged in<br>User is on the Products page | 1. Click the Add to Cart button for a product<br>2. Click the Add to Cart button for the same product again<br>3. Verify the cart counter displays 2<br>4. Navigate to the shopping cart<br>5. Verify the product quantity reflects multiple additions or the product appears multiple times | product = `<any product>` | The same product can be added multiple times and the cart reflects the correct quantity | High | P2 | Screenshot of the cart counter showing 2<br>Screenshot of the shopping cart contents | Draft |
| TC-CART-007 | US-2 · derived (state-transition) | Verify cart persists after adding a product and navigating away | User is logged in<br>A product is in the shopping cart | 1. Add a product to the cart<br>2. Navigate away from the Products page<br>3. Return to the Products page<br>4. Verify the cart counter still shows the added product | product = `<any product>` | The cart persists and the product remains in the cart | High | P2 | Screenshot of the cart counter on return | Draft |
| TC-CART-008 | US-2 · derived (boundary) | Add a product with special characters or edge case names | User is logged in<br>User is on the Products page | 1. Identify a product with a long name or special characters<br>2. Click the Add to Cart button for that product<br>3. Verify the product is added successfully<br>4. Navigate to the shopping cart<br>5. Verify the product displays correctly | product = `<product with edge case name>` | Product with special characters or long names is added and displays correctly in the cart | Low | P3 | Screenshot of the product in the cart | Draft |
| TC-CART-009 | US-2 · derived (ui) | Verify Add to Cart button is only available on the Products page | User is logged in | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Verify Add to Cart buttons are visible and functional<br>3. Navigate to the shopping cart page<br>4. Verify Add to Cart buttons are not present | products_url = `https://www.saucedemo.com/inventory.html` | Add to Cart buttons are available on the Products page and not on the cart page | Low | P3 | Screenshot of the Products page<br>Screenshot of the cart page | Draft |

**Check before running**

- TC-CART-007 — format: step 1 starts with 'Add', not a recognised action verb
- TC-CART-007 — format: step 3 starts with 'Return', not a recognised action verb
- TC-CART-008 — format: step 1 starts with 'Identify', not a recognised action verb
