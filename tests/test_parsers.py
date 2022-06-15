import json
import pytest
from datetime import date

from app.models import Industry, Stock
from app.parsers import (
    IndustryParser,
    IndustryReportParser,
    Parser,
    StockParser
)


class MockRequest:
    url = None
    params = None

    def set_url(self, url):
        self.url = url
    
    def set_params(self, params):
        self.params = params


class MockResponse:
    status_code = 200

    def __init__(self):
        self.request = MockRequest()
        self.content = None

    def set_content(self, content):
        self.content = content
    
    def set_request(self, *args, **kwargs):
        self.request.set_url(args[0])
        if kwargs:
            self.request.set_params(**kwargs)
    
    def json(self):
        return json.loads(self.content)


@pytest.fixture
def mock_response(monkeypatch):
    mock_resp = MockResponse()

    async def mock_get(*args, **kwargs):
        mock_resp.set_request(*args, **kwargs)
        return mock_resp

    monkeypatch.setattr(Parser.client, 'get', mock_get)
    return mock_resp


@pytest.mark.asyncio
class TestParser:
    async def test_get(self, mock_response):
        mock_response.set_content('hello world')

        parser = Parser()
        result = await parser.get('https://example.com/')
        assert result.status_code == 200
        assert result.content == 'hello world'
    
    async def test_get_html(self, mock_response):
        mock_response.set_content(b'<div>Hello World</div>')

        parser = Parser()
        root = await parser.get_html()
        assert root.xpath('//div')[0].text == 'Hello World'
    
    async def test_get_json(self, mock_response):
        mock_response.set_content('{"msg": "hello world"}')

        parser = Parser()
        result = await parser.get_json()
        assert result['msg'] == 'hello world'
    
    async def test_get_json_failed(self, mock_response):
        mock_response.set_content('error')

        parser = Parser()
        result = await parser.get_json()
        assert result == None


@pytest.mark.asyncio
class TestStockParser:
    HTML_SOURCE = """
        <table>
            <tbody>
                <tr>
                    <td bgcolor="#D5FFD5">有價證券代號及名稱 </td>
                    <td bgcolor="#D5FFD5">國際證券辨識號碼(ISIN Code)</td>
                    <td bgcolor="#D5FFD5">上市日</td>
                    <td bgcolor="#D5FFD5">市場別</td>
                    <td bgcolor="#D5FFD5">產業別</td>
                    <td bgcolor="#D5FFD5">CFICode</td>
                    <td bgcolor="#D5FFD5">備註</td>
                </tr>
                <tr>
                    <td bgcolor="#FAFAD2" colspan="7"><b> 股票 <b> </b></b></td>
                </tr>
                <tr>
                    <td bgcolor="#FAFAD2">1101　台泥</td>
                    <td bgcolor="#FAFAD2">TW0001101004</td>
                    <td bgcolor="#FAFAD2">1962/02/09</td>
                    <td bgcolor="#FAFAD2">上市</td>
                    <td bgcolor="#FAFAD2">水泥工業</td>
                    <td bgcolor="#FAFAD2">ESVUFR</td>
                    <td bgcolor="#FAFAD2"></td>
                </tr>
                <tr>
                    <td bgcolor="#FAFAD2">1102　亞泥</td>
                    <td bgcolor="#FAFAD2">TW0001102002</td>
                    <td bgcolor="#FAFAD2">1962/06/08</td>
                    <td bgcolor="#FAFAD2">上市</td>
                    <td bgcolor="#FAFAD2">水泥工業</td>
                    <td bgcolor="#FAFAD2">ESVUFR</td><
                    td bgcolor="#FAFAD2"></td>
                </tr>
                <tr>
                    <td bgcolor="#FAFAD2">1103　嘉泥</td>
                    <td bgcolor="#FAFAD2">TW0001103000</td>
                    <td bgcolor="#FAFAD2">1969/11/14</td>
                    <td bgcolor="#FAFAD2">上市</td>
                    <td bgcolor="#FAFAD2">水泥工業</td>
                    <td bgcolor="#FAFAD2">ESVUFR</td>
                    <td bgcolor="#FAFAD2"></td>
                </tr><
            </tbody>
        </table>
    """

    async def test_get_stocks(self, mock_response):
        mock_response.set_content(self.HTML_SOURCE.encode('MS950'))

        parser = StockParser()
        stocks = await parser.get_stocks()
        assert stocks[0] == Stock(ticker='1101', name='台泥', listed_at='1962/02/09', industry='水泥工業')
        assert stocks[1] == Stock(ticker='1102', name='亞泥', listed_at='1962/06/08', industry='水泥工業')
        assert stocks[2] == Stock(ticker='1103', name='嘉泥', listed_at='1969/11/14', industry='水泥工業')


@pytest.mark.asyncio
class TestIndustryParser:
    HTML_SOURCE = """
        <div id="main-form">
            <div class="outer">
                <h2>每日收盤行情</h2>
                <div class="body">
                <form class="main" method="post" >
                    日期：<div id="d1"></div>
                    &nbsp;&nbsp;
                    分類項目：<select name="type">
                    <option value="MS">大盤統計資訊</option>
                    <option value="IND">收盤指數資訊</option>
                    <option value="MS2">委託及成交統計資訊</option>
                    <option value="ALL">全部</option>
                    <option value="ALLBUT0999">全部(不含權證、牛熊證、可展延牛熊證)</option>
                    <option value="0049">封閉式基金</option>
                    <option value="0099P">ETF</option>
                    <option value="029999">ETN</option>
                    <option value="019919T">受益證券</option>
                    <option value="0999">認購權證(不含牛證)</option>
                    <option value="0999P">認售權證(不含熊證)</option>
                    <option value="0999C">牛證(不含可展延牛證)</option>
                    <option value="0999B">熊證(不含可展延熊證)</option>
                    <option value="0999X">可展延牛證</option>
                    <option value="0999Y">可展延熊證</option>
                    <option value="0999GA">附認股權特別股</option>
                    <option value="0999GD">附認股權公司債</option>
                    <option value="0999G9">認股權憑證</option>
                    <option value="CB">可轉換公司債</option>
                    <option value="TIB">創新板股票</option>
                    <option value="01">水泥工業</option>
                    <option value="02">食品工業</option>
                    <option value="03">塑膠工業</option>
                    <option value="04">紡織纖維</option>
                    <option value="05">電機機械</option>
                    <option value="06">電器電纜</option>
                    <option value="07">化學生技醫療</option>
                    <option value="21">化學工業</option>
                    <option value="22">生技醫療業</option>
                    <option value="08">玻璃陶瓷</option>
                    <option value="09">造紙工業</option>
                    <option value="10">鋼鐵工業</option>
                    <option value="11">橡膠工業</option>
                    <option value="12">汽車工業</option>
                    <option value="13">電子工業</option>
                    <option value="24">半導體業</option>
                    <option value="25">電腦及週邊設備業</option>
                    <option value="26">光電業</option>
                    <option value="27">通信網路業</option>
                    <option value="28">電子零組件業</option>
                    <option value="29">電子通路業</option>
                    <option value="30">資訊服務業</option>
                    <option value="31">其他電子業</option>
                    <option value="14">建材營造</option>
                    <option value="15">航運業</option>
                    <option value="16">觀光事業</option>
                    <option value="17">金融保險</option>
                    <option value="18">貿易百貨</option>
                    <option value="9299">存託憑證</option>
                    <option value="23">油電燃氣業</option>
                    <option value="19">綜合</option>
                    <option value="20">其他</option>
                </select>
                    &nbsp;&nbsp;
                    <a href="#" class="button search">查詢</a>
                </form>
                </div>
            </div>
        </div>
    """

    async def test_get_industries(self, mock_response):
        mock_response.set_content(self.HTML_SOURCE.encode('utf-8'))

        parser = IndustryParser()
        industries = await parser.get_industries()
        assert len(industries) == 28
        assert industries[0] == Industry(code='01', name='水泥工業')
        assert industries[-1] == Industry(code='20', name='其他業')


@pytest.mark.asyncio
class TestIndustryReportParser:
    HTML_SOURCE = """
        {
            "groups1":[{"start":0,"span":11,"title":"(元,股)"},{"start":11,"span":5,"title":"(元,交易單位)"}],
            "notes1":["漲跌(+/-)欄位符號說明:+/-/X表示漲/跌/不比價。","當證券代號為認購(售)權證及認股權憑證時本益比欄位置為結算價；但如為以外國證券或指數為標的之認購(售)權證及履約方式採歐式者，該欄位為空白。","除境外指數股票型基金及外國股票第二上市外，餘交易單位皆為千股。","本統計資訊含一般、零股、盤後定價、鉅額交易，不含拍賣、標購。"],
            "params":{"response":"json","date":"20220614","type":"01","controller":"exchangeReport","format":null,"action":"MI_INDEX","lang":"zh"},
            "stat":"OK",
            "fields1":["證券代號","證券名稱","成交股數","成交筆數","成交金額","開盤價","最高價","最低價","收盤價","漲跌(+/-)","漲跌價差","最後揭示買價","最後揭示買量","最後揭示賣價","最後揭示賣量","本益比"],
            "subtitle1":"111年06月14日每日收盤行情(水泥工業)",
            "data1":[["1101","台泥","26,184,653","17,090","1,051,999,654","40.50","40.55","40.05","40.10","<p style= color:green>-<\u002fp>","0.70","40.10","2,284","40.15","529","13.97"],["1101B","台泥乙特","43,581","9","2,242,300","51.40","51.60","51.40","51.60","<p style= color:red>+<\u002fp>","0.10","51.30","5","51.50","10",""],["1102","亞泥","4,235,603","2,274","184,770,459","43.70","43.80","43.50","43.65","<p style= color:green>-<\u002fp>","0.05","43.65","74","43.70","20","10.75"],["1103","嘉泥","241,460","166","4,365,907","18.30","18.30","18.00","18.20","<p style= color:green>-<\u002fp>","0.05","18.15","16","18.25","8","16.70"],["1104","環泥","478,308","379","10,313,347","21.80","21.80","21.40","21.70","<p style= color:green>-<\u002fp>","0.10","21.65","4","21.70","6","10.19"],["1108","幸福","161,010","127","1,739,958","10.80","10.90","10.75","10.85","<p> <\u002fp>","0.00","10.85","2","10.90","11","16.69"],["1109","信大","229,335","169","4,522,230","19.80","19.85","19.65","19.65","<p style= color:green>-<\u002fp>","0.20","19.65","70","19.75","30","10.08"],["1110","東泥","117,002","76","2,234,388","19.35","19.35","18.85","19.25","<p style= color:green>+<\u002fp>","0.10","19.20","3","19.25","2","71.30"]],
            "date":"20220614",
            "alignsStyle1":[["center","center","center","center","center","center","center","center","center","center","center","center","center","center","center","center"],["left","left","right","right","right","right","right","right","right","center","right","right","right","right","right","right"]]
        }
    """

    async def test_get_report(self, mock_response):
        mock_response.set_content(self.HTML_SOURCE)

        parser = IndustryReportParser()
        industry = Industry(code='01', name='水泥工業')
        date_ = date(2022, 6, 14)
        report = await parser.get_report(industry, date_)
        assert mock_response.request.params == {'date': '20220614', 'type': '01', 'response': 'json'}
        assert report.industry == industry
        assert len(report.stocks) == 8
        assert report.stocks[0] == Stock(ticker="1101", price="40.10", goes_up=False, price_spread="0.70")
        assert report.stocks[-1] == Stock(ticker="1110", price="19.25", goes_up=True, price_spread="0.10")
    
    async def test_get_report_failed(self, mock_response):
        mock_response.set_content('')

        parser = IndustryReportParser()
        industry = Industry(code='01', name='水泥工業')
        date_ = date(2022, 6, 14)
        report = await parser.get_report(industry, date_)
        assert report.industry == industry
        assert report.stocks == []
