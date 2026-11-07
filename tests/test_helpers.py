"""Behavioral regression checks for private intake, WXR inventory and evidence claims."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / 'skills/wordpress-migrate/scripts/init_migration.py'
IMPORT = ROOT / 'skills/wordpress-import/scripts/inventory_wxr.py'
PARITY = ROOT / 'skills/wordpress-parity/scripts/check_parity.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


inventory = load('inventory', IMPORT)
parity = load('parity', PARITY)


def item(post_id, kind='page', status='publish', link='https://example.org/studio/about/', meta=''):
    return f'''<item><title>Example &amp; title</title><link>{link}</link>
    <wp:post_id>{post_id}</wp:post_id><wp:post_type>{kind}</wp:post_type>
    <wp:status>{status}</wp:status><wp:post_name>original-slug</wp:post_name>
    <wp:post_date>2020-01-01 12:00:00</wp:post_date><wp:post_date_gmt>2020-01-01 17:00:00</wp:post_date_gmt>
    <content:encoded><![CDATA[<!-- wp:paragraph --><p>Hello</p>]]></content:encoded>
    <category domain="category" nicename="news">News</category>{meta}</item>'''


def wxr(*items):
    return '''<?xml version="1.0" encoding="UTF-8"?>
    <rss xmlns:wp="http://wordpress.org/export/1.2/" xmlns:content="http://purl.org/rss/1.0/modules/content/">
    <channel><link>https://example.org/studio/</link><wp:wxr_version>1.2</wp:wxr_version>''' + ''.join(items) + '</channel></rss>'


def meta(key, value):
    return f'<wp:postmeta><wp:meta_key>{key}</wp:meta_key><wp:meta_value><![CDATA[{value}]]></wp:meta_value></wp:postmeta>'


def png():
    # A valid 1x1 PNG fixture. These tests check evidence bookkeeping, not similarity.
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', 1, 1, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b'\0\xff\xff\xff')) + chunk(b'IEND', b'')


class Helpers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.export = self.root / 'export.xml'
        self.export.write_text(wxr(item('1')))

    def run_init(self, *extra, input_text=None):
        return subprocess.run([sys.executable, str(INIT), '--source-url', 'https://example.org/studio/',
                               '--output', str(self.root / 'site'), '--export', str(self.export), *extra],
                              input=input_text, capture_output=True, text=True)

    def test_admin_export_intake_can_start_without_a_local_export(self):
        result = subprocess.run([sys.executable, str(INIT), '--source-url', 'https://example.org/studio/',
                                 '--output', str(self.root / 'site'), '--export-from-admin',
                                 '--wordpress-admin-url', 'https://example.org/studio/custom-admin',
                                 '--forms-mode', 'none', '--non-interactive'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((self.root / 'site/migration/intake.json').read_text())
        self.assertIsNone(data['export_path'])
        self.assertEqual(data['export_source'], 'wordpress-admin')
        self.assertEqual(data['export_status'], 'pending-download')
        self.assertEqual(data['export_scope'], 'unconfirmed')
        self.assertEqual(data['export_admin_url'], 'https://example.org/studio/custom-admin')
        self.assertFalse(any(data['scope'].values()))
        self.assertIn('Export pending', result.stdout)
        self.assertIn('/exports/', (self.root / 'site/.gitignore').read_text())

    def test_blank_interactive_export_chooses_browser_download(self):
        result = subprocess.run([sys.executable, str(INIT), '--source-url', 'https://example.org',
                                 '--output', str(self.root / 'site'), '--forms-mode', 'none'],
                                input='\n', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((self.root / 'site/migration/intake.json').read_text())
        self.assertIsNone(data['export_path'])
        self.assertEqual(data['export_status'], 'pending-download')

    def test_local_export_and_browser_export_are_mutually_exclusive(self):
        result = self.run_init('--export-from-admin', '--forms-mode', 'none', '--non-interactive')
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / 'site').exists())

    def test_missing_file_is_not_misreported_as_a_download_or_silently_replaced(self):
        self.export.unlink()
        result = self.run_init('--forms-mode', 'none', '--non-interactive')
        self.assertEqual(result.returncode, 2)
        self.assertIn('--export-from-admin', result.stderr)
        self.assertFalse((self.root / 'site').exists())
        self.assertFalse(self.export.exists())

    def test_noninteractive_email_requires_explicit_recipient_without_writes(self):
        result = self.run_init('--non-interactive', '--forms-mode', 'email')
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / 'site').exists())

    def test_interactive_asks_for_destination_mailbox_and_defers_sender(self):
        result = self.run_init(input_text='email\nforms@example.org\n\n\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Approved contact form recipient', result.stdout)
        data = json.loads((self.root / 'site/migration/intake.json').read_text())
        self.assertEqual(data['forms']['recipients'], ['forms@example.org'])
        self.assertIsNone(data['forms']['sender'])
        self.assertFalse(any(data['scope'].values()))
        self.assertEqual(data['source_url'], 'https://example.org/studio')
        self.assertEqual(data['export_scope'], 'unconfirmed')

    def test_named_sender_and_ci_intent_are_saved_without_authorizing_deployment(self):
        result = self.run_init('--non-interactive', '--forms-mode', 'email',
                               '--contact-to', 'forms@example.org', '--sender', 'website@example.org',
                               '--sender-name', 'Éxample Studio Website', '--ci-mode', 'deploy-on-push')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((self.root / 'site/migration/intake.json').read_text())
        self.assertEqual(data['forms']['sender_name'], 'Éxample Studio Website')
        self.assertEqual(data['forms']['sender'], 'website@example.org')
        self.assertEqual(data['hosting']['ci']['mode'], 'deploy-on-push')
        self.assertIsNone(data['hosting']['ci']['repository'])
        self.assertFalse(any(data['scope'].values()))

    def test_sender_name_rejects_header_injection_and_inapplicable_form_mode(self):
        for mode, name in (('email', 'Website\r\nBcc: hidden@example.org'), ('none', 'Website')):
            recipients = ['--contact-to', 'forms@example.org'] if mode == 'email' else []
            result = self.run_init('--non-interactive', '--forms-mode', mode,
                                   *recipients, '--sender-name', name)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((self.root / 'site').exists())

    def test_repeated_init_does_not_reset_decisions(self):
        result = self.run_init('--non-interactive', '--forms-mode', 'none')
        self.assertEqual(result.returncode, 0, result.stderr)
        intake = self.root / 'site/migration/intake.json'
        before = intake.read_bytes()
        again = self.run_init('--non-interactive', '--forms-mode', 'none', '--authorize-deploy')
        self.assertEqual(again.returncode, 2)
        self.assertEqual(intake.read_bytes(), before)
        ignore = (self.root / 'site/.gitignore').read_text()
        self.assertIn('/migration/intake.json', ignore)
        self.assertIn('/migration/inventory.json', ignore)
        self.assertIn('/migration/lighthouse/', ignore)
        self.assertIn('**/.dev.vars', ignore)

    def test_header_injection_rejected_and_source_unchanged(self):
        before = self.export.read_bytes()
        result = self.run_init('--non-interactive', '--forms-mode', 'email', '--contact-to', 'ops@example.org\nBcc:x@example.org')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.export.read_bytes(), before)
        self.assertFalse((self.root / 'site').exists())

    def test_inventory_distinguishes_public_private_and_shared(self):
        self.export.write_text(wxr(item('1'), item('2', status='draft'), item('3', status='private'),
                                   item('4', kind='attachment', status='inherit'),
                                   item('5', kind='elementor_library'), item('6', kind='resource', link='https://example.org/studio/resource/')))
        before = self.export.read_bytes()
        data = inventory.inspect(self.export)
        self.assertEqual([row['id'] for row in data['items'] if row['public']], ['1', '6'])
        self.assertFalse(any(row['post_type'] == 'post' for row in data['counts']))
        self.assertEqual(data['items'][0]['route'], '/studio/about/')
        self.assertEqual(data['items'][0]['slug'], 'original-slug')
        self.assertEqual(data['items'][0]['title'], 'Example & title')
        self.assertTrue(any(w['type'] == 'classify-custom-type' for w in data['warnings']))
        self.assertEqual(self.export.read_bytes(), before)

    def test_inventory_retains_export_identity_and_warns_on_a_different_site(self):
        content = wxr(item('1')).replace('https://example.org/studio/', 'https://other.example.org/news/')
        content = content.replace('<channel>', '<channel><title>Other site</title>'
                                  '<wp:base_site_url>https://other.example.org/</wp:base_site_url>'
                                  '<wp:base_blog_url>https://other.example.org/news/</wp:base_blog_url>')
        self.export.write_text(content)
        data = inventory.inspect(self.export, source='https://example.org/studio')
        self.assertEqual(data['source_url'], 'https://example.org/studio')
        self.assertEqual(data['export_site']['title'], 'Other site')
        self.assertEqual(data['export_site']['channel_url'], 'https://other.example.org/news/')
        self.assertEqual(data['export_site']['base_site_url'], 'https://other.example.org/')
        self.assertEqual(data['export_site']['base_blog_url'], 'https://other.example.org/news/')
        self.assertTrue(any(w['type'] == 'export-site-mismatch' for w in data['warnings']))
        matching = inventory.inspect(self.export, source='https://other.example.org/news')
        self.assertFalse(any(w['type'] == 'export-site-mismatch' for w in matching['warnings']))

    def test_inventory_preserves_repeated_meta_and_nested_widgets(self):
        builder = json.dumps([{'elements': [{'widgetType': 'heading', 'elements': []}]}])
        metadata = meta('_elementor_data', builder) + meta('_yoast_wpseo_title', 'SEO') + meta('_yoast_wpseo_title', 'Repeated')
        self.export.write_text(wxr(item('1', meta=metadata)))
        data = inventory.inspect(self.export)
        self.assertEqual(data['widget_counts'], {'heading': 1})
        self.assertEqual(data['items'][0]['seo']['_yoast_wpseo_title'], ['SEO', 'Repeated'])
        self.assertIn('elementor', data['items'][0]['builders'])
        self.assertIn('gutenberg', data['items'][0]['builders'])

    def test_inventory_preserves_query_and_warns_slash_collisions(self):
        self.export.write_text(wxr(item('1', link='https://example.org/studio/?page_id=1'),
                                   item('2'), item('3', link='https://example.org/studio/about')))
        data = inventory.inspect(self.export)
        self.assertEqual(data['items'][0]['route'], '/studio/?page_id=1')
        self.assertTrue(any(w['type'] == 'route-collision' for w in data['warnings']))

    def test_inventory_duplicate_ids_entities_and_non_wxr_fail(self):
        for text in (wxr(item('1'), item('1')), '<rss><channel/></rss>', '<html><body>Sign in</body></html>',
                     '<!DOCTYPE rss [<!ENTITY evil "expanded">]>' + wxr()):
            self.export.write_text(text)
            with self.assertRaises(ValueError):
                inventory.inspect(self.export)

    def test_inventory_cannot_overwrite_export(self):
        before = self.export.read_bytes()
        result = subprocess.run([sys.executable, str(IMPORT), str(self.export), '--output', str(self.export)], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.export.read_bytes(), before)

    def evidence(self):
        views = {}
        for mode, width, height in [('desktop', 1440, 1000), ('mobile', 390, 844)]:
            views[mode] = {'width': width, 'height': height,
                           'review': {'status': 'pass', 'reviewed_at': '2026-11-06T15:00:00Z', 'notes': 'Synthetic bookkeeping fixture'}}
            for side, host in [('source', 'https://example.org'), ('target', 'http://127.0.0.1:4321')]:
                name = f'{mode}-{side}.png'
                (self.root / name).write_bytes(png())
                views[mode][side] = {'width': width, 'height': height, 'url': host + '/about/', 'screenshot': name}
            views[mode]['target'].update(overflow=False, broken_images=[])
        return {'routes': [{'url': '/about/', 'public': True}]}, {'schema_version': 1, 'pages': [{'route': '/about/', 'views': views}]}

    def test_complete_evidence_passes_but_missing_route_fails(self):
        source, manifest = self.evidence()
        self.assertEqual(parity.check(source, manifest, self.root), ([], 1))
        source['routes'].append({'url': '/contact/', 'public': True})
        self.assertIn('/contact/: missing page', parity.check(source, manifest, self.root)[0])

    def test_integrity_is_not_review_and_null_view_does_not_pass(self):
        source, manifest = self.evidence()
        view = manifest['pages'][0]['views']['desktop']
        for status in ('pending', 'fail', None):
            view['review']['status'] = status
            self.assertTrue(parity.check(source, manifest, self.root)[0])
        manifest['pages'][0]['views']['desktop'] = None
        self.assertTrue(parity.check(source, manifest, self.root)[0])

    def test_measured_viewport_broken_image_and_shared_screenshot_fail(self):
        source, manifest = self.evidence()
        for mutate in (lambda v: v['target'].update(width=800),
                       lambda v: v['target'].update(overflow=True),
                       lambda v: v['target'].update(broken_images=['missing.jpg']),
                       lambda v: v['target'].update(screenshot=v['source']['screenshot']),
                       lambda v: v['review'].update(reviewed_at='2026-11-06T15:00:00')):
            trial = copy.deepcopy(manifest)
            mutate(trial['pages'][0]['views']['desktop'])
            self.assertTrue(parity.check(source, trial, self.root)[0])

    def test_missing_invalid_and_escaping_capture_files_fail(self):
        source, manifest = self.evidence()
        file = self.root / 'desktop-source.png'
        for content in (b'', b'<html>not a screenshot</html>' * 5):
            file.write_bytes(content)
            self.assertTrue(parity.check(source, manifest, self.root)[0])
        file.unlink()
        self.assertTrue(parity.check(source, manifest, self.root)[0])
        manifest['pages'][0]['views']['desktop']['source']['screenshot'] = '../outside.png'
        self.assertTrue(parity.check(source, manifest, self.root)[0])


if __name__ == '__main__':
    unittest.main()
