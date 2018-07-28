# Data Management
import time
from datetime import datetime
import pandas as pd
from lib import getOrAddNew
from models import db, ETF, Stock, History
from poloniex import Poloniex
polo = Poloniex()

# ETFs
etfs = [
    getOrAddNew( ETF, db.session, stock = getOrAddNew( Stock, db.session, symbol='SPY', source='iex' ) ),
    getOrAddNew( ETF, db.session, stock = getOrAddNew( Stock, db.session, symbol='USDT_BTC', source='poloniex' ) ),
]

def symbolsSPY():
    return pd.read_excel('https://us.spdrs.com/site-content/xls/SPY_All_Holdings.xls',header=3)[:-11]['Identifier'].tolist()

def symbolsUSDT_BTC():
    return ['USDT_DASH','USDT_ETC','USDT_ETH','USDT_LTC','USDT_NXT','USDT_REP','USDT_STR','USDT_XMR','USDT_XRP','USDT_ZEC']

getSymbols = {
    'SPY': symbolsSPY,
    'USDT_BTC': symbolsUSDT_BTC
}

# History sources
def historyIex(stock):
    if stock.symbol != 'CCL.U' and stock.symbol != 'JEF' and stock.symbol != 'CASH_USD': # What's up with these 3?
        df = pd.read_json('https://api.iextrading.com/1.0/stock/'+stock.symbol+'/chart/5y') # Only retrieve new data
        df.set_index('date',inplace=True)
        for date, row in df.iterrows():
            getOrAddNew(
                History,
                db.session,
                stock = stock,
                date = date,
                vwap = row['vwap'],
                high = row['high'],
                low = row['low'],
                open = row['open'],
                close = row['close'],
                volume = row['volume'] 
            )

def historyPoloniex(stock):
    dates = []
    data={'price':[],'volume':[]}
    period = 86400 # 1 day
    length = 500
    end = time.time() # Now
    start = end - ( length * period ) # 500 days ago
    raw = polo.returnChartData(currencyPair=stock.symbol,period=period,start=start,end=end )
    for i in range(len(raw)):
        getOrAddNew(
            History,
            db.session,
            stock = stock,
            date = datetime.fromtimestamp(int(raw[i]['date'])),
            vwap = float(raw[i]['weightedAverage']),
            high = float(raw[i]['high']),
            low = float(raw[i]['low']),
            open = float(raw[i]['open']),
            close = float(raw[i]['close']),
            volume = float(raw[i]['volume'] )
        )

updateHistory = {
    'iex':historyIex,
    'poloniex':historyPoloniex
}

# Update Stocks and Histories
def update():

    # Create Stocks and add to ETFs
    for etf in etfs:
        for symbol in getSymbols[etf.stock.symbol]():
            etf.stocks.append( getOrAddNew( Stock, db.session, symbol=symbol, source=etf.stock.source ) ) # Need to compare old/new lists
        db.session.add(etf)
    db.session.commit()
    print('ETFs and Stocks added')

    # Update Stock histories
    for stock in db.session.query(Stock).all():
        updateHistory[stock.source](stock)
        db.session.commit()
        print(stock.symbol + ' history updated')