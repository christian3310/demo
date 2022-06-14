import asyncio
import httpx
import json
import logging
import re
from datetime import date
from lxml import etree

from app.models import Industry, IndustryReport, Stock
from app.models import IndustryReportFieldIndex, StockFieldIndex


class Parser():
    endpoint: str = None
    client: httpx.AsyncClient = httpx.AsyncClient()
    retry: int = 8

    async def get(self, link, **kwargs) -> httpx.Response:
        for _ in range(self.retry):
            try:
                resp = await self.client.get(link, **kwargs)
            except (httpx.ConnectError, httpx.ReadError):
                await asyncio.sleep(5)
            except (httpx.ConnectTimeout, httpx.ReadTimeout):
                await asyncio.sleep(5)
            else:
                if resp.status_code != 200:
                    await asyncio.sleep(10)
                else:
                    return resp
        
        raise RuntimeError

    async def init_connect(self):
        root = 'https://www.twse.com.tw/zh/'
        await self.get(root)

    async def get_html(self, encoding: str = 'utf-8') -> etree.ElementTree:
        resp = await self.get(self.endpoint)
        if (b'Error Code' in resp.content):
            await self.init_connect()
            await asyncio.sleep(1)
            return await self.get_html(self.endpoint)
        html = etree.HTML(resp.content.decode(encoding))
        return etree.ElementTree(html)
    
    async def get_json(self, **kwargs) -> dict:
        resp = await self.get(self.endpoint, **kwargs)
        try:
            return resp.json()
        except json.JSONDecodeError as e:
            logging.exception(e)
            logging.warning(resp.request.url)
            logging.warning(resp.content)
            return None
    
    async def close(self):
        await self.client.aclose()


class StockParser(Parser):
    endpoint = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'

    async def get_stocks(self) -> list[Stock]:
        source = await self.get_html(encoding='MS950')
        rows = source.xpath('//tr[td[text()="ESVUFR"]]')
        tickers = [self._parse_stock(r) for r in rows]
        return tickers
    
    def _parse_stock(self, row: etree.Element) -> Stock:
        columns = row.getchildren()
        ticker_name = columns[StockFieldIndex.TICKER_NAME.value].text
        industry = columns[StockFieldIndex.INDUSTRY.value].text
        ticker, name = ticker_name.strip().split('\u3000')
        if not industry.endswith('業'):
            industry = f'{industry}業'
        return Stock(
            ticker=ticker,
            name=name,
            listed_at=columns[StockFieldIndex.LISTED_AT.value].text,
            industry=industry
        )


class IndustryParser(Parser):
    endpoint = 'https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html'
    skip_industries = {
        '07': '化學生技醫療業',
        '13': '綜合業',
        '19': '電子工業'
    }

    async def get_industries(self) -> list[Industry]:
        source = await self.get_html(encoding='utf-8')
        elements = source.xpath('//option')
        pattern = re.compile(r'\d{2}$')
        industries = [
            self._parse_industry(e) for e in elements
            if (code := e.get('value')) not in self.skip_industries and
                pattern.match(code)
        ]
        return industries
    
    def _parse_industry(self, element: etree.Element) -> Industry:
        if not (name := element.text).endswith('業'):
            name = f'{name}業'
        return Industry(code=element.get('value'), name=name)


class IndustryReportParser(Parser):
    endpoint = 'https://www.twse.com.tw/exchangeReport/MI_INDEX'

    async def get_report(self, industry: Industry, date_: date) -> IndustryReport:
        params = {
            'date': date_.strftime('%Y%m%d'),
            'type': industry.code,
            'response': 'json'
        }
        data = await self.get_json(params=params)
        try:
            stocks = self._parse_stocks(data)
        except (KeyError, TypeError):
            stocks = []

        return IndustryReport(industry=industry, stocks=stocks)
    
    def _parse_stocks(self, data: dict) -> list[Stock]:
        up_pattern = '>+<'
        return [
            Stock(
                ticker=datum[IndustryReportFieldIndex.TICKER.value],
                price=datum[IndustryReportFieldIndex.PRICE.value],
                goes_up=up_pattern in datum[IndustryReportFieldIndex.GOES_UP.value],
                price_spread=datum[IndustryReportFieldIndex.PRICE_SPREAD.value]
            )
            for datum in data['data1']
        ]

    async def get_reports(
        self,
        industries: list[Industry],
        date_: date
    ) -> list[IndustryReport]:
        reports = []
        for industry in industries:
            report = await self.get_report(industry, date_)
            reports.append(report)
            await asyncio.sleep(5)

        return reports
