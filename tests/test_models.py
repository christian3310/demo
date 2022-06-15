import pytest
from pydantic import ValidationError

from app.models import Stock


def test_stock_listed_at_validation_passed():
    assert Stock(ticker='1234', listed_at='1984/04/04')


def test_stock_listed_at_validation_failed():
    with pytest.raises(ValidationError):
        Stock(ticker='1234', listed_at='19840404')
