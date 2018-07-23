# Data Management
from models import db, ETF, Stock, History
import pandas as pd
import time

etfs = [{
    symbol:'SPY',
    source:'iex'
},{
    symbol:'BTC_USDT',
    source:'poloniex',
    stocks:[            # Same source assumed
        'USDT_DASH',
        'USDT_ETC',
        'USDT_ETH',
        'USDT_LTC',
        'USDT_NXT',
        'USDT_REP',
        'USDT_STR',
        'USDT_XMR',
        'USDT_XRP',
        'USDT_ZEC'
    ]
}]

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

        if etf.symbol == 'SPY':
            stocks = pd.read_excel('https://us.spdrs.com/site-content/xls/SPY_All_Holdings.xls',header=3)
            stocks = stocks[:-11]
        elif etf.symbol == 'BTC_USDT':
            stocks = etf.stocks

        etf = getOrCreate(  
            ETF, \
            stock = getOrCreate( Stock, symbol=etf.symbol ) \
        )

        if etf.stock.symbol == 'SPY':
            for ind, row in stocks.iterrows():
                stock = getOrCreate( Stock, symbol=row['Identifier'], source='iex' )
                etf.stocks.append(stock) # Need to compare old/new lists
                db.session.add(etf)
        elif etf.stock.symbol == "BTC_USDT":
            for symbol in stocks:
                stock = getOrCreate( Stock, symbol = symbol, source = 'poloniex')
                etf.stocks.append(stock) # Need to compare old/new lists
                db.session.add(etf)
    db.session.commit()
    print('ETFs updated')

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
                        # volume = row['volume'] <- speculative 
                    )
        if stock.source == 'poloniex':
            dates = []
            data={'price':[],'volume':[]}
            period = 86400 # 1 day
            length = 500
            end = time.time() # Now
            start = end - ( length * period ) # 500 days ago
            raw = polo.returnChartData(currencyPair=stock.symbol,period=period,start=start,end=end )
            for i in range(len(raw)):
                getOrCreate(
                    History,
                    stock=stock,
                    date = int(raw[i]['date']),
                    vwap = float(raw[i]['weightedAverage']),
                    #high = row['high'],
                    #low = row['low'],
                    #open = row['open'],
                    #close = row['close'],
                    volume = float(raw[i]['volume'] )
                )
        db.session.commit()
        print(stock.symbol + ' updated')