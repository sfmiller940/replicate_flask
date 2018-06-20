# Data Management
from models import db, ETF, Stock, History
import pandas as pd

#etfs = ['SPY','POLO']
etfs = ['SPY']

def getOrCreate(model,**kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance    

def updateStock(etf):
    if etf.stock.symbol == 'SPY':
        spyStocks = pd.read_excel('https://us.spdrs.com/site-content/xls/SPY_All_Holdings.xls',header=3)
        spyStocks = spyStocks[:-11]
        for ind, stock in spyStocks.iterrows():
            newStk = getOrCreate( Stock, symbol=stock['Identifier'], source='iex' )
            db.session.add(newStk)
            etf.stocks.append(newStk) # Need to check if already listed
            db.session.add(etf)
        db.session.commit()
    # Need to add poloniex

def updateETF():
    for etf in etfs:
        etf = getOrCreate(  
            ETF, \
            stock = getOrCreate( Stock, symbol=etf ) \
        )
        updateStock(etf)

def updateHistory():
    for stock in db.session.query(Stock).all():
        if stock.source == "iex":
            if stock.symbol != 'CCL.U' and stock.symbol != 'JEF' and stock.symbol != 'CASH_USD': # What's up with these 3?
                df = pd.DataFrame()
                df = pd.read_json('https://api.iextrading.com/1.0/stock/'+stock.symbol+'/chart/5y') # Only retrieve new data
                df.set_index('date',inplace=True)
                for date, row in df.iterrows():
                    newHist = History(
                        stock=stock,
                        date = date,
                        vwap = row['vwap'],
                        high = row['high'],
                        low = row['low'],
                        open = row['open'],
                        close = row['close'],
                    )
                    db.session.add(newHist)
            # Need to add Poloniex
        db.session.commit()