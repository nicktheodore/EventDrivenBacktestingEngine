
# coding: utf-8

# In[1]:

#Value-at-Risk


# In[2]:

from __future__ import print_function

import datetime

import numpy as np
import pandas_datareader.data as web
from scipy.stats import norm


# In[3]:

def var_covar(P, c, mu, sigma):
    """
    Variance-Covariance calculation of daily Value-at-Risk using confidence level c,
    with mean of returns mu and standard deviation of returns sigma, on a portfolio
    of value P.
    """
    # Calculate alpha, the inverse of the cumulative distribution function of a normal distribution with
    # mean mu and std. dev. sigma
    alpha = norm.ppf(1-c, mu, sigma)
    
    # Return Value-at-Risk calculation
    return P - P*(alpha+1)


# In[8]:

if __name__ == "__main__":
    start = datetime.datetime(2010, 1, 1)
    end   = datetime.datetime(2014, 1, 1)
    
    citi = web.DataReader("C", 'yahoo', start, end)
    citi["returns"] = citi["Adj Close"].pct_change()
    
    P = 1e6   # 1,000,000 USD
    c = 0.99  # 99% confidence interval
    mu = np.mean(citi["returns"])
    sigma = np.std(citi["returns"])
    
    var = var_covar(P, c, mu, sigma)
    print("Value-at-Risk: $%0.2f" % var)


# In[9]:

# "We are 99% confident that our losses can be no more than $56,503.13 the following day.
# David Einhorn: "VaR is an airbag that works all the time except when you have a car accident"
# Always use VaR as a compliment to your risk management overlay, not as a single indicator.

