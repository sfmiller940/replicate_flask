# Replication
import numpy as np
import quadprog as qp

def getWeights(basket):

    # Calculate rates of change
    roc = [] 
    for asset in basket:
        roc.append([ 
            right['price'] / left['price'] 
            for left, right in zip(asset['history'],asset['history'][1:])
        ])
    X = np.array(roc[:-1]).astype(float) # ROC of base assets
    y = np.array(roc[-1]).astype(float) # ROC of target asset

    # Calculate weights
    cols = len(basket) - 1
    G = np.cov(X)
    X = np.transpose(X)
    a = np.dot(y.T - y.mean(), X - X.mean(axis=0)) / (y.shape[0]-1)
    c1 = np.full(cols,1)
    c2 = np.zeros( (cols,cols) )
    np.fill_diagonal( c2, 1)
    C = np.transpose(np.vstack([c1, c2])).astype(float)
    wmin = np.full(cols,0)
    b = np.insert(wmin, 0, 1).astype(float)

    return qp.solve_qp( G, a, C = C, b = b, meq = 1 )[0] # Weights