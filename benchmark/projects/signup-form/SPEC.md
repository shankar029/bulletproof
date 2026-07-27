# SPEC — Signup Form (UI)

A client-side signup form (static HTML+JS). Same DOM contract for both arms so tests can drive it:
`#email`, `#password`, `#confirm` inputs; `#submit` button; `#error` text container; `#success` container.

## Rules
- **Submit is disabled until the whole form is valid.**
- Email must match a basic email format, else invalid.
- Password ≥ 8 chars and contains **at least one letter and one digit**.
- `#confirm` must equal `#password`.
- No validation error is shown **before the user interacts**.
- On a valid submit, `#success` shows `Account created for <email>`; the page does not navigate.
- Invalid input must **never** produce a success message.

## Acceptance (verified by Playwright in `oracle/`)
Disabled-until-valid, invalid-email rejection, short-password rejection, missing-digit rejection,
confirm-mismatch rejection, clean initial state, and a successful happy-path submit.
