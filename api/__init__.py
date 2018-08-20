# API Server
from models import app, Asset, History
from analysis import getWeights
from flask import request
from lib import jsonDump
#
# Route URLs
#

# List of assets
@app.route('/api/asset')
def jsonAssets():
    return jsonDump( [{ # Create model methods to return dict so we don't list this out here
        'id':ass.id,
        'symbol':ass.symbol,
    } for ass in Asset.query.all()  ] )

# List of ETFs
@app.route('/api/etf')
def jsonEtfs():
    return jsonDump( [{
        'id':ass.id,
        'symbol':ass.symbol
    } for ass in Asset.query.filter( Asset.basket != None ).all() ] )

# List of assets in an ETF
@app.route('/api/etf/<_id>') # Use stock symbol or etf id?
def jsonEtf(_id):
    etf = Asset.query.filter( Asset.id == _id ).first()
    return jsonDump({
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
    minLen = 0
    for id in request.get_json()['basket']:
        basket.append({
            'id':id,
            'history':[{'date': row.date, 'price': row.vwap}
                for row in History
                    .query
                    .join(History.asset)
                    .with_entities(History.date, History.vwap)
                    .filter( Asset.id == id )
                    .order_by( History.date )
                    .all()
            ]
        })
        if( minLen == 0 or len(basket[-1]['history']) < minLen ):
            minLen = len(basket[-1]['history'])
    for asset in basket:
        asset['history'] = asset['history'][0:minLen]
    #weights = getWeights(basket)
    return jsonDump(basket)

# Default route to index.html
@app.errorhandler(404)
def page_not_found(e):
    return app.send_static_file('index.html')