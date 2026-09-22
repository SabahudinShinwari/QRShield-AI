import json
import pytest
from crypto_core import encrypt, decrypt, PayloadError, PREFIX, MAX_MESSAGE_BYTES

def test_round_trip_unicode():
    text='Hello বাংলা 🔐'
    assert decrypt(encrypt(text,'correct horse battery staple'),'correct horse battery staple') == text

def test_wrong_password():
    with pytest.raises(PayloadError, match='Decryption failed'):
        decrypt(encrypt('secret','right'),'wrong')

def test_tampered_ciphertext():
    payload=encrypt('secret','right')
    data=json.loads(payload[len(PREFIX):]); value=data['c']; data['c']=('A' if value[0]!='A' else 'B')+value[1:]
    with pytest.raises(PayloadError):
        decrypt(PREFIX+json.dumps(data),'right')

def test_fresh_randomness():
    a=json.loads(encrypt('same','same')[len(PREFIX):]); b=json.loads(encrypt('same','same')[len(PREFIX):])
    assert a['s'] != b['s'] and a['n'] != b['n'] and a['c'] != b['c']

def test_no_plaintext_password_in_payload():
    payload=encrypt('visible-secret','password-secret')
    assert 'visible-secret' not in payload and 'password-secret' not in payload

def test_limits_and_malformed():
    with pytest.raises(PayloadError): encrypt('x'*(MAX_MESSAGE_BYTES+1),'pw')
    with pytest.raises(PayloadError): encrypt('','pw')
    with pytest.raises(PayloadError): decrypt('not-our-qr','pw')
