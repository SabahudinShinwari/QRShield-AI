"""Local development backend for QRShield AI. Not a security-audited public service.

QSE1 crypto_core.py is copied unchanged from the uploaded original application.
Legacy routes are retained so original test_routes.py remains applicable.
"""
import base64
import io
import os
from pathlib import Path

import cv2
import numpy as np
import qrcode
from flask import Flask, jsonify, request, send_file, send_from_directory
from crypto_core import PayloadError, decrypt, encrypt
from url_analysis import URLInputError, inspect_url
from gemini_explainer import ExplanationUnavailable, configured, explain_findings
from ml_detector import ModelUnavailable, model_status, predict_pattern

FRONTEND_DIST = Path(__file__).resolve().parent.parent / 'frontend' / 'dist'
MAX_IMAGE_BYTES = 3 * 1024 * 1024
app = Flask(__name__, static_folder=None)
app.config['MAX_CONTENT_LENGTH'] = MAX_IMAGE_BYTES
app.json.ensure_ascii = False


@app.after_request
def privacy_headers(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


def _json_input():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise PayloadError('Expected JSON request.')
    return data


def _qr_bytes(payload):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=9, border=4)
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(fill_color='black', back_color='white')
    out = io.BytesIO()
    image.save(out, format='PNG')
    return out.getvalue()


def _encrypt_values():
    data = _json_input()
    payload = encrypt(data.get('message'), data.get('password'))
    return payload, _qr_bytes(payload)


@app.post('/encrypt')
def legacy_encrypt():
    try:
        _, png = _encrypt_values()
        return send_file(io.BytesIO(png), mimetype='image/png', as_attachment=True, download_name='encrypted_qr.png')
    except (PayloadError, qrcode.exceptions.DataOverflowError) as exc:
        message = str(exc) if isinstance(exc, PayloadError) else 'Message is too large for a QR code.'
        return jsonify(error=message), 400


@app.post('/api/encrypt')
def api_encrypt():
    try:
        payload, png = _encrypt_values()
        return jsonify(payload=payload, image=f'data:image/png;base64,{base64.b64encode(png).decode("ascii")}')
    except (PayloadError, qrcode.exceptions.DataOverflowError) as exc:
        message = str(exc) if isinstance(exc, PayloadError) else 'Message is too large for a QR code.'
        return jsonify(error=message), 400


def _scan_image():
    uploaded = request.files.get('image')
    if uploaded is None:
        raise PayloadError('Choose a QR image.')
    raw = uploaded.read(MAX_IMAGE_BYTES + 1)
    if len(raw) > MAX_IMAGE_BYTES:
        raise PayloadError('Image exceeds 3 MB.')
    if not (raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'\xff\xd8\xff')):
        raise PayloadError('Unsupported file format. Upload a PNG or JPEG image.')
    image = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise PayloadError('Invalid or corrupted image.')
    if image.shape[0] * image.shape[1] > 12_000_000:
        raise PayloadError('Image dimensions exceed the 12-megapixel limit.')
    value, _, _ = cv2.QRCodeDetector().detectAndDecode(image)
    if not value:
        raise PayloadError('No readable QR code found.')
    if len(value) > 6000:
        raise PayloadError('QR payload too large.')
    return value


@app.post('/scan')
@app.post('/api/scan')
def scan_route():
    try:
        return jsonify(payload=_scan_image())
    except PayloadError as exc:
        return jsonify(error=str(exc)), 400


@app.post('/decrypt')
@app.post('/api/decrypt')
def decrypt_route():
    try:
        data = _json_input()
        return jsonify(message=decrypt(data.get('payload'), data.get('password')))
    except PayloadError as exc:
        return jsonify(error=str(exc)), 400


@app.post('/api/analyze')
def analyze_url():
    try:
        return jsonify(inspect_url(_json_input().get('url')))
    except (PayloadError, URLInputError) as exc:
        return jsonify(error=str(exc)), 400


@app.get('/api/ml/status')
def ml_status():
    return jsonify(model_status())


@app.post('/api/ml/predict')
def ml_predict():
    try:
        # Intentional explicit invocation only. No password/message or QR payload accepted.
        url = _json_input().get('url')
        inspect_url(url)  # shared input validation; do not fetch destination
        return jsonify(predict_pattern(url))
    except (PayloadError, URLInputError) as exc:
        return jsonify(error=str(exc)), 400
    except ModelUnavailable as exc:
        return jsonify(error=str(exc)), 503


@app.post('/api/ai/explain')
def explain_url():
    try:
        data = _json_input()
        if data.get('consent') is not True:
            return jsonify(error='Explicit consent is required before sending findings to Gemini.'), 400
        # Recompute on the server: never trust caller-provided indicator text.
        result = inspect_url(data.get('url'))
        explanation = explain_findings(result)
        return jsonify(explanation=explanation, provider='Gemini', shared='Hostname, scheme and structural findings only')
    except (PayloadError, URLInputError) as exc:
        return jsonify(error=str(exc)), 400
    except ExplanationUnavailable as exc:
        return jsonify(error=str(exc)), 503


@app.get('/api/health')
def health():
    return jsonify(status='ok', mode='local-development', ai_model='trained-local' if model_status()['ready'] else 'not-installed', ml=model_status(), url_analysis='offline-heuristics', gemini_explanations='configured' if configured() else 'not-configured')


@app.get('/')
def index():
    if (FRONTEND_DIST / 'index.html').is_file():
        return send_from_directory(FRONTEND_DIST, 'index.html')
    return jsonify(message='QRShield API is running. Run the React frontend with npm run dev on port 5173.'), 200


@app.get('/<path:filename>')
def frontend_asset(filename):
    # Only serve build files under dist; do not expose backend files.
    if not FRONTEND_DIST.is_dir():
        return jsonify(error='Frontend not built. Use npm run dev.'), 404
    target = (FRONTEND_DIST / filename).resolve()
    if not target.is_relative_to(FRONTEND_DIST.resolve()):
        return jsonify(error='Not found.'), 404
    if target.is_file():
        return send_from_directory(FRONTEND_DIST, filename)
    return jsonify(error='Not found.'), 404


@app.errorhandler(413)
def too_large(_):
    return jsonify(error='Upload exceeds 3 MB.'), 413


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
