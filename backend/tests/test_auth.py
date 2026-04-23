import pytest
from core.security import verify_password, get_password_hash

def test_password_hashing():
    pwd = "mysecretpassword"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed)
