# Orion Banking Portal — Release 7.1 User Stories

## US-101 Customer Login
As a Registered Customer, I want to sign in with my email and password so that I can view my accounts.

Acceptance Criteria:
- Given an active account, when the customer submits a correct email and password, then the accounts overview is displayed.
- Given an active account, when the customer submits an incorrect password five times, then the account is locked for 30 minutes and a lockout notice is displayed.
- When the customer submits an email that is not registered, then a generic "invalid credentials" message is shown and account existence is not disclosed.

## US-102 Funds Transfer
As a Registered Customer, I want to transfer funds between my accounts so that I can manage my balances.

Acceptance Criteria:
- Given two active accounts, when the customer transfers an amount within the available balance, then both balances are updated and a confirmation reference is displayed.
- Given a source account with insufficient funds, when the customer submits the transfer, then the transfer is rejected and no balance changes.
- When the transfer amount is zero or negative, then submission is blocked with a field-level validation message.

## US-103 Statement Download
As a Registered Customer, I want to download a statement so that I can keep my own records.

Acceptance Criteria:
- Given at least one transaction, when the customer requests a PDF statement for a date range, then a statement containing only that customer's transactions is downloaded.
- When the selected date range contains no transactions, then an empty-statement notice is displayed instead of a file.

## US-104 Administrator Audit View
As an Administrator, I want the audit log restricted to administrator accounts so that customer data stays protected.

Acceptance Criteria:
- Given a standard-role customer, when they navigate directly to /audit, then an access-denied response is returned and no audit data is rendered.
- Given an administrator, when they open /audit, then the audit log is displayed with the most recent entries first.
