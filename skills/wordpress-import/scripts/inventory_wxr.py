#!/usr/bin/env python3
"""Offline WXR inventory; never fetch, modify source, or publish private records."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET

CONTENT_NS = 'http://purl.org/rss/1.0/modules/content/'
INTERNAL_TYPES = {'attachment', 'nav_menu_item', 'elementor_library', 'wp_template',
                  'wp_template_part', 'wp_global_styles', 'wp_navigation',
                  'custom_css', 'customize_changeset', 'revision', 'oembed_cache'}


def request_path(url):
    parts = urlsplit(url)
    return (parts.path or '/') + ('?' + parts.query if parts.query else '')


def inspect(path, source=None):
    if path.stat().st_size > 100 * 1024 * 1024:
        raise ValueError('Export exceeds 100 MiB; use a reviewed streaming importer or split exports.')
    raw = path.read_bytes()
    normalized = raw.replace(b'\x00', b'').upper()
    if b'<!DOCTYPE' in normalized or b'<!ENTITY' in normalized:
        raise ValueError('DTD/entity declarations are not supported.')
    root = ET.fromstring(raw)
    channel = root.find('channel')
    if root.tag != 'rss' or channel is None:
        raise ValueError('Expected an RSS channel containing a WordPress WXR export.')
    wp_uri = next((element.tag.split('}')[0][1:] for element in channel
                   if element.tag.endswith('}wxr_version') and
                   element.tag.startswith('{http://wordpress.org/export/')), None)
    if not wp_uri:
        raise ValueError('Missing WordPress WXR version/namespace.')
    wp = '{' + wp_uri + '}'
    base = source or channel.findtext('link') or channel.findtext(wp + 'base_site_url')
    if not base or urlsplit(base).scheme not in ('http', 'https') or not urlsplit(base).hostname:
        raise ValueError('A valid --source-url or channel link is required.')
    export_site = {
        'title': channel.findtext('title', ''),
        'channel_url': channel.findtext('link', ''),
        'base_site_url': channel.findtext(wp + 'base_site_url', ''),
        'base_blog_url': channel.findtext(wp + 'base_blog_url', '')
    }
    records, warnings, routes, ids = [], [], {}, set()
    exported_url = export_site['channel_url'] or export_site['base_blog_url'] or export_site['base_site_url']
    if not exported_url:
        warnings.append({'type': 'missing-export-site-identity'})
    elif source:
        def site_identity(url):
            parts = urlsplit(url)
            return parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip('/') or '/'
        if site_identity(source) != site_identity(exported_url):
            warnings.append({'type': 'export-site-mismatch', 'requested_url': source,
                             'exported_url': exported_url,
                             'detail': 'Review site identity or a verified domain mapping before import.'})
    counts, widgets = Counter(), Counter()
    for node in channel.findall('item'):
        field = lambda key: node.findtext(wp + key, '')
        post_id, kind, status = field('post_id'), field('post_type'), field('status')
        if not post_id or not kind or not status:
            raise ValueError('Each WXR item needs post_id, post_type and status.')
        if post_id in ids:
            raise ValueError(f'Duplicate WXR post ID: {post_id}')
        ids.add(post_id)
        counts[(kind, status)] += 1
        metadata = {}
        for meta in node.findall(wp + 'postmeta'):
            key, value = meta.findtext(wp + 'meta_key', ''), meta.findtext(wp + 'meta_value', '')
            metadata.setdefault(key, []).append(value)
        public = status == 'publish' and kind not in INTERNAL_TYPES
        url = urljoin(base.rstrip('/') + '/', node.findtext('link', '')) if node.findtext('link') else None
        route = request_path(url) if url else None
        if public and not url:
            warnings.append({'type': 'missing-public-url', 'id': post_id})
        if public and kind not in ('page', 'post'):
            warnings.append({'type': 'classify-custom-type', 'id': post_id, 'post_type': kind})
        if public and url:
            # Path slashes normalize only for collision warnings; preserve the actual URL.
            collision = route.split('?')[0].rstrip('/') or '/'
            collision += ('?' + urlsplit(url).query) if urlsplit(url).query else ''
            if collision in routes:
                warnings.append({'type': 'route-collision', 'id': post_id, 'other_id': routes[collision], 'route': route})
            routes[collision] = post_id
        builder = []
        for value in metadata.get('_elementor_data', []):
            try:
                def walk(nodes):
                    if not isinstance(nodes, list):
                        raise ValueError('Expected a list of builder nodes')
                    for item in nodes:
                        if not isinstance(item, dict):
                            raise ValueError('Invalid builder node')
                        if item.get('widgetType'):
                            widgets[str(item['widgetType'])] += 1
                        walk(item.get('elements', []))
                walk(json.loads(value))
                builder.append('elementor')
            except (ValueError, TypeError, RecursionError):
                warnings.append({'type': 'invalid-builder-json', 'id': post_id})
        body = node.findtext('{' + CONTENT_NS + '}encoded', '') or ''
        if '<!-- wp:' in body:
            builder.append('gutenberg')
        if '[et_pb_' in body:
            builder.append('divi')
        seo_keys = [key for key in metadata if any(term in key.lower() for term in ('yoast', 'rank_math', 'aioseo', 'seopress'))]
        records.append({
            'id': post_id, 'title': node.findtext('title', ''), 'post_type': kind,
            'status': status, 'public': public, 'url': url, 'route': route,
            'slug': field('post_name'), 'parent_id': field('post_parent'),
            'published_local': field('post_date'), 'published_gmt': field('post_date_gmt'),
            'modified_local': field('post_modified'), 'modified_gmt': field('post_modified_gmt'),
            'content_characters': len(body), 'builders': sorted(set(builder)),
            'taxonomy': [{'domain': term.get('domain', ''), 'slug': term.get('nicename', ''), 'name': term.text or ''}
                         for term in node.findall('category')],
            'featured_image_ids': metadata.get('_thumbnail_id', []),
            'attachment_url': field('attachment_url') or None,
            'seo': {key: metadata[key] for key in seo_keys},
            'meta_keys': sorted(metadata),
            'repeated_meta_keys': sorted(key for key, values in metadata.items() if len(values) > 1)
        })
    return {
        'schema_version': 1, 'captured_at': datetime.now(timezone.utc).isoformat(),
        'source_url': base, 'requested_source_url': source, 'export_site': export_site,
        'export_sha256': hashlib.sha256(raw).hexdigest(),
        'wxr_version': channel.findtext(wp + 'wxr_version'),
        'counts': [{'post_type': kind, 'status': status, 'count': count}
                   for (kind, status), count in sorted(counts.items())],
        'widget_counts': dict(sorted(widgets.items())), 'items': records, 'warnings': warnings,
        'limitations': ['Export completeness requires live sitemap/navigation reconciliation.',
                        'Public custom types are candidates requiring classification.',
                        'Attachment media, plugin databases and live SEO were not fetched.']
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('export', type=Path)
    parser.add_argument('--source-url')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.export.expanduser().resolve() == args.output.expanduser().resolve():
            raise ValueError('Output cannot overwrite the source export.')
        data = inspect(args.export.expanduser(), args.source_url)
        output = args.output.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
        print(f'Inventoried {len(data["items"])} items; {len(data["warnings"])} warnings. Private report: {output}')
    except (OSError, ValueError, ET.ParseError) as exc:
        parser.exit(2, f'Inventory error: {exc}\n')


if __name__ == '__main__':
    main()
