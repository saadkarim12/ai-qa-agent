# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:08
- **Model:** claude-haiku-4-5
- **Stories:** 1 · **Test cases:** 7
- **Status:** every test case is Draft until a QA engineer reviews it

## US-2 — Add Product to Cart

> As a logged-in user
> I want to add a product to my shopping cart
> So that I can purchase the selected product.

| Test ID | Source | Objective | Preconditions | Steps | Test Data | Expected Result | Risk | Priority | Evidence Requirements | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-CART-001 | US-2 · stated (positive) | Add a product to the shopping cart from the Products page | User is logged in<br>User is on the Products page | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the Add to Cart button for a product<br>3. Verify the product is added to the shopping cart | url = `https://www.saucedemo.com/inventory.html` | Product is successfully added to the shopping cart | Critical | P1 | Screenshot showing the product in the cart<br>Cart count or cart page contents | Draft |
| TC-CART-002 | US-2 · derived (ui) | Update the cart count when a product is added | User is logged in<br>User is on the Products page<br>Shopping cart is empty or has items | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Note the current cart count<br>3. Click the Add to Cart button for a product<br>4. Verify the cart count increases by one | url = `https://www.saucedemo.com/inventory.html` | Cart count increments by one after adding a product | Medium | P2 | Screenshot of the cart count before and after adding the product | Draft |
| TC-CART-003 | US-2 · derived (ui) | Change the Add to Cart button to a Remove button after adding a product | User is logged in<br>User is on the Products page | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the Add to Cart button for a product<br>3. Verify the button changes to a Remove button for that product | url = `https://www.saucedemo.com/inventory.html` | The Add to Cart button changes to a Remove button for the added product | Low | P2 | Screenshot of the button after adding the product | Draft |
| TC-CART-004 | US-2 · derived (positive) | Add multiple different products to the cart | User is logged in<br>User is on the Products page | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the Add to Cart button for the first product<br>3. Click the Add to Cart button for a second product<br>4. Click the Add to Cart button for a third product<br>5. Verify all three products are in the shopping cart | url = `https://www.saucedemo.com/inventory.html` | All three products are successfully added to the shopping cart | High | P2 | Screenshot of the cart containing all three products<br>Cart count shows 3 | Draft |
| TC-CART-005 | US-2 · derived (boundary) | Add the same product multiple times to the cart | User is logged in<br>User is on the Products page | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the Add to Cart button for a product<br>3. Click the Add to Cart button for the same product again<br>4. Verify the product quantity increases or appears multiple times in the cart | url = `https://www.saucedemo.com/inventory.html` | The product is added to the cart multiple times or the quantity is updated | Medium | P3 | Screenshot of the cart showing the product quantity or multiple entries | Draft |
| TC-CART-006 | US-2 · derived (state-transition) | Persist cart contents after navigating away and returning | User is logged in<br>User has added a product to the cart | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Click the Add to Cart button for a product<br>3. Navigate to a different page<br>4. Navigate back to https://www.saucedemo.com/inventory.html<br>5. Verify the product remains in the shopping cart | url = `https://www.saucedemo.com/inventory.html` | Cart contents are preserved after navigating away and returning | High | P2 | Screenshot of the cart before navigating away<br>Screenshot of the cart after returning | Draft |
| TC-CART-007 | US-2 · derived (security) | Allow an unauthenticated user to attempt adding a product | User is not logged in | 1. Navigate to https://www.saucedemo.com/inventory.html<br>2. Verify the user is redirected to the login page or access is denied | url = `https://www.saucedemo.com/inventory.html` | Unauthenticated user cannot access the Products page to add products | Critical | P1 | Screenshot of the login page or access denied message<br>Final page URL | Draft |

**Check before running**

- TC-CART-002 — format: step 2 starts with 'Note', not a recognised action verb
