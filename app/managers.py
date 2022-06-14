import asyncio
import json
from collections import defaultdict
from datetime import date

from app.models import Industry, IndustryReport, Stock
from app.parsers import IndustryParser, IndustryReportParser, StockParser
from app.utils import LOCAL_STORAGE, split


class StockManager:
    local_file = LOCAL_STORAGE / 'listed.json'

    def __init__(self):
        self.parser = StockParser()
    
    async def init(self):
        await self.parser.init_connect()
        await asyncio.sleep(1)
    
    async def get_stocks(self) -> list[Stock]:
        return await self.parser.get_stocks()
    
    def save_to_local(self, stocks: list[Stock]):
        with open(self.local_file, 'w', encoding='utf-8') as f:
            wanted = {'ticker', 'name', 'listed_at', 'industry'}
            data = [stock.dict(include=wanted) for stock in stocks]
            json.dump(data, f, indent=4, ensure_ascii=False)


class IndustryManager:
    concurrency: int = 2

    def __init__(self):
        self.industry_parser = IndustryParser()
    
    async def get_industries(self) -> list[Industry]:
        return await self.industry_parser.get_industries()

    async def get_reports(
        self,
        industries: list[Industry],
        date_: date
    ) -> list[IndustryReport]:
        reports = []
        chunks = split(industries, self.concurrency)
        parsers = [IndustryReportParser() for _ in range(self.concurrency)]
        await asyncio.gather(*[parser.init_connect() for parser in parsers])

        results = await asyncio.gather(
            *[
                parser.get_reports(chunk, date_)
                for parser, chunk in zip(parsers, chunks)
            ]
        )
        for result in results:
            reports.extend(result)

        return reports

    async def _calculate_top3(self, report: IndustryReport, scope: set) -> dict:
        data = []
        for stock in report.stocks:
            if stock.goes_up and stock.ticker in scope:
                price = float(stock.price.replace(',', ''))
                price_spread = float(stock.price_spread.replace(',', ''))
                diff = price_spread / (price - price_spread) * 100
                stock.diff = f'{round(diff, 2)}%'
                data.append(stock.dict(include={'ticker', 'diff'}))

        data.sort(key=lambda s: s['diff'], reverse=True)
        return {
            'industry': report.industry.name,
            'data': data[:3]
        }

    async def calculate_top3(self, reports: list[IndustryReport], stocks: list[Stock]) -> list[dict]:
        scopes = defaultdict(set)
        for stock in stocks:
            scopes[stock.industry].add(stock.ticker)

        results = await asyncio.gather(
            *[
                self._calculate_top3(report, scopes[report.industry.name])
                for report in reports
            ]
        )
        return results

    def save_top3_reports_to_local(self, reports: list):
        for report in reports:
            filename = f'./data/{report["industry"]}_top3.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report['data'], f, indent=4)
