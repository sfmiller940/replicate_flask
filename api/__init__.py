# API Server

from models import app, Stock, ETF
from analysis import getWeights
from flask import jsonify, request

#
# Route URLs
#

# Stock listing
@app.route('/api/stock')
def jsonStocks():
    return jsonify( stocks = [{ # Create model methods to return dict so we don't list this out here
        'id':stk.id,
        'symbol':stk.symbol,
    } for stk in Stock.query.all()  ] )

# ETF listing
@app.route('/api/etf')
def jsonEtfs():
    return jsonify( etfs = [{
        'id':etf.id,
        'symbol':etf.stock.symbol
    } for etf in ETF.query.all() ] )

# Stock listings for specific <_etf>
@app.route('/api/etf/<_id>') # Use stock symbol or etf id?
def jsonEtf(_id):
    etf = ETF.query.filter( ETF.id == _id ).first()
    return jsonify(etf={
        'id':etf.id,
        'symbol':etf.stock.symbol,
        'stocks':[{
            'id':stk.id,
            'symbol':stk.symbol
        } for stk in etf.stocks ]
    })

# Return weights for a given basket of stocks to replicate a given ETF
@app.route('/api/replicate')
def jsonReplicate():
    histories = [
        History.query.filter( History.stock.id == _id ).order_by( History.date ) 
        for _id in request.form.get('basket')
    ]
    return jsonify( getWeights( histories ) )

# Default route to index.html
@app.errorhandler(404)
def page_not_found(e):
    return app.send_static_file('index.html')