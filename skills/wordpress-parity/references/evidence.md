# Evidence manifest

Keep paths relative to `migration/parity/manifest.json`. Capture files stay under that directory. Source and target screenshots must be different nonempty PNG/JPEG files. Browser tools may save the files to an allowed evidence location first; copy reviewed files into this layout when permitted.

The verifier accepts either an import `inventory.json` (`items` with `public: true` and `route`) or the reconciled `routes.json` below. For final checks use the latter, including sitemap-only routes and excluding approved redirects/non-pages:

```json
{"routes": [{"id": "42", "url": "/about/", "public": true}]}
```

A route key is the exact request path plus query, excluding fragments. `public` must be explicit. All public routes need one desktop and one mobile view; extra/duplicate routes are errors. For query-style routes record the exact request URL tested.

Example manifest (repeat for every route; copy both view structures with real evidence):

```json
{
  "schema_version": 1,
  "pages": [{
    "route": "/about/",
    "views": {
      "desktop": {
        "width": 1440, "height": 1000,
        "source": {"url": "https://example.com/about/", "width": 1440, "height": 1000, "screenshot": "about-desktop-source.png"},
        "target": {"url": "http://127.0.0.1:4321/about/", "width": 1440, "height": 1000, "screenshot": "about-desktop-target.png", "overflow": false, "broken_images": []},
        "review": {"status": "pass", "reviewed_at": "2026-11-06T15:00:00Z", "notes": "Inspected full page and interactions."}
      },
      "mobile": {
        "width": 390, "height": 844,
        "source": {"url": "https://example.com/about/", "width": 390, "height": 844, "screenshot": "about-mobile-source.png"},
        "target": {"url": "http://127.0.0.1:4321/about/", "width": 390, "height": 844, "screenshot": "about-mobile-target.png", "overflow": false, "broken_images": []},
        "review": {"status": "accepted-difference", "reviewed_at": "2026-11-06T15:00:00Z", "notes": "Describe the actual difference and current-site acceptance."}
      }
    }
  }]
}
```

Allowed passing review statuses: `pass`, `accepted-difference`. `pending` and `fail` deliberately fail the check. Every review needs a timezone-aware timestamp and nonempty findings. An accepted difference needs actual current-site acceptance, not an inferred permission from another project.

The helper checks actual source/target viewport measurements against the view, validates desktop width ≥1024 and mobile width 320–767, verifies screenshot signatures/files, rejects reused screenshot paths, and checks target integrity. It cannot establish that a screenshot depicts the claimed URL, detect fabricated review notes, or compare pixels. The agent must inspect browser output and the actual images. Passing this helper never substitutes for that review.
