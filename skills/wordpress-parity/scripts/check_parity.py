#!/usr/bin/env python3
"""Check coverage/integrity of recorded browser reviews, not pixel similarity."""
import argparse
from datetime import datetime
import json
from pathlib import Path
from urllib.parse import urlsplit


def route_path(value):
    if not isinstance(value, str) or not value.startswith('/') or value.startswith('//') or '#' in value:
        raise ValueError('Routes must be explicit request paths with optional query and no fragment.')
    return value


def expected_routes(data):
    records = data.get('routes', data.get('items'))
    if not isinstance(records, list):
        raise ValueError('Expected inventory items or reconciled routes list.')
    expected = set()
    for item in records:
        if item.get('public') is not True:
            continue
        path = route_path(item.get('route', item.get('url')))
        if path in expected:
            raise ValueError(f'Duplicate public route: {path}')
        expected.add(path)
    if not expected:
        raise ValueError('No public routes; cannot claim a completed parity sweep.')
    return expected


def check(inventory, manifest, evidence_root):
    expected = expected_routes(inventory)
    if manifest.get('schema_version') != 1 or not isinstance(manifest.get('pages'), list):
        raise ValueError('Expected schema_version 1 and a pages list.')
    errors, seen, screenshots = [], set(), set()
    root = evidence_root.resolve()
    for page in manifest['pages']:
        route = route_path(page.get('route'))
        if route in seen:
            errors.append(f'{route}: duplicate page')
        seen.add(route)
        views = page.get('views', {})
        if set(views) != {'desktop', 'mobile'}:
            errors.append(f'{route}: expected desktop and mobile views')
        for mode in ('desktop', 'mobile'):
            view = views.get(mode)
            label = f'{route} {mode}'
            if not isinstance(view, dict):
                errors.append(f'{label}: missing or invalid view')
                continue
            width, height = view.get('width'), view.get('height')
            if (type(width) is not int or type(height) is not int or height < 400
                    or (mode == 'desktop' and width < 1024)
                    or (mode == 'mobile' and not 320 <= width <= 767)):
                errors.append(f'{label}: invalid viewport')
            for side in ('source', 'target'):
                evidence = view.get(side, {})
                if evidence.get('width') != width or evidence.get('height') != height:
                    errors.append(f'{label} {side}: measured viewport mismatch')
                url = evidence.get('url', '')
                parts = urlsplit(url)
                if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password:
                    errors.append(f'{label} {side}: invalid capture URL')
                # A live alias may redirect; record its final capture URL and explain in review notes.
                rel = evidence.get('screenshot')
                if not isinstance(rel, str) or not rel:
                    errors.append(f'{label} {side}: missing screenshot path')
                    continue
                image = (root / rel).resolve()
                if not image.is_relative_to(root):
                    errors.append(f'{label} {side}: screenshot escapes evidence directory')
                    continue
                if image in screenshots:
                    errors.append(f'{label} {side}: reused screenshot path')
                screenshots.add(image)
                try:
                    size = image.stat().st_size
                    with image.open('rb') as stream:
                        signature = stream.read(8)
                    if size < 32 or not (signature == b'\x89PNG\r\n\x1a\n' or signature.startswith(b'\xff\xd8\xff')):
                        errors.append(f'{label} {side}: empty or unsupported screenshot')
                except OSError:
                    errors.append(f'{label} {side}: screenshot missing or unreadable')
            target = view.get('target', {})
            if target.get('overflow') is not False or target.get('broken_images') != []:
                errors.append(f'{label}: target overflow/broken-image check failed or missing')
            review = view.get('review', {})
            if review.get('status') not in ('pass', 'accepted-difference'):
                errors.append(f'{label}: review incomplete or failed')
            if not isinstance(review.get('notes'), str) or not review['notes'].strip():
                errors.append(f'{label}: review findings missing')
            try:
                stamp = datetime.fromisoformat(review.get('reviewed_at', '').replace('Z', '+00:00'))
                if stamp.utcoffset() is None:
                    raise ValueError('timezone required')
            except (ValueError, TypeError, AttributeError):
                errors.append(f'{label}: invalid review timestamp')
    for route in sorted(expected - seen):
        errors.append(f'{route}: missing page')
    for route in sorted(seen - expected):
        errors.append(f'{route}: not in the public route inventory')
    return errors, len(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    args = parser.parse_args()
    try:
        errors, count = check(json.loads(args.inventory.read_text()),
                              json.loads(args.manifest.read_text()), args.manifest.parent)
        if errors:
            for error in errors:
                print(error)
            parser.exit(1, f'FAIL: {len(errors)} evidence checks failed.\n')
        print(f'PASS: evidence coverage/integrity for {count} routes / {count * 2} views. '
              'Visual similarity still depends on the recorded human/agent browser reviews.')
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        parser.exit(2, f'Evidence error: {exc}\n')


if __name__ == '__main__':
    main()
