
# coding: utf-8

# In[1]:

# sharpe.py


# In[2]:

from __future__ import print_function

import datetime
import numpy as np
import pandas as pd
import pandas_datareader.data as web


# In[3]:

def annualized_sharpe(returns, N=252):
    """
    Calculate the annualized Sharpe Ratio of a returns stream based on a number of trading periods, N.
    N defaults to 252, which then assumes a stream of daily returns.
    
    The function assumes that the returns are the excess of those compared to a benchmark.
    """
    return np.sqrt(N) * returns.mean() / returns.std()


# In[4]:

def equity_sharpe(ticker, start_date=datetime.datetime(2000,1,1), end_date=datetime.datetime(2013,1,1),
                  risk_free_rate=0.05):
    """
    Calculates the annualized Sharpe Ratio based on the daily returns of an
    equity ticker symbol listed on Google Finance (Yahoo Finance because google doesn't work). 
    """
    
    # Obtain the equities daily historic data for the desired time-period and add to a pandas DataFrame
    pdf = web.DataReader(ticker, 'yahoo', start_date, end_date)
    
    # Use the percentage change method to easily calculate daily returns
    pdf['daily_ret'] = pdf['Close'].pct_change()
    
    # Assume an average annual risk-free rate over the period of 5%
    pdf['excess_daily_ret'] = pdf['daily_ret'] - risk_free_rate/252
    
    # Return the annualized Sharpe Ratio based on the excess daily returns
    return annualized_sharpe(pdf['excess_daily_ret'])


# In[6]:

equity_sharpe('GOOG')


# In[7]:

# For Google, the Sharpe Ratio for buying and holding is 0.702!


# In[8]:

def market_neutral_sharpe(ticker, benchmark, start_date=datetime.datetime(2000,1,1), 
                          end_date=datetime.datetime(2013,1,1)):
    """
    Calculates the annualized Sharpe Ratio of a market-neutral long/short strategy involing the long of a 'ticker'
    with a corresponding short of the 'benchmark'.
    """
    # Get historic data for both a symbol/ticker and a benchmark ticker
    tick = web.DataReader(ticker, 'yahoo', start_date, end_date)
    bench = web.DataReader(benchmark, 'yahoo', start_date, end_date)
    
    # Calculate the percentage returns on each of the timeseries
    tick['daily_ret']  = tick['Close'].pct_change()
    bench['daily_ret'] = bench['Close'].pct_change()
    
    # Create a new DataFrame to store the strategy information
    # The net-returns are (long-short)/2, since there is twice the trading capital for this strategy
    strat = pd.DataFrame(index=tick.index)
    strat['net_ret'] = (tick['daily_ret'] - bench['daily_ret']) / 2.0
    
    # Return the annualized Sharpe Ratio for this strategy
    return annualized_sharpe(strat['net_ret'])


# In[9]:

market_neutral_sharpe('GOOG', 'SPY')


# In[10]:

# For Google, the Sharpe Ratio for the long/short market-neutral strategy is 0.828!


# In[28]:

def downward_volatility(returns):
    
    downward_variance = 0
    
    for ret in returns:
        if ret < 0:
            downward_variance += np.power(ret, 2)
        
    downside_risk = np.sqrt(downward_variance / len(returns))
    
    return downside_risk


# In[29]:

def annualized_sortino(returns, N=252):
    """
    Annualized Sortino Ratio: Like the Sharpe Ratio, except only looks at downward volatility.
    """
    return np.sqrt(N) * returns.mean() / downward_volatility(returns)


# In[30]:

def equity_sortino(ticker, start_date=datetime.datetime(2000,1,1), end_date=datetime.datetime(2013,1,1),
                  risk_free_rate=0.05):
    """
    Calculates the annualized Sharpe Ratio based on the daily returns of an
    equity ticker symbol listed on Google Finance (Yahoo Finance because google doesn't work). 
    """
    
    # Obtain the equities daily historic data for the desired time-period and add to a pandas DataFrame
    pdf = web.DataReader(ticker, 'yahoo', start_date, end_date)
    
    # Use the percentage change method to easily calculate daily returns
    pdf['daily_ret'] = pdf['Close'].pct_change()
    
    # Assume an average annual risk-free rate over the period of 5%
    pdf['excess_daily_ret'] = pdf['daily_ret'] - risk_free_rate/252
    
    # Return the annualized Sharpe Ratio based on the excess daily returns
    return annualized_sortino(pdf['excess_daily_ret'])


# In[31]:

equity_sortino('GOOG')
# Sortino is commonly used in high-volatility assets. i.e. It's probably good for crypto.


# In[ ]:



