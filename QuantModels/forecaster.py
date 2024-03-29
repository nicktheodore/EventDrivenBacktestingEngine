
# coding: utf-8

# In[1]:

# S&P500 Forecaster


# In[2]:

# forecast.py


# In[4]:

from __future__ import print_function

import datetime
import numpy as np
import pandas as pd
import sklearn

from pandas_datareader.data import DataReader
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.lda import LDA
from sklearn.metrics import confusion_matrix
from sklearn.qda import QDA
from sklearn.svm import LinearSVC, SVC


# In[5]:

def create_lagged_series(symbol, start_date, end_date, lags=5):
    """
    This creates a Pandas DataFrame that stores the percentage returns of the adjusted closing valueof a
    stock obtained from Yahoo Finance, along with a number of lagged returns from the prior trading days
    (lag defaults to 5 days). Trading volume, as well as the Direction from the previous day, are also included.
    """
    # Obtain stock information from Yahoo Finance
    ts = DataReader(symbol, "yahoo", start_date-datetime.timedelta(365), end_date)
    
    # Create the new lagged DataFrame
    tslag = pd.DataFrame(index=ts.index)
    tslag["Today"] = ts["Adj Close"]
    tslag["Volume"] = ts["Volume"]
    
    # Create the shifted lag series of prior trading period close values
    for i in range(0, lags):
        tslag["Lag%s" % str(i+1)] = ts["Adj Close"].shift(i+1)
    
    # Create the returns DataFrame
    tsret = pd.DataFrame(index=tslag.index)
    tsret["Volume"] = tslag["Volume"]
    tsret["Today"]  = tslag["Today"].pct_change()*100
    
    # If any of the values of percentage returns equals zero, set them to a small number
    # Stops issues with the QDA model in Scikit-Learn
    for i,x in enumerate(tsret["Today"]):
        if (abs(x) < 0.0001):
            tsret["Today"][i] = 0.0001
            
    # Create the lagged percentage returns columns
    for i in range(0, lags):
        tsret["Lag%s" % str(i+1)] = tslag["Lag%s" % str(i+1)].pct_change()*100
    
    # Create the "Direction" column (+1 or -1) indicating an up/down day
    tsret["Direction"] = np.sign(tsret["Today"])
    tsret = tsret[tsret.index >= start_date] # Cool list comprehension feature to discard day 0.
    
    return tsret


# In[7]:

#create_lagged_series("GOOG", datetime.datetime(2010, 3,3), datetime.datetime(2011, 2, 3))


# In[9]:

if __name__ == "__main__":
    # Create a lagged series of the S&P500 US stock market index
    snpret = create_lagged_series("^GSPC", datetime.datetime(2001,1,10), datetime.datetime(2005,12,31), lags=5)
    
    # Use the prior two days of returns as predictor values, with direction as the response
    X = snpret[["Lag1", "Lag2"]]
    y = snpret["Direction"]
    
    # The test data is split into two parts: Before and after the 1st of Jan, 2005.
    test_start = datetime.datetime(2005,1,1)
    
    # Create training and test sets
    X_train = X[X.index < test_start]
    X_test  = X[X.index >= test_start]
    y_train = y[y.index < test_start]
    y_test  = y[y.index >= test_start]
    
    # Create the (parametrized) models
    print("Hit Rates/Confusion Matrices:\n")
    models = [("LR", LogisticRegression()),
              ("LDA", LDA()),
              ("QDA", QDA()),
              ("LSVC", LinearSVC()),
              ("RSVM", SVC(
                  C=1000000.0, cache_size=200, class_weight=None, 
                  coef0=0.0, degree=3, gamma=0.0001, kernel='rbf',
                  max_iter=-1, probability=False, random_state=None,
                  shrinking=True, tol=0.001, verbose=False)
              ),
              ("RF", RandomForestClassifier(
                  n_estimators=1000, criterion='gini', max_depth=None,
                  min_samples_split=2, min_samples_leaf=1, max_features='auto',
                  bootstrap=True, oob_score=False, n_jobs=1, random_state=None,
                  verbose=0)
              )]
    
    # Iterate through the models
    for m in models:
        # Train each of the models on the training data
        m[1].fit(X_train, y_train)
        
        # Make an array of predictions on the test set
        pred = m[1].predict(X_test)
        
        # Output the hit-rate and the confusion matri for each model
        print("%s:\n%0.3f" % (m[0], m[1].score(X_test, y_test)))
        print("%s:\n" % confusion_matrix(pred, y_test))
        


# In[10]:

# Note that all of the hit rates are between 50% and 60%. This tells us that the lagged variables
# are not hugely indicative of future direction. However, we can see that QDA is just under 60%.
# The confusion matrices also tell us that the true positive rate for "down" days is much higher 
# than that of "up" days. This suggests that a better strategy would consider restricting trades
# to short positions.


# In[ ]:



