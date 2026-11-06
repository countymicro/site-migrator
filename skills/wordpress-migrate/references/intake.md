# Intake and per-site state

Ask what cannot be inferred from supplied instructions or connected configuration. Keep the first exchange short; ask conditional questions when the relevant feature is discovered. An unknown optional value is pending, not consent and not a reason to halt independent work.

| Decision | When needed | Handling |
| --- | --- | --- |
| Source URL, including subdirectory | Discovery | User-supplied source; inspect redirects and canonical host |
| WXR export location and scope/date | Import | Prefer All Content; ask for split exports, uploads backup or missing records if needed |
| Destination directory/repository | Before writes | Confirm existing edits and ownership; do not overwrite an unrelated project |
| Form recipients by form/resource | Email implementation | Ask explicitly; do not infer from the site's public address |
| Sender and sending domain | Email configuration | Must be verified for the selected provider; visitor is Reply-To |
| CRM, calendars, gated downloads, autoresponders | When discovered | Preserve approved integrations or agree on replacement; identify dropped automations |
| Shop, accounts, search, comments, multilingual, subscriptions | When discovered | Determine data/runtime/backend needs before removing behavior |
| Fidelity and intentional changes | Design | Default to source design; do not invent a redesign or import another site's accepted compromises |
| Cloudflare account/project and environments | Hosting preparation | Read connected account/project configuration; ask if ambiguous |
| Exact production and functional preview hosts | Hosted forms | Keep Turnstile hostname and Worker origin lists consistent |
| Analytics/consent | If present | Ask whether to preserve approved tracking; avoid duplicating legacy trackers |
| Deploy, push, DNS cutover, real email test | Before each affected external action | Use existing explicit scope; ask only for missing authorization |

Suggested conversational intake:

> I’ll match the existing design and build for Cloudflare Pages. Where is the WordPress export, where should the new project live, and which inbox should receive contact form submissions? I’ll inventory the source while those details are pending.

If a question interface supports only three short questions, use those three and defer account choices. If a form is not yet discovered, defer the mailbox question. Do not ask for passwords or secret keys in chat; explain which local secret command or connected account action is needed.

## State in the destination

- `migration/intake.json`: source URL, local export path, destination, per-site form decisions and scope. Keep ignored; it may reveal private mailbox/workstation details.
- `migration/inventory.json`: WXR counts/records and builder/dependency inventory. Treat as private until reviewed for unpublished titles and metadata.
- `migration/routes.json`: reconciled public route decisions, including sitemap-only routes and redirects. Use this authoritative route set for the final parity sweep.
- `migration/media.json`, `issues.json`: download outcomes, original-to-local mapping and unresolved source gaps.
- `migration/parity/`: screenshot evidence and reviews; raw captures may include private browser context and need review before publishing.
- `migration/status.md`, `MIGRATION.md`: sanitized progress and final evidence.

Do not commit raw WXR, private/draft content, raw captures or account identifiers by default. Public Markdown collections and sanitized reports are deliberate outputs, not a license to publish everything from the export. If unpublished content must be retained locally, keep it outside routing and public assets and ask before publishing it in a public repository.

The bundled initializer adds only its generated private paths to `.gitignore`, refuses to overwrite intake and never initializes Git or deploys. For a preexisting intake, edit intentional decisions in place; rerunning is not a reset command. Its scope fields default to false. If the conversation already authorizes an action, record that scope explicitly rather than asking again.
