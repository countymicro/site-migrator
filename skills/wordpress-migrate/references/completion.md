# Evidence for completion

Use actual observations from the destination, not this file's presence, as proof. Report failed/unavailable checks alongside passing checks.

- **Export acquisition:** if obtained through admin, confirm the correct site/dashboard, observed scope, actual completed local WXR file(s), timestamp/checksum and successful parse. Login/download pending is distinct from import complete; keep raw exports private.
- **Inventory:** count page/post/custom types and publication states; distinguish an empty post collection from missing exports. Reconcile WXR/live routes, navigation and intentional exclusions.
- **Content:** assert source text/sections survive in rendered output, including rich inline formatting, lists, tables, downloads and shared copy. Client edits live in collections. Check every imported record, not one example.
- **URLs/SEO:** compare titles, descriptions, canonicals, robots/noindex, feeds and sitemap inclusion; test aliases, shortlinks, attachment links and media redirects in the Cloudflare runtime. No loops, unrelated catchalls, accidental staging canonicals or drafts in sitemap.
- **Media:** all referenced local assets exist and load, including CSS images, fonts, icons, SVG masks, cropped variants, PDFs and animation JSON. Missing source files have real outcomes and an explicit handling decision.
- **Visual:** every reconciled public page reviewed on desktop and mobile; measured viewports, full-page live/target evidence and findings. Shared fixes rechecked on affected template families. A signed-off small difference belongs to this site only.
- **Behavior:** desktop/mobile menus, focus, link hit targets, carousels, embeds, videos, animation/reduced-motion and every form variant, including pending, errors, success and resource download states.
- **Forms:** configuration unavailable state remains visible; challenge lifecycle works; server rejects bad origins/inputs/tokens; delivery failure is not success. Require documented provider receipts, sanitized delivery diagnostics and correct friendly From/Reply-To. Mock/provider acceptance/recipient-server acceptance/inbox receipt are different evidence levels. Verify sending-domain authentication and investigate bounces if a real test is missing.
- **Build/runtime:** lock dependencies; run install/build/type checks and meaningful tests; compile Functions and Worker; smoke test representative route classes under Wrangler. Astro preview alone does not validate Pages routing or service bindings.
- **CI/CD:** validation on PRs/pushes; automatic production deploy only when requested, on the selected branch after passing checks. Record scoped credential setup without secret values, first push-triggered run URL/conclusion, exact SHA, Worker-before-Pages deployment and hosted smoke results. Report configured vs verified separately.
- **Release if requested:** account/project/environment and exact URL/version/SHA; host allowlists, service/email bindings and challenge behavior on actual hosted origin. Distinguish deployed artifact from current local edits and DNS cutover.

Final report: short outcome, counts, remaining limits, preview/production location, editing/deploy docs, verification results and exact release state. If something essential is blocked, say what and why, preserve a useful runnable result, and continue any independent authorized work.
