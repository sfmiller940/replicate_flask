# API Server

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# Configure api
api = Flask(__name__)
api.config.from_mapping(
  SECRET_KEY='dev',
  SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://super:YiejibusIkmear8@nutcracker-770.postgres.pythonanywhere-services.com:10770/myfolio'
)

# Connect DB
db = SQLAlchemy(api)

# Import models
from models import Stock, ETF

#Import replicator
from analysis import getWeights

#
# Route URLs
#

# Homepage
@api.route('/')
def hello_world():
  return 'Welcome to the homepage!'

# Stock listing
@api.route('/stock')
def stocks_json():
    return jsonify( stocks = [{ # Create model methods to return dict so we don't list this out here
        'id':stk.id,
        'symbol':stk.symbol,
    } for stk in Stock.query.all()  ] )

# ETF listing
@api.route('/etf')
def etfs_json():
    return jsonify( etfs = [{
        'id':etf.id,
        'symbol':etf.stock.symbol
    } for etf in ETF.query.join(Stock).all() ] )

# Stock listings for specific <_etf>
@api.route('/etf/<_etf>') # Use stock symbol or etf id?
def etf_json(_etf):
    et = ETF \
        .query \
        .join(Stock) \
        .filter( Stock.symbol == _etf ) \
        .first()
    return jsonify(etf={
        'id':et.id,
        'symbol':et.stock.symbol,
        'stocks':[{
            'id':stk.id,
            'symbol':stk.symbol
        } for stk in et.stocks]
    })

# Return weights for a given basket of stocks to replicate a given ETF
@api.route('/replicate')
def replicate_json():
    return jsonify( getWeights( request.form.get('base'), request.form.get('target') ) )