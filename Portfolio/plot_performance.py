
# coding: utf-8

# In[1]:

# plot_performance.py


# In[2]:

# IMPORTANT: It is necessary to run this in the same directory as the output file from the backtest. Namely,
# where 'equity.csv' resides.


# In[3]:

import os.path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# In[4]:

if __name__ == "__main__":
    data = pd.read_csv("equity.csv", header=0, parse_dates=True, index_col=0).sort()
    
    # Plot three chars: Equity curve, period returns, drawdowns
    fig = plt.figure()
    
    # Set the outer colour to white
    fig.patch.set_facecolor('white')
    
    # Plot the equity curve
    ax1 = fig.add_subplot(311, ylabel='Portfolio Value, %')
    data['equity_curve'].plot(ax=ax1, color="blue", lw=2.)
    plt.grid(True)
    
    # Plot the returns
    ax2 = fig.add_subplot(312, ylabel='Period returns, %')
    data['returns'].plot(ax=ax2, color="black", lw=2.)
    plt.grid(True)
    
    # Plot the drawdown
    ax3 = fig.add_subplot(313, ylabel='Drawdowns, %')
    data['drawdown'].plot(ax=ax3, color="red", lw=2.)
    plt.grid(True)
    
    # Plot the figures
    plt.show()


# In[ ]:



