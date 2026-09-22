"""Offline URL triage and privacy boundaries; does not require internet."""
import pytest
from url_analysis import URLInputError, inspect_url
from gemini_explainer import ExplanationUnavailable, explain_findings


def titles(url):
    return [i['title'] for i in inspect_url(url)['indicators']]


def test_normal_https_is_not_called_safe():
    result = inspect_url('https://example.org/docs')
    assert result['caution'] == 'no-obvious-flags'
    assert result['indicators'] == []
    assert 'does not establish' in result['disclaimer']
    assert 'rules only' in result['method']


def test_http_userinfo_ip_and_shorteners():
    result = inspect_url('http://login.example.org@192.0.2.10:8080/path')
    assert result['caution'] == 'extra-caution'
    assert {'Unencrypted connection', 'Misleading @ sign / credentials', 'IP-address destination', 'Non-standard port'} <= set(titles('http://login.example.org@192.0.2.10:8080/path'))
    assert 'Shortened link' in titles('https://bit.ly/abc')


def test_punycode_detected_without_network():
    assert 'Internationalized hostname' in titles('https://xn--e1afmkfd.example/')


@pytest.mark.parametrize('bad', [None, '', 'example.org', 'javascript:alert(1)', 'https://exa mple.com', 'https://example.com\n@evil.org', 'https://example.org:99999/', 'https://-bad.example.org', 'https://example.org/' + 'a'*2050])
def test_reject_bad_input(bad):
    with pytest.raises(URLInputError):
        inspect_url(bad)


def test_no_key_does_not_call_provider(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    with pytest.raises(ExplanationUnavailable, match='not configured'):
        explain_findings(inspect_url('https://example.org'))


def test_gemini_only_receives_hostname_and_indicators(monkeypatch):
    from gemini_explainer import explain_findings
    import json
    monkeypatch.setenv('GEMINI_API_KEY', 'test-do-not-use')
    captured = {}

    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *_): return None
        def read(self, _): return json.dumps({'candidates':[{'content':{'parts':[{'text':'Verify independently.'}]}}]}).encode()

    def fake_urlopen(req, timeout):
        captured['request'] = req
        captured['timeout'] = timeout
        return FakeResponse()

    monkeypatch.setattr('gemini_explainer.request.urlopen', fake_urlopen)
    result = inspect_url('https://example.org/private/sensitive?token=SECRET')
    assert explain_findings(result) == 'Verify independently.'
    outbound = captured['request'].data.decode()
    assert 'example.org' in outbound
    assert '/private/' not in outbound and 'SECRET' not in outbound
    assert 'test-do-not-use' == captured['request'].get_header('X-goog-api-key')
