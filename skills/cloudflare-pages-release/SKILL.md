---
name: cloudflare-pages-release
description: Configure and verify a static Astro WordPress replacement on Cloudflare Pages, including Functions, legacy redirects, Worker bindings, preview hosts and controlled deployment/cutover. Use for migration hosting checks, GitHub Actions deployment pipelines and release work.
---

# Pages runtime and release

Read the site's target/account/environment and authorization. Default to a static Astro build hosted on **Cloudflare Pages**, with Pages Functions for necessary routes and a Worker for email. Consult [references/routing-release.md](references/routing-release.md) before routing/deployment. Verify current versions and provider docs; do not silently switch a requested Pages site to Workers static assets because a newer adapter defaults there.

Default new Pages project names to the site/brand slug without adding `-website`: repository `example-website` → Pages project `example` → `example.pages.dev`. Keep repository names independent. Check the desired hostname before creation and verify the actual assigned hostname. Use the selected project/hostname consistently in Wrangler, CI variables, verification URLs and form allowlists. Honor an explicit name or an existing project.

A static Astro site needs no SSR adapter. Configure its build output and include native Functions separately. Lock runtime/dependency versions based on current compatibility; record install/build commands. Do not blindly install a historic Astro/adapter version from a prior migration.

## Local validation

- Verify generated assets, sitemap/robots, canonical host, 404 and redirect files.
- Compile Functions and dry-run the Worker. Serve with the Cloudflare local runtime to test routing and service bindings; `astro preview` alone cannot prove either.
- Test representative normal pages, media/PDFs, aliases, attachment paths, query-ID shortlinks with tracking parameters, sitemap aliases, feed routes, unknown IDs and unknown paths. Check exact status and Location/content, loops and unintended catchalls.
- Limit Functions invocation to routes that need it. Reconcile `_redirects` behavior with invocation coverage and check account/platform limits for this site's redirect volume.

## Continuous integration and deployment

Include validation CI in the destination. Determine whether the user wants validation only or automatic publishing on pushes to the production branch; preserve an existing explicit choice. Read [references/github-actions.md](references/github-actions.md) for the reusable workflow, scoped credentials, deployment ordering and end-to-end checks. Ask for missing repository/branch/account choices near release, not as a blocker to importing content.

Build and verify the workflow before provisioning missing credentials or activating deployment. Adding a YAML file, uploading a secret and completing a push-triggered release are separate milestones. A deploy-on-push request includes following the first eligible run through Worker deployment, Pages deployment and hosted verification for the exact pushed SHA.

## Deploy when authorized

Use the identified account/project/environment, show or record a concrete target, then deploy in dependency order (typically contact Worker before Pages). Verify bindings and secrets through approved tools without disclosing them. Record the actual upload artifact/SHA/deployment ID, not merely a CLI success message. If build output differs from the working tree after a follow-up fix, rebuild and identify what was deployed.

Check the hosted site itself: routes, media, API readiness, configured preview/custom origin, Turnstile, form states, desktop/mobile layout and a representative set of legacy redirects. Use the contact skill for authorized delivery tests. Preview forms need explicit host/key/binding configuration; a working custom domain does not prove the Pages hostname works.

Require the [post-deployment Lighthouse check](../wordpress-parity/references/lighthouse.md) on the verified hosted origin. Compare the planned mobile/desktop/template scenarios to baseline, repair actionable failures and deploy/retest affected changes. Record exact scores, LCP/CLS and diagnostics against the release SHA/time. After custom-domain cutover, repeat there with production analytics enabled; mark preview-only, unavailable and below-budget results accurately. Include this gate after hosted smoke checks in deploy-on-push CI.

A deployment does not authorize domain cutover. If DNS cutover was requested, prepare host/HTTPS rules, rollback target, DNS delta and current production canonical configuration, then execute within that scope and verify. At go-live, configure and verify a Cloudflare permanent www-to-apex redirect preserving paths and query strings, unless the user explicitly selected a different canonical host; follow the canonical-host checklist in [references/routing-release.md](references/routing-release.md). Preserve business email/MX. Keep the old source/backup until cutover and rollback expectations are resolved. Report implemented, committed, pushed, deployed and DNS-switched states separately.
