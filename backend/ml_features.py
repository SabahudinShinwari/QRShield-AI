"""Pure, offline lexical URL features shared by training and inference.

No URL is visited, resolved, or sent to third parties by this module.
Never use UCI's webpage-derived columns: inference has only the raw URL.
"""
from collections import Counter
from math import log2
import ipaddress
import re
from urllib.parse import urlsplit

from url_analysis import inspect_url

TOKEN_RE = re.compile(r'login|signin|verify|account|password|reset|secure|update|billing|wallet|payment', re.I)
ENCODED_RE = re.compile(r'%[0-9a-fA-F]{2}')


def lexical_features(url: str) -> dict[str, float]:
    """Validate with the same parser as the UI; extract numeric lexical features."""
    inspected = inspect_url(url)
    parsed = urlsplit(url)
    host = inspected['hostname']
    path_query = (parsed.path or '') + ('?' + parsed.query if parsed.query else '')
    counts = Counter(url.lower())
    total = max(len(url), 1)
    entropy = -sum((n / total) * log2(n / total) for n in counts.values())
    try:
        ipaddress.ip_address(host)
        host_is_ip = 1
    except ValueError:
        host_is_ip = 0
    return {
        'url_length': float(len(url)),
        'hostname_length': float(len(host)),
        'path_query_length': float(len(path_query)),
        'hostname_labels': float(len(host.split('.'))),
        'host_is_ip': float(host_is_ip),
        'https': float(parsed.scheme.lower() == 'https'),
        'has_userinfo': float(parsed.username is not None or parsed.password is not None),
        'nonstandard_port': float(parsed.port is not None and parsed.port not in (80, 443)),
        'digit_count': float(sum(c.isdigit() for c in url)),
        'digit_ratio': float(sum(c.isdigit() for c in url) / total),
        'hyphen_count': float(url.count('-')),
        'at_count': float(url.count('@')),
        'dot_count': float(url.count('.')),
        'slash_count': float(url.count('/')),
        'question_count': float(url.count('?')),
        'equals_count': float(url.count('=')),
        'ampersand_count': float(url.count('&')),
        'percent_encoded_count': float(len(ENCODED_RE.findall(url))),
        'path_depth': float(sum(bool(seg) for seg in parsed.path.split('/'))),
        'punycode': float('xn--' in host),
        'suspicious_token_count': float(len(TOKEN_RE.findall(url))),
        'character_entropy': float(entropy),
        'offline_rule_count': float(len(inspected['indicators'])),
    }
