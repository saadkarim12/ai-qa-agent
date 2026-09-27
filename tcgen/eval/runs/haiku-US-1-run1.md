# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:08
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
| TC-LOGIN-001 | US-1 · stated (positive) | Log in successfully with valid credentials | User is on the login page<br>User has a registered account | 1. Enter valid username in the username field<br>2. Enter valid password in the password field<br>3. Click the Login button<br>4. Verify the user is redirected to the Products page | username = `standard_user`<br>password = `secret_sauce` | User successfully logs in and is taken to the Products page | Critical | P1 | Screenshot of the Products page after login<br>URL confirms redirect to products page | Draft |
| TC-LOGIN-002 | US-1 · derived (negative) | Display error message with incorrect password | User is on the login page<br>User has a registered account | 1. Enter valid username in the username field<br>2. Enter an incorrect password in the password field<br>3. Click the Login button<br>4. Verify an error message is displayed | username = `standard_user`<br>password = `<incorrect password>` | Login fails and an appropriate error message is displayed | High | P1 | Screenshot of the error message | Draft |
| TC-LOGIN-003 | US-1 · derived (negative) | Display error message with non-existent username | User is on the login page | 1. Enter a non-existent username in the username field<br>2. Enter any password in the password field<br>3. Click the Login button<br>4. Verify an error message is displayed | username = `<non-existent username>`<br>password = `<any password>` | Login fails and an appropriate error message is displayed | High | P1 | Screenshot of the error message | Draft |
| TC-LOGIN-004 | US-1 · derived (required-field) | Reject login with empty username field | User is on the login page | 1. Leave the username field empty<br>2. Enter a password in the password field<br>3. Click the Login button<br>4. Verify an error message is displayed | username = ``<br>password = `<any password>` | Login fails and an appropriate error message is displayed | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-005 | US-1 · derived (required-field) | Reject login with empty password field | User is on the login page | 1. Enter a valid username in the username field<br>2. Leave the password field empty<br>3. Click the Login button<br>4. Verify an error message is displayed | username = `standard_user`<br>password = `` | Login fails and an appropriate error message is displayed | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-006 | US-1 · derived (required-field) | Reject login with both username and password empty | User is on the login page | 1. Leave the username field empty<br>2. Leave the password field empty<br>3. Click the Login button<br>4. Verify an error message is displayed | username = ``<br>password = `` | Login fails and an appropriate error message is displayed | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-007 | US-1 · derived (state-transition) | Remain on login page after failed login attempt | User is on the login page | 1. Enter invalid credentials<br>2. Click the Login button<br>3. Verify the user is still on the login page | username = `<invalid username>`<br>password = `<invalid password>` | User remains on the login page without being redirected | Medium | P3 | Screenshot of the login page<br>URL confirms user is still on login page | Draft |
| TC-LOGIN-008 | US-1 · derived (security) | Prevent SQL injection via username field | User is on the login page | 1. Enter a SQL injection string in the username field<br>2. Enter any password in the password field<br>3. Click the Login button<br>4. Verify the login fails and no unexpected access is granted | username = `' OR '1'='1`<br>password = `<any password>` | Login fails safely without executing SQL or granting access | Critical | P1 | Screenshot of the error message<br>Application logs show no SQL execution | Draft |
| TC-LOGIN-009 | US-1 · derived (security) | Prevent SQL injection via password field | User is on the login page | 1. Enter a valid username in the username field<br>2. Enter a SQL injection string in the password field<br>3. Click the Login button<br>4. Verify the login fails and no unexpected access is granted | username = `standard_user`<br>password = `' OR '1'='1` | Login fails safely without executing SQL or granting access | Critical | P1 | Screenshot of the error message<br>Application logs show no SQL execution | Draft |
