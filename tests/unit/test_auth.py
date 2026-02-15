from src.modules.auth.service import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    password = 'mysecretpass'
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_verify_wrong_password():
    hashed = hash_password('correct')
    assert not verify_password('wrong', hashed)


def test_create_and_decode_token():
    token = create_access_token(user_id='abc-123', role='RESTAURANT')
    payload = decode_access_token(token)
    assert payload['sub'] == 'abc-123'
    assert payload['role'] == 'RESTAURANT'
    assert 'exp' in payload
