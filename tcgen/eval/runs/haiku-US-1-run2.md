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
| TC-LOGIN-001 | US-1 · stated (positive) | User successfully logs in with valid credentials | User is on the login page<br>User has a registered account | 1. Enter username in the username field<br>2. Enter password in the password field<br>3. Click the login button<br>4. Verify the user is redirected to the products page | username = `standard_user`<br>password = `secret_sauce` | User is authenticated and directed to the products page | Critical | P1 | Screenshot of the products page after login | Draft |
| TC-LOGIN-002 | US-1 · derived (negative) | Login fails with empty username field | User is on the login page | 1. Leave the username field empty<br>2. Enter a valid password in the password field<br>3. Click the login button<br>4. Verify an error message is displayed | password = `secret_sauce` | Login is rejected and an appropriate error message is displayed | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-003 | US-1 · derived (negative) | Login fails with empty password field | User is on the login page | 1. Enter a valid username in the username field<br>2. Leave the password field empty<br>3. Click the login button<br>4. Verify an error message is displayed | username = `standard_user` | Login is rejected and an appropriate error message is displayed | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-004 | US-1 · derived (negative) | Login fails with both username and password empty | User is on the login page | 1. Leave both username and password fields empty<br>2. Click the login button<br>3. Verify an error message is displayed | — | Login is rejected and an appropriate error message is displayed | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-005 | US-1 · derived (negative) | Login fails with invalid username | User is on the login page | 1. Enter an invalid username in the username field<br>2. Enter a valid password in the password field<br>3. Click the login button<br>4. Verify an error message is displayed | username = `<invalid_username>`<br>password = `secret_sauce` | Login is rejected and an appropriate error message is displayed | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-006 | US-1 · derived (negative) | Login fails with incorrect password | User is on the login page<br>The username exists in the system | 1. Enter a valid username in the username field<br>2. Enter an incorrect password in the password field<br>3. Click the login button<br>4. Verify an error message is displayed | username = `standard_user`<br>password = `<incorrect_password>` | Login is rejected and an appropriate error message is displayed | Medium | P2 | Screenshot of the error message | Draft |
| TC-LOGIN-007 | US-1 · derived (security) | SQL injection attack in username field is rejected | User is on the login page | 1. Enter a SQL injection string in the username field<br>2. Enter a password in the password field<br>3. Click the login button<br>4. Verify login is rejected or an error message is displayed | username = `' OR '1'='1`<br>password = `<any_value>` | Malicious input is rejected or causes an error without granting access | Critical | P1 | Screenshot showing the rejection or error | Draft |
| TC-LOGIN-008 | US-1 · derived (security) | SQL injection attack in password field is rejected | User is on the login page | 1. Enter a valid username in the username field<br>2. Enter a SQL injection string in the password field<br>3. Click the login button<br>4. Verify login is rejected or an error message is displayed | username = `standard_user`<br>password = `' OR '1'='1` | Malicious input is rejected or causes an error without granting access | Critical | P1 | Screenshot showing the rejection or error | Draft |
| TC-LOGIN-009 | US-1 · derived (navigation) | Login page is accessible without authentication | User is not logged in | 1. Navigate to the login page<br>2. Verify the login form is displayed | — | Login form is displayed and accessible | Low | P3 | Screenshot of the login page | Draft |
