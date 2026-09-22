"""Model integration tests; no synthetic evaluation or fabricated deployment weights."""
import json
from pathlib import Path

import pytest

from ml_features import lexical_features
from ml_detector import ModelUnavailable
from train_phishing_model import load_clean_csv, measurements


def test_features_are_deterministic_and_local(monkeypatch):
    import urllib.request
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **k: (_ for _ in ()).throw(AssertionError('unexpected network')))
    a = lexical_features('https://example.org/login?user=abc')
    assert a == lexical_features('https://example.org/login?user=abc')
    assert a['https'] == 1
    assert a['suspicious_token_count'] >= 1
    assert a['url_length'] == len('https://example.org/login?user=abc')


def test_invalid_url_is_rejected():
    from url_analysis import URLInputError
    with pytest.raises(URLInputError):
        lexical_features('file:///etc/passwd')


def test_no_trained_model_means_503(monkeypatch, tmp_path):
    import ml_detector
    monkeypatch.setattr(ml_detector, 'MODEL_FILE', tmp_path / 'missing.joblib')
    monkeypatch.setattr(ml_detector, 'META_FILE', tmp_path / 'missing.json')
    app = pytest.importorskip("app").app
    with app.test_client() as client:
        assert client.get('/api/ml/status').json['ready'] is False
        r = client.post('/api/ml/predict', json={'url': 'https://example.org'})
        assert r.status_code == 503
        assert 'trained model' in r.json['error'].lower()


def test_ml_endpoint_validates_input():
    app = pytest.importorskip("app").app
    with app.test_client() as client:
        assert client.post('/api/ml/predict', json={'url': 'file:///etc/passwd'}).status_code == 400


def test_rejects_conflicting_dataset_labels(tmp_path):
    # Tiny fixture deliberately cannot be trained; verifies data hygiene only.
    rows = ['URL,label', 'https://same.example/,0', 'https://same.example/,1']
    rows += [f'https://{i}.example.org/path,{i%2}' for i in range(1010)]
    file = tmp_path / 'urls.csv'
    file.write_text('\n'.join(rows) + '\n', encoding='utf-8')
    # This fixture only has one registered domain, and must NOT be evaluated as real training data.
    # loader only; splitting would reject inadequate group distribution.
    # tldextract may not be installed in minimal test environments, so test loader's early gates separately.
    import train_phishing_model
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(train_phishing_model, 'domain_group', lambda url: url.split('/')[2])
    try:
        urls, labels, groups, quality = load_clean_csv(file)
        assert 'https://same.example/' not in urls
        assert quality['conflicting_urls_dropped'] == 1
        assert len(urls) == 1010
    finally:
        monkeypatch.undo()


def test_model_metrics_confusion_matrix_math():
    import numpy as np
    m = measurements(np.array([0, 0, 1, 1]), np.array([0.1, 0.7, 0.4, 0.9]), 0.5)
    assert m['confusion_matrix'] == {'tn': 1, 'fp': 1, 'fn': 1, 'tp': 1}
    assert m['precision_phishing'] == 0.5


def test_valid_fake_model_endpoint_contract_without_fake_deployed_model(monkeypatch):
    app = pytest.importorskip('app').app
    import app as app_module
    monkeypatch.setattr(app_module, 'predict_pattern', lambda u: {
        'signal': 'phishing-like', 'dataset': 'fixture-only', 'method': 'test stub', 'disclaimer': 'not a safety verdict',
    })
    with app.test_client() as client:
        r = client.post('/api/ml/predict', json={'url': 'https://example.org/login'})
        assert r.status_code == 200
        assert r.json['signal'] == 'phishing-like'
        assert 'probability' not in r.json


def test_registered_domain_group_is_shared_by_subdomains_if_tldextract_available():
    pytest.importorskip('tldextract')
    from train_phishing_model import domain_group
    assert domain_group('https://help.accounts.example.co.uk/path') == domain_group('https://example.co.uk/')
