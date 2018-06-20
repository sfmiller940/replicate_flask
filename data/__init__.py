# Data Management
from models import db, ETF, Stock, History
import pandas as pd

etfs = ['SPY']
#etfs = [{symbol:'SPY',source:'iex'},{symbol:'POLONIEX',source:'poloniex'}]

def getOrCreate(model,**kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        return instance    

def updateETF():
    for etf in etfs:
        etf = getOrCreate(  
            ETF, \
            stock = getOrCreate( Stock, symbol=etf ) \
        )

        if etf.stock.symbol == 'SPY':
            stocks = pd.read_excel('https://us.spdrs.com/site-content/xls/SPY_All_Holdings.xls',header=3)
            stocks = stocks[:-11]
            for ind, row in stocks.iterrows():
                stock = getOrCreate( Stock, symbol=row['Identifier'], source='iex' )
                etf.stocks.append(stock) # Need to compare old/new lists
                db.session.add(etf)
        # Poloniex goes here
    db.session.commit()

def updateHistory():
    for stock in db.session.query(Stock).all():
        if stock.source == "iex":
            if stock.symbol != 'CCL.U' and stock.symbol != 'JEF' and stock.symbol != 'CASH_USD': # What's up with these 3?
                df = pd.DataFrame()
                df = pd.read_json('https://api.iextrading.com/1.0/stock/'+stock.symbol+'/chart/5y') # Only retrieve new data
                df.set_index('date',inplace=True)
                for date, row in df.iterrows():
                    getOrCreate(
                        History,
                        stock=stock,
                        date = date,
                        vwap = row['vwap'],
                        high = row['high'],
                        low = row['low'],
                        open = row['open'],
                        close = row['close'],
                    )
            # Poloniex goes here
        db.session.commit()