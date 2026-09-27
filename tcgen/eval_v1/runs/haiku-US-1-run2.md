# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:02
- **Model:** claude-haiku-4-5
- **Stories:** 1 · **Test cases:** 8
- **Status:** every test case is Draft until a QA engineer reviews it

## US-1 — User Login

> User Story 1 — User Login
> As a registered user
> I want to log in to the website using valid credentials
> So that I can access the application.

| Test ID | Source | Objective | Preconditions | Steps | Test Data | Expected Result | Risk | Priority | Evidence Requirements | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-LOGIN-001 | US-1 · stated (positive) | Log in with valid credentials | User is on the login page | 1. Enter `standard_user` in the username field<br>2. Enter `secret_sauce` in the password field<br>3. Click the login button<br>4. Verify the user is redirected to the Products page | username = `standard_user`<br>password = `secret_sauce` | User successfully logs in and accesses the application | Critical | P1 | Screenshot of the Products page after login | Draft |
| TC-LOGIN-002 | US-1 · derived (negative) | Reject login with invalid username | User is on the login page | 1. Enter `<invalid username>` in the username field<br>2. Enter `secret_sauce` in the password field<br>3. Click the login button<br>4. Verify an appropriate error message is displayed<br>5. Verify the user remains on the login page | username = `<invalid username>`<br>password = `secret_sauce` | Login fails and user remains on the login page with an error message | High | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-003 | US-1 · derived (negative) | Reject login with invalid password | User is on the login page | 1. Enter `standard_user` in the username field<br>2. Enter `<invalid password>` in the password field<br>3. Click the login button<br>4. Verify an appropriate error message is displayed<br>5. Verify the user remains on the login page | username = `standard_user`<br>password = `<invalid password>` | Login fails and user remains on the login page with an error message | High | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-004 | US-1 · derived (required-field) | Reject login with missing username | User is on the login page | 1. Leave the username field empty<br>2. Enter `secret_sauce` in the password field<br>3. Click the login button<br>4. Verify an appropriate error message is displayed | username = ``<br>password = `secret_sauce` | Login fails with an error indicating username is required | Medium | P3 | Screenshot of the error message | Draft |
| TC-LOGIN-005 | US-1 · derived (required-field) | Reject login with missing password | User is on the login page | 1. Enter `standard_user` in the username field<br>2. Leave the password field empty<br>3. Click the login button<br>4. Verify an appropriate error message is displayed | username = `standard_user`<br>password = `` | Login fails with an error indicating password is required | Medium | P3 | Screenshot of the error message | Draft |
| TC-LOGIN-006 | US-1 · derived (required-field) | Reject login with both username and password missing | User is on the login page | 1. Leave the username field empty<br>2. Leave the password field empty<br>3. Click the login button<br>4. Verify an appropriate error message is displayed | username = ``<br>password = `` | Login fails with an error message | Medium | P3 | Screenshot of the error message | Draft |
| TC-LOGIN-007 | US-1 · derived (ui) | Clear username field without affecting password | User is on the login page | 1. Enter `standard_user` in the username field<br>2. Enter `secret_sauce` in the password field<br>3. Clear the username field<br>4. Verify the password field still contains the entered password | username = `standard_user`<br>password = `secret_sauce` | Username field is cleared while password remains intact | Low | P4 | Screenshot of both fields | Draft |
| TC-LOGIN-008 | US-1 · derived (security) | Log in successfully with locked_out_user account | User is on the login page | 1. Enter `locked_out_user` in the username field<br>2. Enter `secret_sauce` in the password field<br>3. Click the login button<br>4. Verify an appropriate error message is displayed | username = `locked_out_user`<br>password = `secret_sauce` | Login is rejected with an appropriate error message | High | P2 | Screenshot of the error message | Draft |

**Check before running**

- TC-LOGIN-008 — grounding: test data username = `locked_out_user` is not in the story or the examples
