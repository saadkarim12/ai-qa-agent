# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:26
- **Model:** claude-opus-5
- **Stories:** 1 · **Test cases:** 9
- **Status:** every test case is Draft until a QA engineer reviews it

## US-1 — User Login

> User Story 1 — User Login
> As a registered user
> I want to log in to the website using valid credentials
> So that I can access the application.

| Test ID | Source | Objective | Preconditions | Steps | Test Data | Expected Result | Risk | Priority | Evidence Requirements | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-LOGIN-001 | US-1 · stated (positive) | Log in successfully with valid credentials | Browser is open on `https://www.saucedemo.com/`<br>User is not logged in | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `standard_user` in the username field<br>3. Enter `secret_sauce` in the password field<br>4. Click the login button<br>5. Verify the products page is displayed | username = `standard_user`<br>password = `secret_sauce` | User is logged in and the products page is displayed | Critical | P1 | Screenshot of the page after login | Draft |
| TC-LOGIN-002 | US-1 · derived (negative) | Reject login with a valid username and an invalid password | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `standard_user` in the username field<br>3. Enter `<invalid password>` in the password field<br>4. Click the login button<br>5. Verify an error message is displayed | username = `standard_user`<br>password = `<invalid password>` | Login is refused, an appropriate error message is displayed and the user stays on the login page | High | P1 | Screenshot of the error message | Draft |
| TC-LOGIN-003 | US-1 · derived (negative) | Reject login with an unknown username | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `<unregistered username>` in the username field<br>3. Enter `secret_sauce` in the password field<br>4. Click the login button<br>5. Verify an error message is displayed | username = `<unregistered username>`<br>password = `secret_sauce` | Login is refused and an appropriate error message is displayed | High | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-004 | US-1 · derived (required-field) | Require the username field | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Leave the username field empty<br>3. Enter `secret_sauce` in the password field<br>4. Click the login button<br>5. Verify an error message is displayed | password = `secret_sauce` | Login is blocked and an appropriate error message about the missing username is displayed | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-005 | US-1 · derived (required-field) | Require the password field | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `standard_user` in the username field<br>3. Leave the password field empty<br>4. Click the login button<br>5. Verify an error message is displayed | username = `standard_user` | Login is blocked and an appropriate error message about the missing password is displayed | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-006 | US-1 · derived (boundary) | Verify credentials are case sensitive | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `STANDARD_USER` in the username field<br>3. Enter `secret_sauce` in the password field<br>4. Click the login button<br>5. Verify an error message is displayed | username = `STANDARD_USER`<br>password = `secret_sauce` | Login is refused and an appropriate error message is displayed | Medium | P3 | Screenshot of the error message | Draft |
| TC-LOGIN-007 | US-1 · derived (ui) | Mask the password while typing | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `secret_sauce` in the password field<br>3. Verify the typed characters are masked | password = `secret_sauce` | Password characters are not shown in plain text | Medium | P3 | Screenshot of the password field | Draft |
| TC-LOGIN-008 | US-1 · derived (security) | Reject SQL injection input in the login fields | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `' OR '1'='1` in the username field<br>3. Enter `' OR '1'='1` in the password field<br>4. Click the login button<br>5. Verify the user is not logged in | username = `' OR '1'='1`<br>password = `' OR '1'='1` | Login is refused, an appropriate error message is displayed and no application data is exposed | Critical | P2 | Screenshot of the page after submit | Draft |
| TC-LOGIN-009 | US-1 · derived (permission) | Prevent access to the products page without logging in | No user is logged in<br>Browser session has no login cookies | 1. Navigate to `<products page URL>`<br>2. Verify the products page is not displayed | target page = `<products page URL>` | Access is denied and the user is kept on or returned to the login page with an appropriate error message | Critical | P1 | Screenshot of the resulting page | Draft |
