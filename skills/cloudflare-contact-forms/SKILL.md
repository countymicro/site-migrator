---
name: cloudflare-contact-forms
description: Replace WordPress contact and lead forms with visible native forms and a Cloudflare Worker email backend, including Turnstile, environment bindings, delivery errors and persistent thank-you UI. Use during migrations or form submission troubleshooting.
---

# Native forms and Worker email

Read the site's form inventory and ask for missing destinations/workflow choices. Map every form/resource to approved recipients and success behavior. Preserve scheduling embeds separately. Use [references/implementation.md](references/implementation.md) for account/runtime details and [references/verification.md](references/verification.md) for state/hosted checks.

## Behavior contract

- Render fields, labels and fallback email/phone independently of API readiness. Loading configuration, missing bindings, blocked challenges or unavailable JavaScript must not make the form disappear. Make fallback and status copy client-editable.
- Model configuration/challenge readiness, editing, sending, recoverable error and success as explicit states. Disable duplicate submission immediately; show a visible sending indicator with `aria-busy`/live status. Preserve entered data on failure.
- Enable sending only when required configuration and the current challenge are ready. Expiry/error/reset clears readiness. Use a theme matching the page; avoid forcing an unreadable automatic dark widget on a light design.
- After a confirmed successful API response, show a **persistent thank-you view or real thank-you page**, announce it and move focus sensibly. A field reset followed by a new Turnstile widget is not a success view. Do not let reset/config/challenge callbacks overwrite success. Provide an explicit “send another” action if needed.
- Reveal the matching local resource only after a successful request when that is the agreed workflow. Clarify whether the resource is merely gated UI or requires genuine access control/email delivery.

## Server contract

Use a same-origin Pages endpoint and, where supported, a private service-bound Worker for email. Validate exact configured origins, methods/content types, bounded raw request bytes and field lengths/format; protect against header injection and abuse. Recipients and sender are server-side configuration, never visitor-controlled. Use a verified sender with visitor email only as Reply-To. Validate Turnstile on the server, including hostname/action; reject missing/invalid/expired tokens. Keep provider secrets server-side and redact submission content from logs.

Rate-limit with a durable/provider-supported binding. Bound challenge/provider timeouts and return distinct unavailable, validation, challenge, rate-limit and delivery errors. Return success only after provider acceptance. Do not automatically retry an ambiguous email send in a way that duplicates enquiries; preserve a clear recoverable status and use idempotency where supported.

Keep production/test accounts, recipient bindings, Turnstile keys and exact allowed hostnames consistent. A ready configuration check cannot prove the recipient is authorized or an inbox received mail. Implement mock success/delay/failure before touching live delivery.

## Completion

Test every form variant through the full browser state matrix, not just a successful challenge or empty POST. Use unit/runtime tests for server boundaries and browser checks for visibility, sending, errors and persistent success. If real sending was authorized, perform a labeled test to the approved recipient and record provider outcome and inbox confirmation separately. If not, report that delivery remains unverified; do not claim a mock proved live email.
