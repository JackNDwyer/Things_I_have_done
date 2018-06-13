import numpy as np
import pandas as pd
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.covariance import EllipticEnvelope



def out(df):
    cols = df.shape[1]
    print cols
    classifiers = {'svm':OneClassSVM(kernel='rbf', gamma=1.0/df.shape[0], tol=0.001, nu=0.5, shrinking=True, cache_size=80),
    'forest':IsolationForest(max_samples='auto'),"robust covariance (Minimum Covariance Determinant)":
    EllipticEnvelope(contamination=0.261),"empirical_covariance": EllipticEnvelope(support_fraction=1.,
                                             contamination=0.261)}
    for key,model in classifiers.iteritems():
        model = model.fit(df.iloc[:,:cols].values)
        pred = model.predict(df.iloc[:,:cols].values)

        scores = model.decision_function(df.iloc[:,:cols].values).flatten()
        maxvalue = np.max(scores)
        scores = maxvalue - scores

        df[key+'_score'] = scores
        df[key+'_class'] = pred
    return df




    
