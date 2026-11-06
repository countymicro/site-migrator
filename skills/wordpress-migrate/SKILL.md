---
name: wordpress-migrate
description: Rebuild a WordPress site in Astro for Cloudflare Pages, coordinating export intake, content and URL preservation, design parity, email forms, and release verification. Use for a complete WordPress migration with this skill pack.
---

# WordPress migration

Deliver an editable Astro project, preserving the source site's design, public content, URLs and SEO, plus a report of verified behavior and gaps. Default to static Astro on Cloudflare Pages with Workers for email. Honor an explicitly different target; adapt the hosting phase rather than silently switching products.

## Intake and resume

Read the destination's instructions, Git status and any `migration/` records. If the destination is not yet known, do read-only source discovery and ask for it. Reuse answers from this conversation and the site's intake; never take another site's configuration as defaults.

Ask only for missing decisions that affect the work. Start with a short batch:

- Where is the WordPress WXR export (absolute path or attached file), and is it an All Content export? Request the actual file in the conversation if attachment is needed; text-only question tools cannot accept uploads.
- Where should the new site/repository live? Inspect an existing destination before writing.
- For discovered contact/lead forms: which mailbox receives each form, and should CRM workflows or resource delivery be retained? A public contact address is not proof of the submission destination.

Default to closely matching the live site. Offer those defaults briefly; ask about redesign only if intent conflicts. Ask later for missing verified sender/domain, Cloudflare account/project, preview/custom hostnames and deployment scope when those decisions become relevant. A missing account or secret does not block content/design work. If no export is available, inventory the live site and document the import blocker; never invent drafts, dates, taxonomy or plugin data.

Use [references/intake.md](references/intake.md) for conditional questions and saved-state conventions. Optionally run `scripts/init_migration.py` with conversational answers using `--non-interactive`; the interactive version is for a human terminal. Credentials go through environment/secret tools, not intake JSON or chat.

## Execute the migration

1. Read [wordpress-import](../wordpress-import/SKILL.md). Reconcile WXR, live sitemap, menus, links and media before choosing templates. Inventory custom content and dynamic workflows; identify features a static replacement cannot reproduce.
2. Build content collections and reusable native Astro layouts. Preserve original routes and metadata. Keep all client-editable copy, shared business details, navigation and form feedback in collections. Read [wordpress-parity](../wordpress-parity/SKILL.md) while implementing design; source screenshots and computed styles are required design inputs.
3. When forms exist, read [cloudflare-contact-forms](../cloudflare-contact-forms/SKILL.md). Build them visibly even before account configuration. A native email form is not equivalent to a CRM workflow; disclose and resolve that decision.
4. Read [cloudflare-pages-release](../cloudflare-pages-release/SKILL.md) for local runtime checks and any authorized release. Prepare a working local result before asking about optional publishing. Do not automatically deploy because a scaffold offers to.
5. Complete all-page desktop/mobile visual review, interactions, content/SEO verification and appropriate build/type/runtime checks. Repair defects and recapture affected routes. Do not call DOM integrity checks or a passing build proof of visual parity.

Read these sibling files as phases of one workflow; do not require separate invocations or user approvals to continue ordinary implementation. If a required tool is unavailable, use a supported equivalent or report the specific unverified part and continue independent work.

## Completion and handoff

Maintain `migration/status.md` with completed work, current evidence, unresolved decisions and the next useful action. Keep `migration/intake.json` private. Produce a destination `README.md` for editing/building/deploying and `MIGRATION.md` with actual counts of pages, posts, other public types, retained unpublished entries, assets, redirect rules and exclusions. Never copy counts or acceptance notes from the reference project.

List unconverted widgets/workflows, missing media, source defects, intentionally changed behavior, accepted visual differences, and any routes not verified. Distinguish zero items from unknown/missing data. Report local implementation, commit/push, deployed URL/version, DNS status, provider acceptance and inbox receipt separately. Use [references/completion.md](references/completion.md) for the evidence checklist. Finish the authorized work; do not substitute a plan or an importer scaffold for the migrated site.
