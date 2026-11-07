# Routing and release details

## Route ownership

Cloudflare Pages `_redirects` applies to static responses, not to requests handled by Functions. Keep a deliberate `_routes.json` in the final build output. For a site with root query shortlinks plus a form API, this may be:

```json
{"version": 1, "include": ["/", "/api/*"], "exclude": []}
```

This is an example, not a mandatory universal rule. Inventory additional query-style entry paths, locale/subdirectory prefixes and other dynamic routes. If a Function owns a route, implement any needed redirect there. Do not add global middleware invocation without checking its effect on static redirects and costs. The root Function must fall through to the actual homepage for ordinary `/` requests.

`_redirects` does not select on query parameters. Generate mappings for known `p`, `page_id` and `attachment_id` IDs and use a Function where required. Preserve unrelated query parameters, handle unknown IDs normally, avoid prefix/host open redirects, and verify slash handling in the Cloudflare runtime. Do not turn every unknown path into a 200 homepage response.

For moved media and attachment aliases, target the correct local media or equivalent page. Test both the existence and redirect behavior of targets. Count static redirect lines, dynamic rules and query mapping combinations separately; do not inflate rule counts with platform slash normalization. Check the current platform limits before generating large rule sets; use an appropriate supported design if they are exceeded.

Retain old feeds/sitemap aliases only where they existed. Static 200 rewrites are a different behavior from 301 redirects. Preserve true 404 behavior and noindex exclusions. A source feed with zero items can still require a valid empty feed.

## Environments and cutover

Use explicit site-specific project and Worker names; no County Micro identifiers, copied namespace IDs, widget keys or default recipient. Account selection must not rely on whichever login happened to be active. Check service/email bindings for production and functional previews after deployment.

Keep production canonical URLs based on the intended domain, even while serving a preview. Decide separately how previews are restricted/excluded from indexing, without putting a global staging noindex rule into the production artifact. Custom domains, www/apex redirects, HTTPS and DNS are separate from uploading `dist/`. Verify certificate/host behavior after any authorized domain change.

Before authorized cutover record old routing/DNS and known rollback deployment, avoid deleting WordPress/backups, and make any necessary canonical-host redirect explicit. Email configuration must not silently replace the company's mail service. If real email cannot be tested, state the missing evidence instead of claiming delivery.

## Canonical host at go-live

Use the apex as the production canonical host and configure a **Cloudflare 301 www-to-apex redirect** when the site goes live, unless the user explicitly selected another canonical host. Preserve that choice in the destination's `migration/` records. For a subdomain-only site, record the intended host rather than assuming ownership of the parent apex or its www hostname.

For an apex site, use a Cloudflare Single Redirect matching only the site's exact www hostname, for example `http.host eq "www.example.com"`, with dynamic target `concat("https://example.com", http.request.uri.path)`, status `301` and query-string preservation enabled. Match both HTTP and HTTPS. Substitute the destination's actual domain. An existing equivalent Cloudflare rule can be retained; inspect overlapping rules before adding another. Ensure www DNS is proxied and its TLS certificate is valid before verifying HTTPS requests. A DNS alias or canonical tag alone does not provide this redirect.

Keep canonicals, sitemap and internal absolute URLs on the chosen HTTPS apex. During authorized cutover, record the previous www DNS/rules for rollback and the actual rule identifier/settings. Do not change unrelated subdomains or mail records.

Verify live HTTP and HTTPS requests to www for `/`, a real nested page and a path with query parameters (including tracking parameters). Record the first response status and exact `Location`: the host redirect must retain the path and query string and target the HTTPS apex. Follow the chain to verify the expected page or legacy redirect, without loops or an apex-to-www bounce. Check HTTPS apex pages and certificate behavior too.

If domain access, DNS or TLS is pending, continue preview/content work and record the redirect as pending in `migration/status.md`. A preview deployment or saved rule is not evidence that the live redirect works; do not claim go-live complete until these hosted checks pass.

## Official references

- [Static Astro and Cloudflare adapter behavior](https://docs.astro.build/en/guides/integrations-guide/cloudflare/).
- [Pages Astro framework guide](https://developers.cloudflare.com/pages/framework-guides/deploy-an-astro-site/) for Pages build settings; reconcile adapter advice with the installed Astro version.
- [Pages redirects](https://developers.cloudflare.com/pages/configuration/redirects/) for rule semantics, query limitations and current limits.
- [Functions routing](https://developers.cloudflare.com/pages/functions/routing/) for invocation coverage in build output.
- [Pages service bindings](https://developers.cloudflare.com/pages/functions/bindings/#service-bindings) for Worker/environment configuration.
- [Cloudflare www-to-apex Single Redirect](https://developers.cloudflare.com/rules/url-forwarding/examples/redirect-www-to-root/) for hostname matching, dynamic targets and query-string preservation.
- [Pages www-to-apex guide](https://developers.cloudflare.com/pages/how-to/www-redirect/) for an alternative using Bulk Redirects and proxied www DNS.

These are maintained external references. Recheck them during a real implementation rather than assuming this pack freezes provider behavior.
