import io
import json

import cv2
import numpy as np
import pytest

from app import app
from crypto_core import encrypt


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def upload(client, content, filename):
    return client.post('/scan', data={'image': (io.BytesIO(content), filename)}, content_type='multipart/form-data')


def test_encrypt_and_decrypt_endpoints(client):
    response = client.post('/encrypt', json={'message': 'Hello', 'password': 'test-password'})
    assert response.status_code == 200
    assert response.mimetype == 'image/png'
    payload = encrypt('Hello', 'test-password')
    result = client.post('/decrypt', json={'payload': payload, 'password': 'test-password'})
    assert result.json['message'] == 'Hello'


def test_encrypt_rejects_oversize_utf8(client):
    response = client.post('/encrypt', json={'message': '😀' * 101, 'password': 'pw'})
    assert response.status_code == 400
    assert '400 UTF-8 bytes' in response.json['error']


def test_decrypt_rejects_wrong_password(client):
    response = client.post('/decrypt', json={'payload': encrypt('secret', 'right'), 'password': 'wrong'})
    assert response.status_code == 400
    assert 'message' not in response.json


def test_upload_rejects_non_image(client):
    response = upload(client, b'This is not an image', 'fake.png')
    assert response.status_code == 400
    assert 'Unsupported file format' in response.json['error']


def test_upload_rejects_corrupted_png(client):
    response = upload(client, b'\x89PNG\r\n\x1a\nnot-real-png', 'fake.png')
    assert response.status_code == 400
    assert 'corrupted' in response.json['error']


def test_upload_rejects_oversize(client):
    response = upload(client, b'0' * (3 * 1024 * 1024 + 1), 'huge.png')
    assert response.status_code in (400, 413)
    assert '3 MB' in response.json['error']


def test_upload_valid_image_without_qr(client):
    ok, png = cv2.imencode('.png', np.full((100, 100, 3), 255, dtype=np.uint8))
    assert ok
    response = upload(client, png.tobytes(), 'blank.png')
    assert response.status_code == 400
    assert response.json['error'] == 'No readable QR code found.'
