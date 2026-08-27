# ShopFront - Release 4.2 User Stories

## US-001 Account Login
As a Registered User, I want to log in with my email and password so that I can access my account.

Acceptance Criteria:
- Given a registered account, when the user submits a correct email and password, then the user is taken to the dashboard.
- Given a registered account, when the user submits an incorrect password three times in a row, then the account is locked for 15 minutes and a lockout message is shown.
- When the user submits an unregistered email, then a generic "invalid credentials" message is shown and the email is not disclosed as unknown.

## US-002 Password Reset
As a Registered User, I want to reset a forgotten password so that I can regain access.

Acceptance Criteria:
- Given a valid reset link, when the user submits a new password of at least 12 characters, then the password is updated and the user is signed out of all other sessions.
- Given a reset link older than 30 minutes, when the user opens it, then the link is rejected as expired.
- The system should handle reset failures appropriately.

## US-003 Basket Checkout
As a Customer, I want to pay for the items in my basket so that my order is confirmed.

Acceptance Criteria:
- Given a basket with at least one item, when the customer submits without a billing address, then submission is blocked with a field-level validation message.
- Given a valid card, when payment is authorised, then an order confirmation page is displayed with the order number.
- When the card is declined, then an error is shown and the basket contents are preserved.

## US-004 Role-Based Admin Access
As an Administrator, I want admin pages restricted to admin accounts so that customer data stays protected.

Acceptance Criteria:
- Given a standard-role user, when they navigate directly to /admin, then they are redirected to an access-denied page.
- Given an admin-role user, when they navigate to /admin, then the admin dashboard is displayed.

## US-005 Order History Export
As a Customer, I want to export my order history so that I can keep my own records.

Acceptance Criteria:
- Given at least one past order, when the customer requests a CSV export, then a file containing all their orders is downloaded.
- The export must not contain orders belonging to other customers.

## US-006 Search Results
As a Guest User, I want to search the catalogue so that I can find products quickly.

Acceptance Criteria:
- When a search term matches no products, then an empty-state message with suggested categories is shown.
- Search should be fast and user-friendly, returning appropriate results.

## US-007 Notification Preferences
As a Registered User, I want to control which emails I receive so that I am not spammed.

## US-008 Session Handling
Sessions are a recurring source of support tickets in the current release. When a customer leaves a tab
open overnight and returns, the application sometimes keeps them signed in well past the intended
window, and in other cases signs them out in the middle of checkout with no warning and no way to
recover the basket they had assembled. Support has also reported that signing out on one device does
not reliably end sessions elsewhere, which matters for shared machines in the store branches.
