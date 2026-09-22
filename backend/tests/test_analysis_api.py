"""Flask endpoint tests, run after pip install -r requirements.txt."""
from app import app


def test_analysis_api_has_no_safe_verdict():
    with app.test_client() as client:
        r = client.post('/api/analyze', json={'url':'https://example.org/docs'})
        assert r.status_code == 200
        assert r.json['caution'] == 'no-obvious-flags'
        assert 'does not establish' in r.json['disclaimer']


def test_analysis_validates_url_and_consent():
    with app.test_client() as client:
        assert client.post('/api/analyze', json={'url':'file:///etc/passwd'}).status_code == 400
        denied = client.post('/api/ai/explain', json={'url':'https://example.org', 'consent':False})
        assert denied.status_code == 400
        assert 'consent' in denied.json['error'].lower()


def test_no_key_explanation_is_disabled(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    with app.test_client() as client:
        r = client.post('/api/ai/explain', json={'url':'https://example.org', 'consent':True})
        assert r.status_code == 503
        assert 'not configured' in r.json['error'].lower()
