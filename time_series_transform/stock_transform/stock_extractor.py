import yfinance as yf
from datetime import datetime
from time_series_transform.stock_transform.base import *


class Stock_Extractor(object):
    def __init__(self,symbol,engine):
        self.client = self._get_extractor(engine)
        self.symbol = symbol
        self.stock = None

    def _get_extractor(self,engine):
        engineDict = {
            'yahoo':yahoo_stock
        }
        return engineDict[engine]

    def get_stock_period(self,period):
        data = self.client.getHistoricalByPeriod(period)
        additionalInfo = self.client.getAdditionalInfo()
        self.stock = Stock(self.symbol,data,additionalInfo)
        return self.stock

    def get_stock_date(self,start_date,end_date):
        data = self.client.getHistoricalByRange(start_date,end_date)
        self.stock = Stock(self.symbol,data)
        return self.stock

    # I/O
    @classmethod
    def get_stock_from_csv(cls, symbol, path, *args, **kwargs):
        data = pd.read_csv(path)
        stock_data = Stock(symbol, data, *args, **kwargs)
        return stock_data


    @classmethod
    def get_stock_from_parquet(cls, symbol, path, *args, **kwargs):
        data = pd.read_parquet(path, engin = 'pyarrow')
        stock_data = Stock(symbol, data, *args, **kwargs)
        return stock_data

class Portfolio_Extractor(object):
    def __init__(self,symbolList,engine):
        self.engine = engine
        self.symbolList = symbolList
        self.portfolio = None

    def get_portfolio_period(self,period):
        stockList = []
        for symbol in self.symbolList:
            stock_data = Stock_Extractor(symbol, self.engine).get_stock_period(period)
            stockList.append(stock_data)

        self.portfolio = Portfolio(stockList)
        return self.portfolio

    def get_portfolio_date(self,start_date, end_date):
        stockList = []
        for symbol in self.symbolList:
            stock_data = Stock_Extractor(symbol, self.engine).get_stock_date(start_date, end_date)
            stockList.append(stock_data)

        self.portfolio = Portfolio(stockList)
        return self.portfolio


class yahoo_stock(object):

    """
    Fetching stock data from yahoo finance
    
    API Document: 
    - https://github.com/ranaroussi/yfinance
    - https://pypi.org/project/fix-yahoo-finance/0.1.0/
    ---
    Require:
    - yfinance

    """
    def __init__(self,symbol):
        self._symbol = symbol
        self._ticker = self._getStock(symbol)
    

    # getter and setter
    @property
    def ticker(self):
        return self._ticker

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, symbol):
        self._symbol = symbol
        self._ticker = yf.Ticker(symbol)
    
    def _getStock(self, symbol):
        ticker = yf.Ticker(symbol)
        return ticker

    def getCompanyInfo(self):
        return self.ticker.info

    """
    Historical Data
    ---
    Input:
    symbol: string
    period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    (default is '1mo')
    start_date, end_date: String, "%Y-%m-%d", eg "2020-02-20"
    ---
    Return:
    date, open, high, low, close, volume, dividends, stock splits
    """

    def getHistoricalByPeriod(self, period = '1mo'):
        return self.ticker.history(period)

    def getHistoricalByRange(self, start_date, end_date):
        return self.ticker.history(start = start_date, end = end_date)

    def getActions(self):
        return self.ticker.actions

    def getDividends(self):
        return self.ticker.dividends

    def getSplits(self):
        return self.ticker.splits

    def getSustainability(self):
        return self.ticker.sustainability

    def getRecommendations(self):
        return self.ticker.recommendations

    def getNextEvent(self):
        return self.ticker.calendar

    def getAdditionalInfo(self):
        info_dict = {
            'company_info':self.getCompanyInfo(),
            'sustainability': self.getSustainability()
        }

        schedule_dict = {
            'actions': self.getActions(),
            'recommendations': self.getRecommendations(),
            'next_event': self.getNextEvent()
        }
       
        data = {
            'info': info_dict,
            'schedule': schedule_dict
            
        }
        return data