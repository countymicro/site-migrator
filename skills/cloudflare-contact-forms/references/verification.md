# Form verification matrix

Use an isolated mock receiver or browser network stubs for sending tests until live submission is authorized. Stubs must not reach the real email binding. “Challenge succeeded”, “API accepted a mock”, “provider accepted” and “received in inbox” are different results.

| State/test | Observable result |
| --- | --- |
| Configuration loading/unavailable or plain Astro preview | Fields visible; clear fallback; no false sent message; challenge does not initialize with missing key |
| Missing token | Send disabled or clear validation; server rejects bypass |
| Challenge success | Send enables exactly once prerequisites are met |
| Expired/error/reset challenge | Send disables; recoverable UI; input retained |
| Delayed successful POST | Visible sending indicator, disabled duplicate action, meaningful busy state |
| Successful POST | Thank-you persists; fields/challenge not immediately shown again; focus/status announcement works |
| Late/reset callbacks after success | Thank-you remains until explicit “send another” |
| 400/403/429/502/503, timeout/network failure | Appropriate visible error; input retained; no download/thank-you claimed |
| Repeat/recovery | Explicit retry/new-message behavior; a fresh token when needed; no double send |
| Resource request | Correct download offered after success only; email delivery and access control match agreed scope |

Server tests should exercise exact-origin rejection (including deceptive suffix domains), method/content type, streamed size limit without Content-Length, malformed fields/header injection, missing/invalid/expired/duplicate challenge, wrong hostname/action, limiter rejection, missing bindings and provider failure. Do not send email merely to test invalid inputs.

Hosted checks on each intended functional origin:

1. Public configuration endpoint is available only as intended and uses the right public widget key.
2. Empty/invalid authorized request reaches validation, while unapproved origin is rejected.
3. Real challenge renders in the intended theme, succeeds and enables sending. Test expiry/error handling locally too.
4. If authorized, submit one clearly labeled test; verify provider acceptance and ask for or inspect actual inbox receipt through approved tooling. Do not silently send to discover the correct destination.
5. Record deployed version, host, service/email bindings, test kind and results without request bodies, secrets or tokens.

A hosted 200 config/400 validation/Turnstile success combination proves reachability/challenge configuration, not email delivery and not the browser thank-you flow. Both need their own evidence.
