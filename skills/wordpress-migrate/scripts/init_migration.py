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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-url')
    parser.add_argument('--output', help='Separate destination site directory, not this toolkit')
    parser.add_argument('--export', dest='export_path', help='Local WXR path; never copied or changed')
    parser.add_argument('--forms-mode', choices=('email', 'preserve', 'none', 'undecided'))
    parser.add_argument('--contact-to', action='append', default=[], help='Repeat for multiple approved recipients')
    parser.add_argument('--sender', help='Verified sender; may remain pending during local implementation')
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
        export_path = Path(ask(args.export_path, 'WordPress WXR export path')).expanduser().resolve()
        if not export_path.is_file():
            raise ValueError('Export path must be an existing local file; request it before dependent import work.')
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
        if mode != 'email' and (recipients or sender):
            raise ValueError('Recipient/sender flags require --forms-mode email.')
        intake = output / 'migration/intake.json'
        if intake.exists():
            raise ValueError('Intake already exists; resume or edit it instead of resetting decisions.')
        if output.exists() and not output.is_dir():
            raise ValueError('Destination is not a directory.')
        data = {
            'schema_version': 1, 'source_url': source,
            'export_path': str(export_path), 'workspace': str(output),
            'export_scope': 'unconfirmed', 'fidelity': 'close-to-source',
            'forms': {'mode': mode, 'recipients': recipients, 'sender': sender,
                      'per_form_routing': {}, 'workflow_decision': 'pending'},
            'hosting': {'target': 'cloudflare-pages', 'account': None, 'project': None,
                        'functional_origins': []},
            'scope': {name: getattr(args, 'authorize_' + name) for name in
                      ('deploy', 'push', 'dns_cutover', 'live_email_test')}
        }
        intake.parent.mkdir(parents=True, exist_ok=True)
        ignore = output / '.gitignore'
        existing = ignore.read_text() if ignore.exists() else ''
        private_paths = ('/migration/intake.json', '/migration/inventory.json',
                         '/migration/parity/', '/wordpress/', '/exports/',
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
    except (ValueError, OSError, EOFError) as exc:
        parser.exit(2, f'Intake error: {exc}\n')


if __name__ == '__main__':
    main()
