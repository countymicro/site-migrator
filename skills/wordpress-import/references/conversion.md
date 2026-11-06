# Conversion details that change the result

## WXR and live source

WXR can hold posts, pages, custom fields/taxonomies, comments and users; it is not a copy of every plugin's database or of the uploads directory. Confirm the export's scope against live evidence. Official format entry points: [WordPress Export](https://wordpress.org/documentation/article/tools-export-screen/) and [WP-CLI export](https://developer.wordpress.org/cli/commands/export/).

Use a namespace-aware XML parser with numeric coercion disabled where identifiers/dates/text must remain exact. Preserve repeated metadata entries instead of silently discarding duplicates. Do not resolve external entities or execute exported scripts. Huge exports may need streaming/split-file processing; reconcile split-file duplicate IDs explicitly.

WXR link/permalink may differ from `post_name`, especially for nested pages, an assigned front page, custom permalink structures and subdirectory installations. Avoid deriving routes just from titles. Build route collision checks for encoded paths, trailing-slash equivalents and different post types. Retain query-style URLs as legacy mapping decisions if the new build needs path-based routes.

Use a configured set of exact source hostnames and base path, not a hardcoded domain or a prefix regex that also matches unrelated domains. Preserve query/fragment semantics; do not classify all links on the host as uploads. Resolve protocol-relative and relative media URLs against their actual document/base URL.

## Builders and plugins

Inventory builder types and widget names. For Elementor, inspect `_elementor_data`, global kit/site settings, shared template references and responsive defaults. Determine headers/footers from real template relationships; do not hardcode template IDs from another migration. Classic HTML, Gutenberg blocks, Divi/shortcodes and other builders need their own extraction strategy.

Capture source HTML, scoped CSS, fonts/icons and rendered screenshots. Recreate section/column/widget hierarchy and defaults, not merely flattened text. Translate responsive widths/order, padding, gaps, overlaps, headers and per-page variants; retain enough source IDs for debugging. Imported styles are evidence, not a reason to include an entire plugin runtime.

Preserve inline heading spans, explicit breaks, emphasized colors, links, lists, tables, testimonials and price/features. A sanitizer that removes every style can erase the design; retain a small reviewed formatting subset and reject executable content. Validate the result against live rendered text and screenshots.

Map forms, gated PDFs, video, Lottie, calendars, carousels, portal links and dynamic data separately. Hosted form shortcodes rarely include CRM workflows or full field definitions. Do not claim email replacement preserves subscriptions, marketing consent, CRM lists or autoresponders. Preserve approved scheduling embeds separately from email forms.

## Assets

Track attachment IDs and original URLs independently: not every referenced file is an exported attachment. Discover CSS images, masks, local/external font files, icons, animation JSON, inline SVG dependencies, lazy attributes and srcset sizes. Preserve the actual cropped variant when it changes composition. Keep every font weight/style declaration even if several point at the same variable font file.

Check MIME/content and filename collisions, encoded names, unsafe path traversal and external query-dependent asset variants. A saved HTML error page is not an image. SVGs and animation content need review before use. Downloads should remain inside the intended asset root.

When a source URL is unavailable, record status and attempts. Recover from a supplied backup if possible; otherwise omit broken decoration or preserve empty geometry as appropriate, and report the gap. Do not substitute unrelated art or fabricate files.

## URL/SEO decisions

Capture live title, description, canonical, robots and redirects because plugin values and live overrides can disagree with WXR. Preserve explicit noindex even for odd-looking published templates. Sitemaps contain only the intended canonical indexable URLs; staging-host access controls/noindex must not leak into production settings.

Inventory old uploads URLs, attachment pages, `?p=`, `?page_id=`, `?attachment_id=`, aliases, XML feeds and native/SEO-plugin sitemaps. Preserve known feeds, even when empty, if they are part of the source contract. Redirect only to an equivalent destination supported by source evidence; an obsolete service with no replacement should not automatically point home. Preserve unrelated tracking parameters when consuming legacy ID parameters.

For current collection behavior consult [Astro content collections](https://docs.astro.build/en/guides/content-collections/). Choose supported APIs at implementation time, lock versions, and avoid baking a historic framework major into this toolkit.
