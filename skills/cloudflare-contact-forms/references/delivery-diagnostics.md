# Delivery diagnostics and domain authentication

Use this when a real submission shows success but the mailbox has no message, or when onboarding a new sending domain. Do not assume a paid plan, API code defect or inbox spam rule caused the failure before inspecting evidence.

## Establish the delivery stage

1. Use a uniquely labeled, user-authorized test with a recorded time, intended recipient and deployed version. Confirm the browser shows sending followed by persistent thank-you.
2. Capture the provider receipt and correlate its message ID with Worker acceptance/failure events and Email Service activity/delivery events. Configure Worker observability deliberately; receipt IDs/status codes are useful, form bodies and raw errors containing personal data are not. An exception or missing receipt must fail the API rather than returning a false sent message.
3. Distinguish provider accepted, recipient server accepted, bounced/rejected, suppressed, and inbox-confirmed. If the recipient rejected mail, retain a sanitized SMTP status/reason and inspect that cause. A later bounce can occur after the API has returned success.
4. Inspect Inbox/Junk/quarantine with approved mailbox access, or ask the recipient for the labeled test. Once the cause is known, fix that cause and retest within the existing authorization. Stop on repeated identical failures without new evidence; do not keep sending duplicate probes.

## Authenticate the actual From domain

Inspect the sending domain's provider onboarding, required DNS records and current DNS. Check DKIM publication/signing and DMARC alignment for the actual From domain. Microsoft 365 rejection `550 5.7.509` can indicate a DMARC failure: a missing provider DKIM record was the observed cause in the reference migration, not a universal diagnosis for every missing email.

Read the provider-generated record for this domain. Never copy a DKIM selector/key from a previous site. Prepare the exact record name, type, value, purpose and proposed DNS delta before requesting any missing authorization. Adding DKIM delegates signing authority; it is distinct from switching the website domain. Do not treat `dns_cutover` permission as blanket permission to change mail authentication.

Apply only authorized records. Preserve existing mail routing/MX and existing SPF/DMARC policy unless a concrete, separately authorized change is required. Do not create a second SPF record or weaken DMARC to bypass a signing problem. Verify propagation and provider authentication state, then retest delivery and inspect the received message/authentication headers where available.

If the recipient/plan/API is unsupported, verify current account capabilities and documentation before proposing a paid upgrade or alternate provider. Do not bake historic pricing or plan assumptions into the migration.

## Evidence and scope

Report receipt ID, sanitized provider/SMTP outcome, inbox receipt, sender display name and Reply-To separately. A successful live delivery does not automatically validate future deployments or new domains.

A request to test a submission authorizes that test, not every diagnostic production deployment, DNS edit or new credential. Existing broader authorizations still apply: prepare the concrete repair, ask only when a needed action is outside that scope, then continue. If an execution tool requires confirmation for a credential/DNS action, explain the exact boundary and reason; do not manufacture a blanket approval rule from this reference case.

References: [Workers send API](https://developers.cloudflare.com/email-service/api/send-emails/workers-api/), [Email authentication](https://developers.cloudflare.com/email-service/concepts/email-authentication/), [Email Service activity log](https://developers.cloudflare.com/email-service/observability/logs/).
