# Data Management
import time
from datetime import datetime
import pandas as pd
from lib import getOrAddNew
from models import db, Asset, History
from poloniex import Poloniex
polo = Poloniex()

# ETFs
etfs = [
    getOrAddNew( Asset, db.session, symbol='SPY', source='iex' ),
    getOrAddNew( Asset, db.session, symbol='USDT_BTC', source='poloniex' ),
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
def historyIex(asset):
    if asset.symbol != 'CCL.U' and asset.symbol != 'JEF' and asset.symbol != 'CASH_USD': # What's up with these 3?
        df = pd.read_json('https://api.iextrading.com/1.0/stock/'+asset.symbol+'/chart/5y') # Only retrieve new data
        df.set_index('date',inplace=True)
        for date, row in df.iterrows():
            getOrAddNew(
                History,
                db.session,
                asset = asset,
                date = date,
                vwap = row['vwap'],
                high = row['high'],
                low = row['low'],
                open = row['open'],
                close = row['close'],
                volume = row['volume'] 
            )

def historyPoloniex(asset):
    dates = []
    data={'price':[],'volume':[]}
    period = 86400 # 1 day
    length = 500
    end = time.time() # Now
    start = end - ( length * period ) # 500 days ago
    raw = polo.returnChartData(currencyPair=asset.symbol,period=period,start=start,end=end )
    for i in range(len(raw)):
        getOrAddNew(
            History,
            db.session,
            asset = asset,
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

# Update assets and histories
def update():

    # Create assets and add to baskets
    for etf in etfs:
        for symbol in getSymbols[etf.symbol]():
            etf.basket.append( getOrAddNew( Asset, db.session, symbol=symbol, source=etf.source ) ) # Need to compare old/new lists
        db.session.add(etf)
    db.session.commit()
    print('ETFs and Stocks added')

    # Update asset histories
    for asset in Asset.query.all():
        updateHistory[asset.source](asset)
        db.session.commit()
        print(asset.symbol + ' history updated')