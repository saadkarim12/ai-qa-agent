# Checkout Behaviour Scenarios

## SCENARIO TC-301 Guest checkout with valid card
Given a guest user with one item in the basket
When the guest submits a valid card and a complete delivery address
Then the order is created and an order number is displayed

## SCENARIO TC-302 Expired card
Given a guest user at the payment step
When the guest submits a card with a past expiry date
Then the payment is rejected and an expiry error is displayed

## SCENARIO TC-303 Session expiry during checkout
Given a customer who has been idle for 20 minutes at the payment step
When the customer submits the payment form
Then the customer is returned to sign-in and the basket contents are preserved
