# GitHub Actions validation and publishing

Read this when implementing the destination site's CI or deploy-on-push request. The toolkit's own Python workflow is unrelated to deploying client sites.

## Decide and prepare the destination

Inspect the site's existing workflows, default/production branch, npm scripts, Node version file, Cloudflare project/Worker and Pages Git integration. Include validation on pull requests and production-branch pushes. If automatic publishing was not specified, ask whether pushes should deploy; do not activate it merely because a YAML template exists. Avoid duplicate production publishers from Actions and Pages Git integration; choose a single intended publisher and make any configuration changes within scope.

Adapt [assets/github-cloudflare.yml](../assets/github-cloudflare.yml) into the destination's `.github/workflows/cloudflare.yml`. It assumes static output in `dist/`, `.nvmrc`, npm scripts `check`, `test`, `build`, `verify`, `worker:deploy`, `verify:cloudflare`, and a contact Worker. Verify or implement those interfaces rather than adding no-op scripts. Remove contact steps for a site without forms. Run validation from a clean checkout: `verify` must use committed, sanitized public verification inputs rather than ignored WXR exports, private drafts, local browser captures or a workstation cache. Normal build/validation must not require the old WordPress server or production secrets.

`verify:cloudflare` must honor `PREVIEW_URL` and fail on wrong status/Location/content; a localhost default must not hide a hosted check failure.

Set the actual production branch in both the push trigger and deploy-step conditions (the example uses `main`). Use pinned, verified action revisions and the destination lockfile/runtime. Validation must complete before credentials are exposed or deployment starts; PR code must not deploy or receive production secrets. Do not use `pull_request_target` to execute untrusted changes with credentials.

## Credentials and configuration

Use approved connected tools or secret commands to provision these in the **destination** GitHub repository/environment, never in this reusable toolkit:

| Setting | Storage/use |
| --- | --- |
| `CLOUDFLARE_API_TOKEN` | Encrypted Actions secret, scoped deployment credential |
| `CLOUDFLARE_ACCOUNT_ID` | Actions variable identifying the selected account |
| `CLOUDFLARE_PAGES_PROJECT` | Actions variable with the existing project name |
| `CLOUDFLARE_PAGES_URL` | Actions variable with the exact functional URL used for hosted smoke checks |
| Turnstile secret | Worker secret in the target Cloudflare environment, not a public build variable |

Prefer an existing suitable deployment token. If a new token is necessary, prepare its concrete account/resources, permissions, expiration/rotation and intended GitHub secret before any missing approval. Use Pages deployment access plus only the Worker edit/binding permissions the actual deploy requires. Apply resource restrictions supported by the account; do not promise a Pages token is project-scoped when it is account-wide. Do not request global API keys or DNS/mail edit access merely for a routine deploy. Choose expiry deliberately; the reference site's non-expiring token is not a default.

Transfer a newly issued token directly to encrypted secret storage, without echoing it in logs, screenshots, chat, command arguments or committed files. If a UI/tool has a confirmation boundary for granting access, explain that specific boundary. Reuse authorizations already given. Keep secret *values* out of intake and evidence; record configuration presence and intended scope. Check missing credentials early with a helpful CI error, not a misleading deploy success.

## Deployment contract

The workflow validates the exact checked-out SHA, deploys the contact Worker first, then Pages/Functions from the same build with explicit project, branch and commit hash. Serialize releases targeting the same production environment and do not cancel a running multi-resource deployment halfway through. GitHub concurrency does not guarantee FIFO or that every intermediate commit runs: verify the final hosted SHA is the intended latest one. Record partial outcomes and stop if Worker/Pages or hosted checks fail; do not claim a complete release or blindly redeploy older artifacts.

Keep Actions permissions minimal (`contents: read` for the direct CLI workflow); add deployment/PR permissions only if an actual integration uses them. A manual dispatch from a non-production branch should not accidentally publish production. Use GitHub environment protections if required by the site's release policy.

After deploy, smoke-test hosted routes/redirects/media and the contact configuration endpoint, where applicable. This CI check must not send real enquiries. Browser challenge/thank-you and inbox checks remain separate evidence. Emit a run summary with SHA, target, deployment URLs/versions when available and verification results; never print credentials.

## Prove it works

Commit and push when authorized, then follow the first eligible **push-triggered** Actions run for that exact SHA to completion. Investigate failed jobs/logs; fix and rerun within the user's scope. Record run URL/conclusion, actual Worker/Pages IDs and hosted check outcomes. Workflow recognition, a stored secret, a manual local deployment or a successful build alone does not prove automatic publishing works. If provisioning/execution is blocked, report configured versus verified and finish independent work.

References: [Cloudflare Pages Direct Upload with CI](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/), [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [GitHub deployment controls](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments).
