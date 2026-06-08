---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Auth Endpoints

## GET /login

Description: Renders the login page. Flags: no auth required; no side effects. Parameters: none. Sample Response: HTML.

## POST /login

Description: Authenticates an admin and sets the signed `session` cookie.

Flags: no auth required; sets cookie on success.

Parameters: form fields `email`, `password`.

Sample Request: `POST /login`

Sample Response: `303 See Other` redirect to `/admin/questions`.

Error Responses: renders login HTML with 401 for invalid credentials or 403 for unverified email.

## GET /register

Description: Renders admin registration page. Flags: no auth required; no side effects. Parameters: none. Sample Response: HTML.

## POST /register

Description: Creates a whitelisted admin user and sends a verification email.

Flags: no auth required; writes a user row and sends email.

Parameters: form fields `username`, `email`, `password`.

Sample Response: HTML register page with success message.

Error Responses: 403 HTML when email is not whitelisted; 409 HTML when email exists.

## GET /verify

Description: Verifies an email address from a JWT query token.

Flags: no auth required; updates `User.email_verified`.

Parameters: query `token`.

Sample Response: HTML login page with success message.

Error Responses: 400 for invalid token, 404 HTML when user is missing.

## POST /logout

Description: Clears the `session` cookie.

Flags: no auth required; clears cookie.

Parameters: none.

Sample Response: `303 See Other` redirect to `/login`.

Error Responses: standard 500 error on unhandled server failure.

## GET /forgot-password

Description: Renders forgot-password page. Flags: no auth required; no side effects. Parameters: none. Sample Response: HTML.

## POST /forgot-password

Description: Sends a password reset email if the submitted email belongs to a user.

Flags: no auth required; may send email.

Parameters: form field `email`.

Sample Response: HTML forgot-password page with enumeration-safe success message.

Error Responses: standard 422 validation error or 500 internal error.

## GET /reset-password/{token}

Description: Renders reset form when token is valid, or an invalid-token state.

Flags: no auth required; no side effects.

Parameters: path `token`.

Sample Response: HTML reset-password page.

Error Responses: invalid tokens render HTML with `token_error`.

## POST /reset-password/{token}

Description: Updates a user's password from a valid password reset JWT.

Flags: no auth required; updates `User.password`.

Parameters: path `token`; form field `password`.

Sample Response: HTML login page with success message.

Error Responses: invalid token renders reset HTML with `token_error`; missing user renders reset HTML with error.
