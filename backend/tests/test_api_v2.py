"""New API contract tests in addition to the preserved original tests."""
import base64
import io
from app import app


def test_health_describes_actual_capabilities():
    with app.test_client() as client:
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.json['ai_model'] in ('not-installed', 'trained-local')
        assert 'ml' in response.json
        assert response.json['url_analysis'] == 'offline-heuristics'


def test_new_encrypt_scan_decrypt_roundtrip():
    with app.test_client() as client:
        encrypted = client.post('/api/encrypt', json={'message': 'Hello 🔐', 'password': 'strong-demo-password'})
        assert encrypted.status_code == 200
        body = encrypted.json
        assert body['payload'].startswith('QSE1:')
        assert 'Hello 🔐' not in body['payload']
        assert body['image'].startswith('data:image/png;base64,')
        png = base64.b64decode(body['image'].split(',', 1)[1])
        assert png.startswith(b'\x89PNG\r\n\x1a\n')
        scanned = client.post('/api/scan', data={'image': (io.BytesIO(png), 'generated.png')}, content_type='multipart/form-data')
        assert scanned.status_code == 200
        assert scanned.json['payload'] == body['payload']
        decrypted = client.post('/api/decrypt', json={'payload': body['payload'], 'password': 'strong-demo-password'})
        assert decrypted.status_code == 200
        assert decrypted.json['message'] == 'Hello 🔐'
        assert decrypted.headers['Cache-Control'] == 'no-store'


def test_wrong_password_and_invalid_json():
    with app.test_client() as client:
        encrypted = client.post('/api/encrypt', json={'message': 'Hi', 'password': 'right'}).json
        wrong = client.post('/api/decrypt', json={'payload': encrypted['payload'], 'password': 'wrong'})
        assert wrong.status_code == 400
        assert 'message' not in wrong.json
        malformed = client.post('/api/encrypt', data='not-json', content_type='text/plain')
        assert malformed.status_code == 400


def test_no_persistent_history_routes():
    with app.test_client() as client:
        assert client.get('/api/history').status_code == 404
