# API Server

from models import app, Asset, History
from analysis import getWeights
from flask import jsonify, request

#
# Route URLs
#

# List of assets
@app.route('/api/asset')
def jsonAssets():
    return jsonify( assets = [{ # Create model methods to return dict so we don't list this out here
        'id':ass.id,
        'symbol':ass.symbol,
    } for ass in Asset.query.all()  ] )

# List of ETFs
@app.route('/api/etf')
def jsonEtfs():
    return jsonify( etfs = [{
        'id':ass.id,
        'symbol':ass.symbol
    } for ass in Asset.query.filter( Asset.basket != None ).all() ] )

# List of assets in an ETF
@app.route('/api/etf/<_id>') # Use stock symbol or etf id?
def jsonEtf(_id):
    etf = Asset.query.filter( Asset.id == _id ).first()
    return jsonify(etf={
        'id':etf.id,
        'symbol':etf.symbol,
        'basket':[{
            'id':ass.id,
            'symbol':ass.symbol
        } for ass in etf.basket ]
    })

# Replicate an ETF from a given basket of assets
@app.route('/api/replicate', methods=['POST'])
def jsonReplicate():
    basket = []
    for id in request.get_json()['basket']:
        basket.append({
            'id':id,
            'history':[{'date': row.date, 'price': str(row.vwap)} # str to deal with decimal? 
                for row in History
                    .query
                    .join(History.asset)
                    .with_entities(History.date, History.vwap)
                    .filter( Asset.id == id )
                    .order_by( History.date )
                    .all()
            ]
        })
    return jsonify(basket=basket)

# Default route to index.html
@app.errorhandler(404)
def page_not_found(e):
    return app.send_static_file('index.html')