import pytest
from src.security import decode_access_token

def test_invalid_token_handling():
    assert decode_access_token("bu.bir.token.degildir") is None
    assert decode_access_token("") is None

def test_pagination_math():
    total_items = 25
    limit = 10
    total_pages = (total_items + limit - 1) // limit
    assert total_pages == 3
    
    total_items = 5
    limit = 10
    total_pages = (total_items + limit - 1) // limit
    assert total_pages == 1