# Periodic Data Importing

# Pandas
import pandas as pd

# Models - Import from models or server?
from models import Stock, ETF, History

# DB - Is this necessary?
import sqlalchemy as SA
from sqlalchemy.orm import sessionmaker
engine = SA.create_engine('postgresql+psycopg2://super:YiejibusIkmear8@nutcracker-770.postgres.pythonanywhere-services.com:10770/myfolio', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

def updateData():
    # Save SPY
    stockSPY = Stock(symbol="SPY") # Check if SPY already exists
    session.add( stockSPY )
    etfSPY = ETF(stock=stockSPY)
    session.add(etfSPY)
    session.commit()

    # Save SPY stocks
    spyStocks = pd.read_excel('https://us.spdrs.com/site-content/xls/SPY_All_Holdings.xls',header=3)
    spyStocks = spyStocks[:-11] # Drop bottom 11 rows
    for ind, stock in spyStocks.iterrows():
        newStk = Stock(symbol=stock['Identifier']) # Check if stock already exists
        session.add(newStk)
        etfSPY.stocks.append(newStk)
        session.add(etfSPY)
    session.commit()

    # Save history of stocks
    for stock in session.query(Stock):
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
                session.add(newHist)
    session.commit()