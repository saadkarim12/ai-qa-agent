# Test Cases

- **Site:** https://www.saucedemo.com/
- **Generated:** 27 Sep 2026 14:09
- **Model:** claude-sonnet-5
- **Stories:** 1 · **Test cases:** 7
- **Status:** every test case is Draft until a QA engineer reviews it

## US-1 — User Login

> User Story 1 — User Login
> As a registered user
> I want to log in to the website using valid credentials
> So that I can access the application.

| Test ID | Source | Objective | Preconditions | Steps | Test Data | Expected Result | Risk | Priority | Evidence Requirements | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| TC-LOGIN-001 | US-1 · stated (positive) | Log in successfully with valid credentials | User is on the login page<br>User has a registered account | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `standard_user` in the username field<br>3. Enter `secret_sauce` in the password field<br>4. Click the login button | username = `standard_user`<br>password = `secret_sauce` | User is redirected to the Products page and is logged in | Critical | P1 | Screenshot of the Products page after login | Draft |
| TC-LOGIN-002 | US-1 · derived (negative) | Reject login with an incorrect password | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `standard_user` in the username field<br>3. Enter `<invalid password>` in the password field<br>4. Click the login button | username = `standard_user`<br>password = `<invalid password>` | An appropriate error message is displayed and the user remains on the login page | High | P1 | Screenshot of the error message | Draft |
| TC-LOGIN-003 | US-1 · derived (negative) | Reject login with an unregistered username | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `<invalid username>` in the username field<br>3. Enter `secret_sauce` in the password field<br>4. Click the login button | username = `<invalid username>`<br>password = `secret_sauce` | An appropriate error message is displayed and the user remains on the login page | High | P1 | Screenshot of the error message | Draft |
| TC-LOGIN-004 | US-1 · derived (required-field) | Reject login when the username field is left empty | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Leave the username field empty<br>3. Enter `secret_sauce` in the password field<br>4. Click the login button | username = ``<br>password = `secret_sauce` | An appropriate error message is displayed indicating the username is required | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-005 | US-1 · derived (required-field) | Reject login when the password field is left empty | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `standard_user` in the username field<br>3. Leave the password field empty<br>4. Click the login button | username = `standard_user`<br>password = `` | An appropriate error message is displayed indicating the password is required | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-006 | US-1 · derived (required-field) | Reject login when both username and password fields are left empty | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Leave the username field empty<br>3. Leave the password field empty<br>4. Click the login button | username = ``<br>password = `` | An appropriate error message is displayed indicating that both fields are required | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-007 | US-1 · derived (security) | Prevent login using SQL injection style input in the credential fields | User is on the login page | 1. Navigate to `https://www.saucedemo.com/`<br>2. Enter `' OR '1'='1` in the username field<br>3. Enter `' OR '1'='1` in the password field<br>4. Click the login button | username = `' OR '1'='1`<br>password = `' OR '1'='1` | Login is rejected and an appropriate error message is displayed, with no unauthorized access granted | Critical | P1 | Screenshot of the error message | Draft |
