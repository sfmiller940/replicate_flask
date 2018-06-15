# Replication

import numpy as np
import pandas as pd
import quadprog as qp

def getWeights(base=[], target=''):
    if(base==[] or target==''):
        return []

    # Load data
    df = pd.DataFrame()
    roc = pd.DataFrame() # Rate of change for each asset
    symbols = base + [target]
    for symbol in symbols:
        df = pd.read_json('https://api.iextrading.com/1.0/stock/'+symbol+'/chart/5y')
        df.set_index('date',inplace=True)
        roc[symbol] = df['close'].pct_change()[1:] # Get rate of change minus first row NA

    cols = len(base)
    X = np.array( roc[base] ).astype(float) # ROC of base assets
    y = np.array( roc[target] ).astype(float) # ROC of target asset

    # Estimate weights
    G = np.cov( np.transpose(X) )
    a = np.dot(y.T - y.mean(), X - X.mean(axis=0)) / (y.shape[0]-1) # from Stack Exchange
    c1 = np.full(cols,1)
    c2 = np.zeros( (cols,cols) )
    np.fill_diagonal( c2, 1)
    C = np.transpose(np.vstack([c1, c2]))
    wmin = np.full(cols,0)
    b = np.insert(wmin, 0, 1)
    optimal = qp.solve_qp( G, a, C = C, b = b, meq = 1 )

    return optimal[0] # Weights