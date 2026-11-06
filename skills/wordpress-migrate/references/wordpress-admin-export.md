# Download a fresh export through WordPress admin

Use this when the user has no usable export or asks for a fresh one. This obtains data from the **source WordPress site being migrated**, not the new Astro destination. Use the current environment's supported browser tool and its documented login/download controls; do not assume a particular browser API exists.

## Sign in to the correct site

1. Inspect the source URL and any supplied admin address. For a normal installation, `/wp-admin/` under the WordPress install path is a starting point, not proof of the correct endpoint. Account for subdirectories, multisite and custom login/SSO routes. Confirm the dashboard's site identity before exporting, especially if several sites share a login.
2. Reuse an authorized signed-in browser session where available. Otherwise open the sign-in page and let the user sign in, autofill credentials, complete MFA/CAPTCHA, or approve SSO through a supported handoff. Use existing authorized credentials only through permitted tools. Do not ask for passwords or one-time codes in chat, save them in intake, or copy session cookies into shell requests.
3. Resume after observing the authenticated dashboard. Do not repeatedly retry rejected credentials or bypass security controls. If access is denied, MFA is pending, or the account lacks export capability, ask for the needed handoff/access or a manual export and continue independent public-site discovery. Do not reset passwords, create users, elevate roles or change site settings to obtain access.

A migration request using this pack includes obtaining a missing export through authorized WordPress access. Do not ask again for routine navigation/download steps when that scope and access are established. Authentication handoffs and tool-enforced confirmations still apply.

## Generate and retrieve the file

Open **Tools → Export**, choose **All content**, then **Download Export File**. Observe the actual page/options rather than assuming labels are identical on every installation. Use the built-in content export; do not install a plugin, perform a restore/import or alter published content to generate it. If the platform uses a different export flow or creates several files, follow the observed authorized flow and retain all parts.

Choose an ignored private folder such as `<destination>/exports/` once the destination is known. Use the browser's supported download mechanism, wait for completion and obtain the actual local file/artifact path. If the browser cannot deliver a usable local file, ask the user to save or attach it, then continue from that file. Never claim a click or a success toast proves that a usable export was downloaded. Avoid leaving an unreviewed duplicate in a shared/public folder.

## Validate and resume

Check that the download is nonempty and parseable WXR, not a login page, error response, partial download or unrelated ZIP. If an export archive is supplied, inspect it and extract only expected files safely into the private folder before inventory. Preserve the original bytes; do not overwrite an older export or edited content automatically.

Run the import skill's offline inventory on each WXR file, reconcile split-file duplicates and compare the site's URL/identity, content types and counts with the intended source. The inventory retains original WXR channel/base URLs separately from `--source-url` and warns on a site mismatch; reconcile that warning before marking intake available. A verified domain mapping can explain a difference, and a multisite network base URL alone is not proof of the selected child site. Record export provenance in private intake: method `wordpress-admin`, actual admin/site address without session parameters, download time, selected scope, actual file path(s), and checksum from inventory. Preserve a meaningful zero-post count; do not confuse an empty/error export with a site that has no posts.

For a pending browser intake, set `export_path` to the downloaded local file, `export_status` to `available`, and `export_scope` to the observed selection only after validation. Keep `export_source: wordpress-admin`; add `export_files` for multiple parts and `export_downloaded_at` for the observed completion time. Then continue the normal import automatically; do not stop at the downloaded file.

Raw WXR can contain drafts, user details and private metadata. Keep it outside public assets, Git history and CI artifacts, and avoid capturing passwords/session tokens in screenshots or reports. A content export does not replace uploads backup or plugin database configuration; continue checking the import skill's documented gaps.

Official reference: [WordPress Tools Export](https://wordpress.org/documentation/article/tools-export-screen/).
