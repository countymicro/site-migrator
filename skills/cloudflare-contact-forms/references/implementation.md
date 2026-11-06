# Account and runtime implementation

Check current official provider APIs and the destination's dependency versions rather than copying an old Worker's call signature. Cloudflare Email Service and Email Routing APIs/configuration are distinct; determine which is actually available in the target account. If native sending is unavailable, ask about an approved alternative and continue local form work.

For native Email Service, the sending domain must be onboarded, and recipient restrictions in the email binding must match the configured destination. Inspect the account without printing secrets. Do not change business MX/mail routing as a side effect of adding a website form.

Use a Pages service binding to a contact Worker when email/rate-limit bindings require that architecture. Forward the original same-origin request without replacing its URL origin with an internal synthetic hostname that then fails the configuration check. Keep the Worker private if public invocation is unnecessary. Production and preview service bindings need separate verification after deploy/redeploy.

Maintain per-environment values:

| Value | Check |
| --- | --- |
| Fixed form recipient(s) | User-approved; matches provider/binding restrictions |
| Fixed From | Verified domain/address; no visitor-controlled sender |
| Friendly sender name | Site-specific editable configuration; encoded via provider named-address API, not concatenated raw headers |
| Turnstile sitekey + secret | Same widget/environment; secret stored with secret tooling |
| Turnstile hostnames | Actual custom domain, www if used, and designated Pages host |
| Worker origin list | Exact scheme/host/port for every functional host; no suffix-wildcard trust |
| Expected action/hostname | Enforced on server verification response |
| Rate-limit binding | Provisioned and available to deployed Worker |
| Pages service binding | Correct Worker/environment and redeployed configuration |

Use an isolated preview/test Worker and recipient for functional previews; do not authorize arbitrary preview subdomains against the production inbox. Local Astro preview has no `/api/contact`; show a fallback instead of initializing a production challenge. Test Turnstile keys belong only in isolated development. Their dummy Siteverify response may use `action: test` and `hostname: localhost`: account for this explicitly in the test harness, without weakening production hostname/action checks.

Fetch configuration first; expose only public readiness/sitekey values for allowed hosts, never secret/account details. Register the challenge onload callback before loading its script. Clean up on navigation if applicable. Once successful, form reset/config refetch, error/expiry callbacks or late async responses must not return the UI to editing. Consider a single state owner with guards for stale responses.

## Sender identity and acceptance

Use the provider's structured named-address API where supported. In Cloudflare Email Service this is `from: {email: configuredAddress, name: configuredDisplayName}`, with visitor `replyTo` kept separate. Keep the display name in site configuration/content and carry it into Worker configuration deliberately; do not hardcode another client’s brand in the Worker. Reject CR/LF/control characters in configurable header values and use the provider’s escaping/encoding for Unicode names.

Type the send result accurately and require a nonempty documented `messageId` before the success response. Test missing/empty receipts as failure, named From, visitor Reply-To, and provider rejection. A message ID is provider acceptance, not proof of inbox arrival. See [delivery diagnostics](delivery-diagnostics.md) for authentication, observability and bounce diagnosis.

## Official references

Verify these at implementation time:

- [Email Sending Workers API](https://developers.cloudflare.com/email-service/api/send-emails/workers-api/): named addresses and send receipts; verify the API available to this account.
- [Email Service send bindings](https://developers.cloudflare.com/email-service/configuration/send-bindings/): sender and recipient restrictions.
- [Pages service bindings](https://developers.cloudflare.com/pages/functions/bindings/#service-bindings): Pages-to-Worker configuration and redeployment.
- [Turnstile server validation](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/): token verification, hostname and action.
- [Turnstile testing](https://developers.cloudflare.com/turnstile/troubleshooting/testing/): matching test keys and isolated local tests.
- [Turnstile errors](https://developers.cloudflare.com/turnstile/troubleshooting/client-side-errors/error-codes/): `110200` means the current domain is not authorized.

For console noise, identify the failing request and response first. Separate extension `contentscript`/Trusted Types errors and challenge iframe diagnostics from the actual `/api/contact` response. Reproduce in an appropriate clean browser when needed. Do not relax site CSP or add `data:`/wildcards to connect rules merely to hide unrelated logs. If a site policy actually blocks a required resource, use the narrow official integration requirements.
