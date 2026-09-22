"""Versioned password-encrypted QR payload. No plaintext or password is serialized."""
import base64
import json
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.exceptions import InvalidTag

PREFIX = 'QSE1:'
MAX_MESSAGE_BYTES = 400
MAX_PAYLOAD_CHARS = 6000
SALT_BYTES = 16
NONCE_BYTES = 12
# Fixed, reviewed parameters: do not accept attacker-controlled KDF work factors.
SCRYPT_N, SCRYPT_R, SCRYPT_P = 2**14, 8, 1
AAD = b'QSE1|scrypt|N=16384|r=8|p=1|AES-256-GCM'

class PayloadError(ValueError):
    pass

def _encode(data):
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')

def _decode(value, expected=None):
    if not isinstance(value, str) or not value or len(value) > MAX_PAYLOAD_CHARS:
        raise PayloadError('Invalid encoded payload.')
    try:
        import re
        if not re.fullmatch(r'[A-Za-z0-9_-]+', value):
            raise ValueError('Invalid alphabet')
        raw = base64.b64decode(value + '=' * (-len(value) % 4), altchars=b'-_', validate=True)
        if _encode(raw) != value:
            raise ValueError('Noncanonical encoding')
    except (ValueError, base64.binascii.Error) as exc:
        raise PayloadError('Invalid encoded payload.') from exc
    if expected is not None and len(raw) != expected:
        raise PayloadError('Invalid payload field length.')
    return raw

def _key(password, salt):
    if not isinstance(password, str) or not password or len(password.encode('utf-8')) > 1024:
        raise PayloadError('Password must contain 1–1024 UTF-8 bytes.')
    return Scrypt(salt=salt, length=32, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P).derive(password.encode('utf-8'))

def encrypt(message, password):
    if not isinstance(message, str):
        raise PayloadError('Message must be text.')
    raw = message.encode('utf-8')
    if not raw or len(raw) > MAX_MESSAGE_BYTES:
        raise PayloadError(f'Message must contain 1–{MAX_MESSAGE_BYTES} UTF-8 bytes.')
    salt, nonce = secrets.token_bytes(SALT_BYTES), secrets.token_bytes(NONCE_BYTES)
    sealed = AESGCM(_key(password, salt)).encrypt(nonce, raw, AAD)
    fields = {'s': _encode(salt), 'n': _encode(nonce), 'c': _encode(sealed)}
    return PREFIX + json.dumps(fields, separators=(',', ':'), sort_keys=True)

def decrypt(payload, password):
    if not isinstance(payload, str) or len(payload) > MAX_PAYLOAD_CHARS or not payload.startswith(PREFIX):
        raise PayloadError('Unsupported or invalid encrypted QR format.')
    try:
        fields = json.loads(payload[len(PREFIX):])
        if not isinstance(fields, dict) or set(fields) != {'s', 'n', 'c'}:
            raise ValueError('Invalid fields')
        salt = _decode(fields['s'], SALT_BYTES)
        nonce = _decode(fields['n'], NONCE_BYTES)
        sealed = _decode(fields['c'])
        if not 17 <= len(sealed) <= MAX_MESSAGE_BYTES + 16:
            raise ValueError('Invalid ciphertext size')
    except (ValueError, TypeError, KeyError) as exc:
        raise PayloadError('Malformed encrypted QR payload.') from exc
    try:
        raw = AESGCM(_key(password, salt)).decrypt(nonce, sealed, AAD)
        return raw.decode('utf-8')
    except (InvalidTag, UnicodeDecodeError) as exc:
        raise PayloadError('Decryption failed: incorrect password or altered QR payload.') from exc
