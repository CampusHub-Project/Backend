import pytest
from src.security import hash_password, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    raw = "campus_123"
    hashed = hash_password(raw)
    assert verify_password(raw, hashed) is True
    assert verify_password("wrong_pass", hashed) is False

def test_jwt_operations():
    user_id, role = 101, "student"
    token = create_access_token(user_id, role)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert str(decoded["sub"]) == str(user_id)
    assert decoded["role"] == role