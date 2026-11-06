# Site Migrator

Skills for an AI coding agent to rebuild a WordPress site as an editable **Astro website on Cloudflare Pages**, while keeping its design, content, URLs and search metadata.

## Start a migration

Give your agent this prompt, replacing the example URL:

> Using https://github.com/countymicro/site-migrator, migrate the WordPress site at https://example.com.

The agent reads [AGENTS.md](AGENTS.md) and starts the [migration skill](skills/wordpress-migrate/SKILL.md). It asks for missing details as they become relevant:

- **WordPress export:** where the XML file is saved. In WordPress, choose **Tools → Export → All content**.
- **New project:** where to create the website and which Git repository to use.
- **Forms:** which inbox receives submissions, the sender address and friendly sender name, and any downloads or CRM behavior to preserve.
- **Hosting:** the Cloudflare account, project and domain, plus whether pushes should automatically publish the site.

You can include answers in your first prompt to save time. Each website gets its own project and repository, so you can reuse this toolkit for multiple clients.

This repository is private, so your agent needs GitHub access. If it cannot read the link directly, clone it:

```sh
git clone https://github.com/countymicro/site-migrator.git
```

Then tell the agent:

> Read site-migrator/AGENTS.md and use its migration workflow to migrate https://example.com.

## What it handles

- Converts pages and posts into editable Markdown content collections and downloads media locally.
- Preserves page addresses, SEO titles and descriptions, and creates redirects where needed.
- Recreates layouts and checks every public page against the original on desktop and mobile.
- Replaces contact forms with email submissions, spam protection, a sending indicator and a persistent thank-you message.
- Configures friendly email sender names, checks delivery receipts, and investigates missing mail or domain authentication problems.
- Adds GitHub Actions validation and, when requested, automatic Cloudflare deployment after checks pass.

The agent asks before dropping or changing features it cannot reproduce, such as store checkout, member accounts or plugin-specific workflows. Keep the original site available during migration so its appearance and behavior can be compared.

## What you receive

A separate website repository with editing and deployment instructions, plus a migration report listing content counts, redirects, checks performed and anything still unresolved.

The report distinguishes code changes, commits, pushes, deployments, domain changes and confirmed email delivery. Publishing, domain/email DNS changes and real test emails follow your instructions; missing access or decisions are raised when needed.

## Included skills

| Skill | Purpose |
| --- | --- |
| [wordpress-migrate](skills/wordpress-migrate/SKILL.md) | Start here; gathers answers and runs the complete migration |
| [wordpress-import](skills/wordpress-import/SKILL.md) | Import content, media, URLs and SEO |
| [wordpress-parity](skills/wordpress-parity/SKILL.md) | Match the design and check desktop/mobile pages |
| [cloudflare-contact-forms](skills/cloudflare-contact-forms/SKILL.md) | Build forms and verify email behavior |
| [cloudflare-pages-release](skills/cloudflare-pages-release/SKILL.md) | Set up CI, deployment and hosted checks |

The release skill includes a [GitHub Actions template](skills/cloudflare-pages-release/assets/github-cloudflare.yml) to adapt for each website.

## Optional developer tools

These helpers need Python 3.10+ and no extra Python packages. Run them from this repository. They support the agent's work; they do not build or deploy a website by themselves.

Start a guided intake:

```sh
python3 skills/wordpress-migrate/scripts/init_migration.py \
  --source-url https://example.com --output /path/to/new-site
```

Use `--help` for options, including `--sender-name` and `--ci-mode`. See the [import skill](skills/wordpress-import/SKILL.md) for export inventory and the [parity skill](skills/wordpress-parity/SKILL.md) for screenshot evidence checks. The evidence helper checks recorded coverage and files; the agent still needs to inspect the actual pages.

Run helper tests:

```sh
python3 -m unittest discover -s tests -v
```

Keep client exports, credentials, private drafts and contact submissions out of this toolkit and public website assets. The migration workflow keeps private intake files separate from publishable content.
