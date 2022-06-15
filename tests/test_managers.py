import pytest

from app.managers import IndustryManager
from app.models import Industry, IndustryReport, Stock


INDUSTRY = Industry(code='01', name='水泥工業')
STOCKS = [
    Stock(ticker='1101', goes_up=True, price='40.10', price_spread='0.70', industry='水泥工業'),
    Stock(ticker='1102', goes_up=False, price='43.65', price_spread='0.05', industry='水泥工業'),
    Stock(ticker='1103', goes_up=False, price='18.20', price_spread='0.05', industry='水泥工業'),
    Stock(ticker='1104', goes_up=True, price='21.70', price_spread='0.10', industry='水泥工業'),
    Stock(ticker='1108', goes_up=False, price='10.85', price_spread='0.00', industry='水泥工業'),
    Stock(ticker='1109', goes_up=False, price='19.65', price_spread='0.20', industry='水泥工業'),
    Stock(ticker='1110', goes_up=True, price='19.25', price_spread='0.10', industry='水泥工業'),
    Stock(ticker='1101B', goes_up=True, price='51.60', price_spread='0.10', industry='水泥工業'),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'stocks,stock_scope,results',
    [
        (
            [],
            STOCKS[:-1],
            []
        ),
        (
            STOCKS,
            STOCKS[:-1],
            [{'ticker': '1101', 'diff': '1.78%'}, {'ticker': '1110', 'diff': '0.52%'}, {'ticker': '1104', 'diff': '0.46%'}]
        ),
        (
            STOCKS[:2],
            STOCKS[:-1],
            [{'ticker': '1101', 'diff': '1.78%'}]
        )
    ]
)
async def test_calculate_top3(stocks, stock_scope, results):
    manager = IndustryManager()
    report = IndustryReport(industry=INDUSTRY, stocks=stocks)
    top3_results = await manager.calculate_top3([report], stock_scope)
    assert top3_results[0]['data'] == results
