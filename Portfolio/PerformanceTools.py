
# coding: utf-8

# In[1]:

# Performance tools


# In[2]:

from __future__ import print_function

import numpy as np
import pandas as pd


# In[3]:

def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a benchmark of zero (i.e. no risk-free rate information).
    
    Parameters
    ----------
    @returns: A pandas Series representing period percentage returns.
    @periods: Daily (252), Hourly (252*6.5), Minutely (252*6.5*60), etc.
    """
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)


# In[4]:

def create_drawdowns(pnl):
    """
    Calculate the largest peak-to-trough drawdown for the PnL curve, as well as the duration
    of the drawdown. 
    Requires that the pnl returns is a pandas Series.
    
    Parameters
    ----------
    @pnl: A pandas Series representing period percentage returns
    
    Returns
    -------
    :drawdown: Highest to peak-to-trough drawdown.
    :duration: Longest duration spent in drawdown.
    """
    
    # Calculate the cumulative returns curve and set up the High Water Mark
    hwm = [0]
    
    # Create the drawdown and duration series
    idx = pnl.index
    drawdown = pd.Series(index=idx)
    duration = pd.Series(index=idx)
    
    # Loop over the index range
    for t in range(1, len(idx)):
        hwm.append(max(hwm[t-1], pnl[t]))
        drawdown[t] = (hwm[t]-pnl[t])
        duration[t] = (0 if drawdown[t] == 0 else duration[t-1]+1)
    
    return drawdown, drawdown.max(), duration.max()


# In[ ]:



