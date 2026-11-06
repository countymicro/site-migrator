# Site Migrator

Reusable agent skills for rebuilding WordPress sites in **Astro on Cloudflare Pages**, with Markdown content collections, local media, preserved URLs and SEO, native email forms, and evidence from desktop/mobile browser review.

Start a migration with:

> Using https://github.com/countymicro/site-migrator, migrate the WordPress site at https://example.com.

The agent should read [AGENTS.md](AGENTS.md), then [wordpress-migrate](skills/wordpress-migrate/SKILL.md). It asks for the WordPress export and destination project, then the form email recipient and any other decisions needed for the actual site. It proceeds with discovery and local implementation while deployment decisions are pending. Each migrated site gets its own project and Git repository; this repository holds the reusable process.

A repository URL is an instruction to the agent to fetch and read the repository; it does not automatically install skills in every agent product. If your agent cannot fetch it, clone this repository and point the agent to its local `AGENTS.md`:

```sh
git clone https://github.com/countymicro/site-migrator.git
```

## Skills

| Skill | Use |
| --- | --- |
| [wordpress-migrate](skills/wordpress-migrate/SKILL.md) | Intake, coordination, completion report; start here for a whole migration |
| [wordpress-import](skills/wordpress-import/SKILL.md) | WXR inventory, content/media, builders, metadata, URL preservation |
| [wordpress-parity](skills/wordpress-parity/SKILL.md) | Rebuild design and inspect every public page at desktop and mobile sizes |
| [cloudflare-contact-forms](skills/cloudflare-contact-forms/SKILL.md) | Native forms, Worker email, Turnstile, submission and thank-you states |
| [cloudflare-pages-release](skills/cloudflare-pages-release/SKILL.md) | Pages routing, bindings, hosted checks, deployment and domain cutover |

The skills can be used directly by path. Keep this directory structure when copying the pack: the main skill links to its sibling skills. No paid plugin, specific browser provider, global skill installation, or County Micro account is required. Use the browser and deployment tools available in the current environment.

## Helpers

Python 3.10+ is enough for all bundled helpers; they use only the standard library. Astro, Node, Wrangler and browser tooling belong in the destination project, with versions chosen and locked during that migration.

Optional interactive intake (run from this repository):

```sh
python3 skills/wordpress-migrate/scripts/init_migration.py \
  --source-url https://example.com --output /path/to/client-site
```

For agent-driven intake, ask the questions conversationally, then pass the answers with `--non-interactive`. Run `--help` for the options. This writes a private, ignored `migration/intake.json` and creates no application, deploys nothing, and sends no email. The agent continues with the skills to build the actual site.

Inspect a WXR export without touching it or fetching its URLs:

```sh
python3 skills/wordpress-import/scripts/inventory_wxr.py /private/path/export.xml \
  --source-url https://example.com --output /path/to/client-site/migration/inventory.json
```

Check recorded visual evidence after browser review:

```sh
python3 skills/wordpress-parity/scripts/check_parity.py \
  --inventory /path/to/client-site/migration/inventory.json \
  --manifest /path/to/client-site/migration/parity/manifest.json
```

This checks route coverage, viewport measurements, review records, screenshot files, overflow and broken images. It does **not** compare pixels or decide visual similarity. See the [evidence format](skills/wordpress-parity/references/evidence.md).

Run the helper regression suite with:

```sh
python3 -m unittest discover -s tests -v
```

## What completion means

A successful build is one check. A migration also needs reconciled content and URL inventories, all-page visual review, tested form states, and an honest account of source gaps. The report separates implemented, committed, pushed, deployed, DNS switched, provider-accepted email and inbox-confirmed delivery.

The defaults are local implementation and close design fidelity. Publishing, changing DNS/MX, and sending real test messages follow the user's actual instructions; the agent asks only for missing authorization or essential details. Existing authorizations persist.

Exports can contain drafts, users, private content and plugin metadata. Keep exports, intake answers, credentials, raw captures, and contact submissions out of this reusable repository and out of public site assets. Sanitized evidence and imported public content belong in each destination repository as appropriate.

These skills encode lessons from the County Micro migration without shipping its content, export, keys, or account configuration. They are a guided migration toolkit, not a universal automatic converter for every WordPress plugin, store, or membership system.
