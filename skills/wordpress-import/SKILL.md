---
name: wordpress-import
description: Obtain WordPress WXR exports through browser admin or local files and convert them into Astro content collections while preserving routes, SEO, builder structure and local media. Use during a WordPress-to-Astro migration or to repair an incomplete import.
---

# Import WordPress content

Read the site's intake and inspect the export before coding a converter. If the export is missing or pending, follow [the WordPress admin browser export workflow](../wordpress-migrate/references/wordpress-admin-export.md) to obtain and validate a fresh file, then resume here. Never alter the source export. Run the offline helper with absolute source/output paths:

```sh
python3 scripts/inventory_wxr.py /path/to/export.xml --source-url https://example.com --output /path/to/site/migration/inventory.json
```

Resolve script paths relative to this skill. The helper inventories; it does not convert builder widgets, fetch assets or prove that the export is complete. Review its retained original channel/base URLs and any `export-site-mismatch` warning against the intended source; a `--source-url` override is not site-identity verification. Read [references/conversion.md](references/conversion.md) for builder/media details and URL pitfalls.

## Reconcile before rendering

Compare export counts, statuses, post types and URLs with the live sitemap, navigation and crawled internal links. Inspect live SEO and design metadata. Record each public route, source ID, type, status, proposed destination and reason for any redirect or exclusion in `migration/routes.json`. Keep route paths independent of content filenames/slugs. Include sitemap-only and custom-type routes in the final verification set. Do not treat attachments, builder templates, menus or private records as public pages automatically.

Classify custom types before omitting them: a resource may be a page, a blog may contain zero posts, and a builder library may supply a shared footer. Ask for missing location datasets, split exports or plugin configuration where they affect real content. Do not expand unresolved template variables into fictional city pages.

## Produce editable collections

Use current supported Astro content collection APIs, a schema and native components. Retain title, original ID/slug/full URL, publication/modification dates with known timezone, categories, tags/custom taxonomies, featured image/alt, SEO title/description/canonical/robots, template identity and section structure. Preserve blank/unknown values honestly. Distinguish live overrides from export values with provenance.

Place public copy, headings, links, lists, navigation, business details, form labels/status/thank-you copy and shared sections in content collections. Unpublished records stay private and excluded from routing, assets, feeds and sitemap. Keep content editing understandable in the destination README; if section references or markers are used, validate them and explain how they work.

Extract builder/plugin data from postmeta when the regular body is empty or incomplete. Rebuild native layout/interaction components instead of depending on WordPress, PHP or copied builder runtime. Record unsupported widgets/shortcodes rather than silently dropping them. Preserve meaningful rich formatting while stripping executable handlers/scripts and unsafe URL schemes.

Download media into `public/images` (other local asset folders may hold fonts/icons). Rewrite all occurrences, including inline HTML/srcset and CSS backgrounds/masks. Use bounded retries/timeouts, stable filenames, collision detection and a manifest with HTTP outcomes. Keep original-to-local redirects where needed. Verify no runtime dependency remains on the old uploads host.

## Verify and preserve edits

Make import stages explicit and repeatable. Cache valid downloads/captures with provenance and an intentional refresh option. Warn before overwriting generated collections after client edits; prefer staging plus a reviewable diff. Do not run a destructive import as part of normal build.

Check all imported records' rendered text, metadata, URLs and referenced assets. Check local internal links/fragments and destination existence, sitemap/noindex exclusions, aliases, feeds and query-style legacy links. Reconcile counts back to inventory. Hand route decisions to the parity and Pages release skills; a successful XML parse is not migration completion.
