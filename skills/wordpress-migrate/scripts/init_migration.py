#!/usr/bin/env python3
"""Collect per-site decisions without generating an app or contacting services."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


def source_url(value):
    parts = urlsplit(value.strip())
    if (parts.scheme not in ('http', 'https') or not parts.hostname
            or parts.username or parts.password or parts.query or parts.fragment):
        raise ValueError('Source must be an http(s) site URL without credentials, query or fragment.')
    try:
        parts.port
    except ValueError as exc:
        raise ValueError('Source URL has an invalid port.') from exc
    return value.strip().rstrip('/')


def email(value):
    value = value.strip()
    if not re.fullmatch(r'[^\s@<>\x00-\x1f]+@[^\s@<>\x00-\x1f]+\.[^\s@<>\x00-\x1f]+', value):
        raise ValueError('Use a mailbox address without a display name or control characters.')
    return value


def display_name(value):
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError('Sender name cannot contain control characters.')
    value = value.strip()
    if not value or len(value) > 200:
        raise ValueError('Sender name must contain 1–200 characters.')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-url')
    parser.add_argument('--output', help='Separate destination site directory, not this toolkit')
    export_choice = parser.add_mutually_exclusive_group()
    export_choice.add_argument('--export', dest='export_path', help='Local WXR path; never copied or changed')
    export_choice.add_argument('--export-from-admin', action='store_true',
                               help='Record a pending browser download from WordPress admin; agent performs it')
    parser.add_argument('--wordpress-admin-url', help='Optional admin starting URL without credentials/session parameters')
    parser.add_argument('--forms-mode', choices=('email', 'preserve', 'none', 'undecided'))
    parser.add_argument('--contact-to', action='append', default=[], help='Repeat for multiple approved recipients')
    parser.add_argument('--sender', help='Verified sender; may remain pending during local implementation')
    parser.add_argument('--sender-name', help='Friendly sender display name; separate from sender mailbox')
    parser.add_argument('--ci-mode', choices=('undecided', 'validation-only', 'deploy-on-push'), default='undecided',
                        help='Record CI intent without provisioning credentials or deploying')
    parser.add_argument('--non-interactive', action='store_true', help='Require answers via flags; never read stdin')
    for action in ('deploy', 'push', 'dns-cutover', 'live-email-test'):
        parser.add_argument('--authorize-' + action, action='store_true',
                            help='Record authorization already given by the user')
    args = parser.parse_args()

    def ask(value, prompt, required=True, default=None):
        if value:
            return value
        if args.non_interactive:
            if required:
                raise ValueError(f'Missing {prompt}; supply the corresponding flag.')
            return default
        answer = input(prompt + (f' [{default}]' if default else '') + ': ').strip()
        if not answer and required and default is None:
            raise ValueError(f'{prompt} is required.')
        return answer or default

    try:
        source = source_url(ask(args.source_url, 'Source WordPress URL'))
        output = Path(ask(args.output, 'Destination site directory')).expanduser().resolve()
        toolkit = Path(__file__).resolve().parents[3]
        if output == toolkit or toolkit in output.parents or output in toolkit.parents:
            raise ValueError('Choose a separate destination outside this toolkit.')
        export_value = args.export_path
        if not args.export_from_admin:
            if args.non_interactive and not export_value:
                raise ValueError('Supply --export with a local file or --export-from-admin for a browser download.')
            export_value = ask(export_value, 'WordPress WXR export path (blank to download through WordPress admin)',
                               required=False)
        export_path = Path(export_value).expanduser().resolve() if export_value else None
        if export_path is not None and not export_path.is_file():
            raise ValueError('Export path must exist; use --export-from-admin if a fresh browser export is needed.')
        admin_url = source_url(args.wordpress_admin_url) if args.wordpress_admin_url else None
        if admin_url and export_path is not None:
            raise ValueError('--wordpress-admin-url requires the browser export choice, not a local file.')
        mode = ask(args.forms_mode, 'Form mode: email, preserve, none, undecided', default='email')
        if mode not in ('email', 'preserve', 'none', 'undecided'):
            raise ValueError('Invalid form mode.')
        recipients = args.contact_to
        if mode == 'email' and not recipients:
            recipients = [ask(None, 'Approved contact form recipient email')]
        recipients = [email(item) for item in recipients]
        sender = args.sender
        if mode == 'email' and not args.non_interactive:
            sender = ask(sender, 'Verified sender email (blank to configure later)', required=False)
        sender = email(sender) if sender else None
        name = args.sender_name
        if mode == 'email' and not args.non_interactive:
            name = ask(name, 'Friendly sender name (blank to configure later)', required=False)
        name = display_name(name) if name is not None else None
        if mode != 'email' and (recipients or sender or name):
            raise ValueError('Recipient/sender/name flags require --forms-mode email.')
        intake = output / 'migration/intake.json'
        if intake.exists():
            raise ValueError('Intake already exists; resume or edit it instead of resetting decisions.')
        if output.exists() and not output.is_dir():
            raise ValueError('Destination is not a directory.')
        data = {
            'schema_version': 1, 'source_url': source,
            'export_path': str(export_path) if export_path is not None else None,
            'export_source': 'provided-file' if export_path is not None else 'wordpress-admin',
            'export_status': 'available' if export_path is not None else 'pending-download',
            'export_admin_url': admin_url, 'workspace': str(output),
            'export_scope': 'unconfirmed', 'fidelity': 'close-to-source',
            'forms': {'mode': mode, 'recipients': recipients, 'sender': sender, 'sender_name': name,
                      'per_form_routing': {}, 'workflow_decision': 'pending'},
            'hosting': {'target': 'cloudflare-pages', 'account': None, 'project': None,
                        'functional_origins': [],
                        'ci': {'provider': 'github-actions', 'mode': args.ci_mode,
                               'repository': None, 'production_branch': None}},
            'scope': {name: getattr(args, 'authorize_' + name) for name in
                      ('deploy', 'push', 'dns_cutover', 'live_email_test')}
        }
        intake.parent.mkdir(parents=True, exist_ok=True)
        ignore = output / '.gitignore'
        existing = ignore.read_text() if ignore.exists() else ''
        private_paths = ('/migration/intake.json', '/migration/inventory.json',
                         '/migration/parity/', '/migration/lighthouse/', '/wordpress/', '/exports/',
                         '/src/content/drafts/', '/.env', '/.env.*', '/.dev.vars',
                         '/.dev.vars.*', '**/.dev.vars', '**/.dev.vars.*')
        missing = [item for item in private_paths if item not in existing.splitlines()]
        if missing:
            with ignore.open('a') as stream:
                stream.write(('\n' if existing and not existing.endswith('\n') else '')
                             + '\n# Private migration inputs and evidence\n' + '\n'.join(missing) + '\n')
        # Exclusive creation protects an existing intake even across concurrent runs.
        with intake.open('x') as stream:
            json.dump(data, stream, indent=2)
            stream.write('\n')
        print(f'Created {intake}. Continue with wordpress-migrate; nothing deployed or sent.')
        if export_path is None:
            print('Export pending: use the WordPress admin browser workflow, validate the download, then update intake.')
    except (ValueError, OSError, EOFError) as exc:
        parser.exit(2, f'Intake error: {exc}\n')


if __name__ == '__main__':
    main()
