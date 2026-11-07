# Lighthouse checks and optimizations

Include this loop in a migration; do not wait for a separate performance request. Keep the source design and approved integrations. Use each destination’s existing build and deployment setup rather than copying a previous client’s optimizer, IDs or assets.

## Audit, fix, deploy, verify

1. Save a source baseline when available. Audit the homepage on mobile and desktop, plus examples of each distinct template: contact, article, archive/product, long image-heavy pages and embeds where present. Add pages with issues found during the visual sweep.
2. Use a pinned Lighthouse version in the destination and record settings. Run performance checks sequentially with the same settings before/after. Inspect the failed audits and LCP/CLS/network details, then fix their causes using the checklist below.
3. Rebuild and run normal checks; visually recheck affected templates on desktop/mobile and exercise menus, forms and embeds. A higher score does not replace the all-route visual review.
4. After an authorized deployment, verify the intended artifact/SHA is served and rerun Lighthouse on that deployed origin. After domain cutover, repeat on the canonical production hostname with real analytics/integrations enabled: a clean preview can miss production-only failures. After further fixes or tag-manager changes, audit again.
5. Record before/after scores, FCP/LCP/TBT/CLS, the audited URLs, tool/settings, capture times and release SHA/run URL in the migration report. Keep raw reports ignored and outside public output. Report failed or unavailable checks honestly; local, preview and production results are separate evidence.

Aim for **Performance ≥90, Accessibility 100, Best Practices 100 and SEO 100** on the audited indexable pages, unless the site has an explicitly agreed budget. Fix actionable failures and verify after deployment; do not silently lower targets or discard failing pages/runs. If scores vary, repeat and report the range/median. Preserve intentional noindex policies. Lighthouse scores are lab evidence, not field Core Web Vitals or WCAG certification.

## Optimization checklist

- **CSS:** combine/minify styles in their original cascade order and remove unused rules where useful. When pruning, include interaction scripts and preserve runtime/provider classes, responsive rules, variables and animations. Recheck loaded widgets and open menus, not only initial markup.
- **Images/LCP:** generate appropriately sized modern raster variants while retaining original media/download URLs, crops, transparency and animation. Use accurate dimensions, `srcset` and `sizes`; eagerly load the actual above-fold hero/logo or first product image. Preload CSS hero backgrounds with matching mobile/desktop URLs and media conditions. Lazy-load below-fold images and embeds with reserved space. Do not preload every image.
- **Stable layout:** changing image hints can shrink percentage-sized logos inside auto-sized links. Stabilize the intended containing block and compare header/hero/footer geometry on mobile and desktop. Test font swaps and responsive images for layout shifts.
- **Fonts/cache:** use local WOFF2 and an appropriate `font-display`; avoid full icon libraries for a few symbols. Native SVGs or reproducible subsets should retain used glyphs, runtime states and licenses, with a regeneration path. Use immutable caching for content-hashed assets; verify deployed headers and keep mutable HTML separate.
- **Accessibility:** fix measured contrast, descriptive link/image names, headings, focus order and touch targets. Closed menus must not expose focusable controls; test submenu, Escape and focus return. Check form states and provider-injected markup as well as placeholders. Preserve visual typography through CSS while fixing semantics.
- **SEO/browser errors:** repair missing descriptions, canonicals, descriptive links, favicons, asset 404s and console errors. Keep intentional robots/noindex behavior. Inspect third-party initiators: obsolete GTM tags can fail only on production. Preserve approved analytics/consent; remove a tracker only within this site’s authorization. Review the exact pending changes, publish only the authorized tag change, and verify the published version, remaining analytics and fresh network/console results. Never suppress errors or special-case Lighthouse to improve scores.

## Commands and CI

Install a compatible pinned Lighthouse dev dependency in the destination. Example:

```sh
npx --no-install lighthouse https://example.org/ \
  --chrome-flags='--headless --disable-gpu' \
  --only-categories=performance,accessibility,best-practices,seo \
  --output=json --output=html \
  --output-path=migration/lighthouse/home-mobile
```

Use `--preset=desktop` and a separate output path for desktop. Repeat for the selected template URLs. Keep reports under ignored `migration/lighthouse/`; publish a reviewed summary rather than raw reports that may contain URLs, content and browser context.

For deploy-on-push sites, implement a small `audit:lighthouse` script using the destination’s existing test tooling or Lighthouse CI. It must require `LIGHTHOUSE_BASE_URL` (no localhost fallback), run the selected scenarios sequentially against the verified deployed artifact, enforce the agreed score targets and record results/diagnostics. Provide Chrome in the runner. Run it after hosted smoke checks, not before deployment, and mark preview-only coverage accurately. No separate manifest format is required. The [release template](../../cloudflare-pages-release/assets/github-cloudflare.yml) includes the hook; adapt or remove assumptions about scripts/forms as usual.

References: [official Lighthouse CLI](https://github.com/GoogleChrome/lighthouse#using-the-node-cli), [performance scoring](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring).
