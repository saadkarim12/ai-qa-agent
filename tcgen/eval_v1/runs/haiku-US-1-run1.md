# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:01
- **Model:** claude-haiku-4-5
- **Stories:** 1 · **Test cases:** 9
- **Status:** every test case is Draft until a QA engineer reviews it

## US-1 — User Login

> User Story 1 — User Login
> As a registered user
> I want to log in to the website using valid credentials
> So that I can access the application.

| Test ID | Source | Objective | Preconditions | Steps | Test Data | Expected Result | Risk | Priority | Evidence Requirements | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-LOGIN-001 | US-1 · stated (positive) | Log in with valid credentials | User is on the login page<br>User has a registered account | 1. Enter `standard_user` in the username field<br>2. Enter `secret_sauce` in the password field<br>3. Click the Login button<br>4. Verify the user is redirected to the Products page | username = `standard_user`<br>password = `secret_sauce` | User is successfully authenticated and gains access to the application | Critical | P1 | Screenshot showing the Products page after login | Draft |
| TC-LOGIN-002 | US-1 · derived (negative) | Display error message for invalid username | User is on the login page | 1. Enter `<invalid username>` in the username field<br>2. Enter `secret_sauce` in the password field<br>3. Click the Login button<br>4. Verify an error message is displayed | username = `<invalid username>`<br>password = `secret_sauce` | Login fails and an appropriate error message is displayed | High | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-003 | US-1 · derived (negative) | Display error message for invalid password | User is on the login page | 1. Enter `standard_user` in the username field<br>2. Enter `<invalid password>` in the password field<br>3. Click the Login button<br>4. Verify an error message is displayed | username = `standard_user`<br>password = `<invalid password>` | Login fails and an appropriate error message is displayed | High | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-004 | US-1 · derived (negative) | Display error message when both credentials are invalid | User is on the login page | 1. Enter `<invalid username>` in the username field<br>2. Enter `<invalid password>` in the password field<br>3. Click the Login button<br>4. Verify an error message is displayed | username = `<invalid username>`<br>password = `<invalid password>` | Login fails and an appropriate error message is displayed | High | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-005 | US-1 · derived (required-field) | Display error message when username field is empty | User is on the login page | 1. Clear the username field<br>2. Enter `secret_sauce` in the password field<br>3. Click the Login button<br>4. Verify an error message is displayed | username = ``<br>password = `secret_sauce` | Login fails and an appropriate error message is displayed | High | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-006 | US-1 · derived (required-field) | Display error message when password field is empty | User is on the login page | 1. Enter `standard_user` in the username field<br>2. Clear the password field<br>3. Click the Login button<br>4. Verify an error message is displayed | username = `standard_user`<br>password = `` | Login fails and an appropriate error message is displayed | High | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-007 | US-1 · derived (required-field) | Display error message when both fields are empty | User is on the login page | 1. Clear the username field<br>2. Clear the password field<br>3. Click the Login button<br>4. Verify an error message is displayed | username = ``<br>password = `` | Login fails and an appropriate error message is displayed | High | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-008 | US-1 · derived (security) | Password field masks input for security | User is on the login page | 1. Click the password field<br>2. Enter `secret_sauce`<br>3. Verify the entered text is masked and not visible | password = `secret_sauce` | Password characters are masked and not visible on screen | High | P3 | Screenshot of the password field with masked input | Draft |
| TC-LOGIN-009 | US-1 · derived (positive) | Log in as a different user account | User is on the login page<br>A second registered user account exists | 1. Enter `problem_user` in the username field<br>2. Enter `secret_sauce` in the password field<br>3. Click the Login button<br>4. Verify the user is redirected to the Products page | username = `problem_user`<br>password = `secret_sauce` | User is successfully authenticated with different credentials and gains access to the application | High | P3 | Screenshot showing the Products page after login | Draft |

**Check before running**

- TC-LOGIN-009 — grounding: test data username = `problem_user` is not in the story or the examples
