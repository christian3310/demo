import asyncio

from app.managers import IndustryManager, StockManager


async def main(target_date, target_dist):
    stock_manager = StockManager()
    await stock_manager.init()

    stocks = await stock_manager.get_stocks()
    stock_manager.save(stocks, dist=target_dist)
    await asyncio.sleep(2)

    industry_manager = IndustryManager()
    industries = await industry_manager.get_industries()
    await asyncio.sleep(2)

    reports = await industry_manager.get_reports(industries, target_date)
    top3_reports = await industry_manager.calculate_top3(reports, stocks)
    industry_manager.save_top3_reports_to_local(top3_reports)
    industry_manager.save_top3_reports(top3_reports, dist=target_dist)
