"""Offline URL-structure triage. Heuristics, NOT AI, reputation, or a safety verdict.

No DNS lookups or outbound requests. Never execute or open the submitted URL.
"""
import ipaddress
import re
from urllib.parse import urlsplit

MAX_URL_CHARS = 2048
SHORTENERS = frozenset({
    'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly',
    'cutt.ly', 'rebrand.ly', 'shorturl.at', 'tiny.cc', 'rb.gy', 'lnkd.in',
})


class URLInputError(ValueError):
    """Invalid URL input, with a safe user-facing message."""


def _flag(title: str, detail: str, severity: str) -> dict:
    return {'title': title, 'detail': detail, 'severity': severity}


def inspect_url(value: str) -> dict:
    if not isinstance(value, str) or not value or len(value) > MAX_URL_CHARS:
        raise URLInputError('Enter one URL, up to 2,048 characters.')
    # urlsplit silently strips certain control characters. Reject them before parsing.
    if value != value.strip() or any(ord(ch) < 33 or ord(ch) == 127 for ch in value):
        raise URLInputError('Enter a URL without spaces or control characters.')
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
        port = parsed.port  # Access validates port syntax and range.
    except ValueError as exc:
        raise URLInputError('The URL has an invalid host or port.') from exc
    if parsed.scheme.lower() not in ('http', 'https') or not hostname or not parsed.netloc:
        raise URLInputError('Enter a full HTTP or HTTPS URL, including https:// or http://.')
    if len(hostname) > 253:
        raise URLInputError('The hostname is too long.')
    try:
        ascii_hostname = hostname.encode('idna').decode('ascii').lower()
    except UnicodeError as exc:
        raise URLInputError('The hostname is invalid.') from exc
    if not re.fullmatch(r'[a-z0-9.\-:\[\]]+', ascii_hostname):
        raise URLInputError('The hostname contains unsupported characters.')
    if not (parsed.username is None and parsed.password is None):
        # User-info is valid syntax but suspicious, so it is an indicator, not an error.
        pass
    labels = ascii_hostname.rstrip('.').split('.')
    try:
        ipaddress.ip_address(ascii_hostname)
        is_ip = True
    except ValueError:
        is_ip = False
        if not all(label and len(label) <= 63 and not label.startswith('-') and not label.endswith('-') for label in labels):
            raise URLInputError('The hostname is invalid.')
    indicators: list[dict] = []
    if parsed.scheme.lower() == 'http':
        indicators.append(_flag('Unencrypted connection', 'HTTP does not provide HTTPS transport protection.', 'elevated'))
    if parsed.username is not None or parsed.password is not None:
        indicators.append(_flag('Misleading @ sign / credentials', 'A URL with user information can disguise which host the browser will actually visit.', 'elevated'))
    if is_ip:
        indicators.append(_flag('IP-address destination', 'The host is an IP address rather than a recognizable domain name.', 'attention'))
    if any(label.startswith('xn--') for label in labels):
        indicators.append(_flag('Internationalized hostname', 'Punycode can be legitimate, but visually similar domain names warrant extra checking.', 'attention'))
    if not is_ip and len(labels) >= 5:
        indicators.append(_flag('Many hostname levels', 'An unusually deep hostname may obscure the registrable domain.', 'attention'))
    if ascii_hostname in SHORTENERS or any(ascii_hostname.endswith('.' + d) for d in SHORTENERS):
        indicators.append(_flag('Shortened link', 'A link shortener hides the final destination; do not assume where it redirects.', 'attention'))
    if port is not None and port not in (80, 443):
        indicators.append(_flag('Non-standard port', 'This URL uses an uncommon port; verify that it is expected.', 'attention'))
    if len(value) > 120:
        indicators.append(_flag('Long URL', 'An unusually long URL can be harder to inspect manually.', 'attention'))
    if re.search(r'%[0-9a-fA-F]{2}', parsed.path) or re.search(r'%[0-9a-fA-F]{2}', parsed.netloc):
        indicators.append(_flag('Encoded URL characters', 'Percent-encoded content can make a URL harder to read. Encoding alone is not malicious.', 'attention'))
    if '\\' in value:
        indicators.append(_flag('Backslash in URL', 'Backslashes can be interpreted inconsistently; avoid following ambiguous links.', 'elevated'))

    caution = 'extra-caution' if any(f['severity'] == 'elevated' for f in indicators) else ('review' if indicators else 'no-obvious-flags')
    headline = {
        'extra-caution': 'Extra caution recommended',
        'review': 'Review these URL characteristics',
        'no-obvious-flags': 'No obvious structural indicators found',
    }[caution]
    return {
        'hostname': ascii_hostname,
        'scheme': parsed.scheme.lower(),
        'caution': caution,
        'headline': headline,
        'indicators': indicators,
        'method': 'Offline rules only — not machine learning or a reputation check.',
        'disclaimer': 'This does not establish that a URL is safe or malicious. No destination was visited or checked against threat feeds.',
        'guidance': 'Verify the domain independently and avoid entering credentials or downloading files from unexpected QR links.',
    }
