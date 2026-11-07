---
name: wordpress-parity
description: Recreate and verify a migrated WordPress site's visual design and interactions against the live source on every public page at desktop and mobile sizes. Use for migration design work and visual parity follow-up fixes.
---

# Rebuild and verify design

Use the reconciled route inventory, live rendered pages, computed styles and source assets. A flattened content import or generic themed layout does not satisfy a design-preserving migration. Read [references/review.md](references/review.md) while building and reviewing.

Use the environment's supported browser tool and follow its automation rules. If browser access fails, complete content/runtime work, keep browser verification pending and report the limitation. Do not label pages reviewed without seeing them.

## Review loop

1. Establish native template families and shared components from real source pages. Build representative desktop/mobile examples early, then cover all routes.
2. For **every public page**, compare source and target at the same desktop and mobile viewport. Defaults: 1440×1000 and 390×844; measure actual viewport dimensions, not just requested dimensions. Add intermediate widths if a breakpoint problem appears.
3. Scroll the full page to trigger lazy content, wait for fonts/media to settle, return to consistent positions and capture full-page evidence. Account for a logged-in admin bar without altering the target layout. Record dynamic frames/provider failures separately.
4. Inspect the actual screenshots and interactions. Measure computed typography, width, alignment, margins, crops and section geometry to explain meaningful mismatches. Fix shared causes, then recheck affected templates and unusual per-page overrides.
5. Save source/target captures and review findings per route/viewport. After a fix, mark old evidence superseded and recapture affected views. A zero-overflow/zero-broken-image result is an integrity check, not visual sign-off.

Test navigation, hover/focus, full card link areas, mobile ordering, carousels, videos/embeds, reduced motion and form visibility/states. Include contact, legal, resources, calendar and unusual long-copy pages, not just the homepage.

During implementation and after release, read [references/lighthouse.md](references/lighthouse.md). Include measured CSS/image/font/loading optimizations and accessibility/SEO fixes in the migration, with score/metric baselines and fresh deployed-origin audits. Preserve layout and approved integrations, then recheck affected views and states. A passing score does not replace visual review.

Use [references/evidence.md](references/evidence.md) for the bundled `scripts/check_parity.py` contract. Run it on the final reconciled public route set, not only the WXR subset. Its pass means evidence coverage/integrity passed; only actual browser review can establish similarity.

Close with route coverage, corrected shared differences, current screenshots, remaining source conditions and site-specific accepted differences. Ask about genuinely ambiguous or intentional changes, not each routine spacing fix. Do not assume this site's owner accepts the small differences accepted for a previous client.
