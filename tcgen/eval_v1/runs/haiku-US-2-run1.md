# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:02
- **Model:** claude-haiku-4-5
- **Stories:** 1 · **Test cases:** 8
- **Status:** every test case is Draft until a QA engineer reviews it

## US-2 — Add Product to Cart

> As a logged-in user
> I want to add a product to my shopping cart
> So that I can purchase the selected product.

| Test ID | Source | Objective | Preconditions | Steps | Test Data | Expected Result | Risk | Priority | Evidence Requirements | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-CART-001 | US-2 · stated (positive) | Add a product to the shopping cart | User is logged in<br>User is on the Products page | 1. Click the Add to Cart button for a product<br>2. Verify the product is added to the shopping cart<br>3. Verify the cart badge displays the updated item count | product = `<any available product>` | Product is successfully added to the shopping cart and cart count is incremented | Critical | P1 | Screenshot of the product after clicking Add to Cart<br>Screenshot of the updated cart badge<br>Current cart item count | Draft |
| TC-CART-002 | US-2 · derived (positive) | Add multiple different products to the shopping cart | User is logged in<br>User is on the Products page | 1. Click the Add to Cart button for the first product<br>2. Click the Add to Cart button for a second product<br>3. Verify both products are in the shopping cart<br>4. Verify the cart badge displays the correct total item count | product_1 = `<first available product>`<br>product_2 = `<second available product>` | Both products are successfully added to the cart with the correct total count | High | P2 | Screenshot of the cart page showing both products<br>Cart badge displaying total count | Draft |
| TC-CART-003 | US-2 · derived (positive) | Add the same product to the shopping cart multiple times | User is logged in<br>User is on the Products page | 1. Click the Add to Cart button for a product<br>2. Click the Add to Cart button for the same product again<br>3. Verify the product appears in the shopping cart with the correct quantity | product = `<any available product>` | Product quantity is incremented correctly in the cart | High | P2 | Screenshot of the cart showing product quantity | Draft |
| TC-CART-004 | US-2 · derived (ui) | Verify Add to Cart button changes after adding a product | User is logged in<br>User is on the Products page | 1. Locate the Add to Cart button for a product<br>2. Click the Add to Cart button<br>3. Verify the button text or state changes to indicate the product is in the cart | product = `<any available product>` | The Add to Cart button changes state or label to reflect that the product is in the cart | Medium | P3 | Screenshot of the button before and after clicking | Draft |
| TC-CART-005 | US-2 · derived (permission) | Prevent adding a product to cart when not logged in | User is not logged in | 1. Navigate to https://www.saucedemo.com/<br>2. Verify the Products page is not accessible<br>3. Verify the user cannot interact with Add to Cart buttons | — | User is redirected to login page and cannot add products to cart | Critical | P1 | Screenshot of the resulting page<br>Final page URL | Draft |
| TC-CART-006 | US-2 · derived (state-transition) | Maintain cart contents after navigating away and returning | User is logged in<br>User has added products to the cart | 1. Add a product to the cart<br>2. Navigate away from the Products page<br>3. Return to the Products page<br>4. Verify the product remains in the shopping cart | product = `<any available product>` | Cart contents are preserved during navigation | High | P2 | Screenshot of cart before navigation<br>Screenshot of cart after returning | Draft |
| TC-CART-007 | US-2 · derived (navigation) | Add a product to cart and view cart contents | User is logged in<br>User is on the Products page | 1. Click the Add to Cart button for a product<br>2. Click the shopping cart icon or link<br>3. Verify the product is displayed in the cart page | product = `<any available product>` | User can navigate to the cart and see the added product | High | P2 | Screenshot of the cart page<br>Product name and details visible | Draft |
| TC-CART-008 | US-2 · derived (ui) | Display product price and details when added to cart | User is logged in<br>User is on the Products page | 1. Add a product to the cart<br>2. Click the shopping cart icon or link<br>3. Verify the product name, price, and quantity are displayed in the cart | product = `<any available product>` | Product information is correctly displayed in the cart | Medium | P3 | Screenshot of the cart showing product details | Draft |

**Check before running**

- TC-CART-004 — format: step 1 starts with 'Locate', not a recognised action verb
- TC-CART-006 — format: step 1 starts with 'Add', not a recognised action verb
- TC-CART-006 — format: step 3 starts with 'Return', not a recognised action verb
- TC-CART-008 — format: step 1 starts with 'Add', not a recognised action verb
