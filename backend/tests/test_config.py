import pytest
from src.config import SECRET_KEY, DB_URL

def test_critical_configs():

    assert SECRET_KEY is not None
    assert len(SECRET_KEY) >= 10
    assert DB_URL.startswith("mysql://") or DB_URL.startswith("sqlite")