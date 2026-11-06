# Design and interaction review

Look for the meaningful mismatches below. Use the source's values and target behavior; numeric spacing from a prior site is not a universal design rule.

| Area | Common migration loss |
| --- | --- |
| Type | Missing font weights, incorrect heading tags/sizes, line height, inline spans, explicit breaks, fallback fonts |
| Layout | Wrong column widths/shrink, nested padding, section gaps, header variants, sticky/overlap offsets, mobile order |
| Imagery | Wrong cropped variant/aspect ratio, missing masks/backgrounds, different object fit, blank-image geometry |
| Widgets | List/social icons, price/features, resource cards, icon-box placement, video placeholders and animation sizing |
| Contact | Form absent until API is ready, header covering fields, missing heading gap, misaligned contact links/social row |
| Cards/CTAs | Only text clickable, underline on social hover, CTA aligned inside the wrong wrapper, touch targets |
| Testimonials | Avatar/name gap, second-row vertical alignment, carousel pagination/height, single active slide |
| Narrow screens | Closed menu still overflowing, long code/pre text, unbroken URLs, embeds wider than their column |

Forms must remain visible even when configuration is unavailable. A blank live third-party form is evidence of a source failure, not the desired usability of a newly commissioned replacement. Record an intentional native replacement as such; compare its typography/spacing to the source design and verify every state separately.

Distinguish source conditions from regressions: missing media, empty premium animation placeholders, provider error pages, rotating headlines and asynchronous carousel timing. Do not load hidden animations just because their JSON exists if that diverges from the intended/source state. Discuss material intentional changes. Tiny differences may be accepted for the current site; document that acceptance without calling the result pixel-exact.

For each page inspect top/header, all middle sections and footer. Exercise desktop and mobile menus, submenu keyboard/focus/escape behavior, telephone/email links, portal/card links, social hover, testimonial controls and CTA positioning. Verify no horizontal overflow or broken/pending images. Probe a tablet breakpoint when responsive source rules differ there.

All forms also need the state matrix in the contact skill: loading/sending and persistent success are visible UI work, not solely Worker tests. Use browser network stubs or an isolated mock receiver for delay/failure/success. These must not create real contact submissions unless that test was authorized.
