import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator


class Stock(BaseModel):
    ticker: str
    name: Optional[str]
    listed_at: Optional[str]
    industry: Optional[str]
    goes_up: Optional[bool]
    price: Optional[str]
    price_spread: Optional[str]
    diff: Optional[str]

    @validator('listed_at')
    def listed_date_rule(cls, v):
        assert re.match(r'\d{4}/\d{2}/\d{2}', v)
        return v


class Industry(BaseModel):
    code: str
    name: str


class IndustryReport(BaseModel):
    industry: Industry
    stocks: list[Stock]


class IndustryReportFieldIndex(Enum):
    TICKER: int = 0
    PRICE: int = 8
    GOES_UP: int = 9
    PRICE_SPREAD: int = 10


class StockFieldIndex(Enum):
    TICKER_NAME: int = 0
    LISTED_AT: int = 2
    INDUSTRY: int = 4