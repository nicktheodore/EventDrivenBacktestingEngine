
# coding: utf-8

# In[1]:

# Testing for stationarity with the Hurst Exponent


# In[8]:

from __future__ import print_function

from numpy import cumsum, log, polyfit, sqrt, std, subtract
from numpy.random import randn
import pandas_datareader.data as web
from datetime import datetime

def hurst(ts):
    """
    Returns the Hurst Exponent of the time series vector ts
    """
    # Create a range of lag values
    lags = range(2, 100)
    
    # Calculate the array of the variances of the lagged differences
    tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]
    
    # Use a linear fit to estimate the Hurst Exponent
    poly = polyfit(log(lags), log(tau), 1)
    
    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0


# In[9]:

# Create a Geometric Brownian Motion, Mean-Reverting, and Trending series
gbm = log(cumsum(randn(100000)) + 1000)
mr  = log(randn(100000) + 1000)
tr  = log(cumsum(randn(100000) + 1) + 1000)

amzn = web.DataReader("AMZN", "yahoo", datetime(2000,1,1), datetime(2015,1,1))


# In[10]:

# Output the Hurst Exponent for each of above series and the price of Amazon (Adj Close) for the previous ADF test
print("Hurst(GBM):    %s" % hurst(gbm))
print("Hurst(MR) :    %s" % hurst(mr))
print("Hurst(TR) :    %s" % hurst(tr))


# In[11]:

# Run the above code to obtain AMZN
print("Hurst(AMZN):   %s" % hurst(amzn['Adj Close']))


# In[32]:

def hurst_behavior(ts):
    h = hurst(ts)
    tol = 0.05
    if abs(h-0.5) < tol:
        print("Geometric Brownian Motion H: %f, tol: %f" % (h, tol))
    else:
        if h > 0.5 + tol:
            print("Trending Timeseries H: %f, tol: %f" % (h, tol))
        elif h < 0.5 - tol:
            print("Mean-Reverting Timeseries H: %f, tol: %f" % (h, tol))


# In[33]:

hurst_behavior(gbm)
hurst_behavior(mr)
hurst_behavior(tr)
hurst_behavior(amzn['Adj Close'])


# In[ ]:



