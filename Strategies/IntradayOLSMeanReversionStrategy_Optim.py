
# coding: utf-8

# In[1]:

# IntradayOLSMeanReversionStrategy


# In[2]:

from __future__ import print_function

import datetime

import numpy as np
import pandas as pd
import statsmodels.api as sm

from itertools import product

from EventDrivenBacktester.StrategyABC import Strategy
from EventDrivenBacktester.EventClasses import SignalEvent
from EventDrivenBacktester.Backtester import Backtest
from EventDrivenBacktester.DataHandlerABC import HistoricCSVDataHandlerHFT
from EventDrivenBacktester.Portfolio.PortfolioBaseClass import PortfolioHFT
from EventDrivenBacktester.ExecutionHandler import SimulatedExecutionHandler


# In[3]:

class IntradayOLSMRStrategy(Strategy):
    """
    Uses Ordinary Least Squares (OLS) to perform a rolling linear regression to determine
    the optimal hedge ratio between a pair of equities.
    
    The Z-score of the residuals timeseries is then calculated in a rolling fashion. If it
    exceeds an interval of thresholds (defaulting to [0.5, 3.0]), then a long/short signal pair
    are generated (for the high threshold), or an exit signal pair are generated (for the low threshold).
    """
    
    def __init__(self, bars, events, ols_window=100, zscore_low=0.5, zscore_high=3.0):
        """
        Initializes the statistical arbitrage strategy.
        
        Parameters
        ----------
        @bars: The DataHandler object that provides bar information.
        @events: The Event Queue object.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.ols_window = ols_window
        self.zscore_low = zscore_low
        self.zscore_high = zscore_high
        
        # Energy sector equities pair, previously determined to possess mean-reverting behaiour.
        self.pair = ('AREX', 'WLL') 
    
        self.datetime = datetime.datetime.utcnow()
        
        self.long_market = False
        self.short_market = False
    
    def calculate_xy_signals(self, zscore_last):
        """
        Calculates the actual x, y signal pairings to be sent to the signal generator.
        [...]
        
        Parameters
        ----------
        @zscore_last: The current Z-score to test against.
        
        @return: y_signal, x_signal
        """
        y_signal = None
        x_signal = None
        
        p0 = self.pair[0]
        p1 = self.pair[1]
        
        dt = self.datetime
        hr = abs(self.hedge_ratio)
        
        # If we're long the market and below the negative of the high zscore threshold
        if zscore_last <= -self.zscore_high and not self.long_market:
            self.long_market = True
            y_signal = SignalEvent(1, p0, dt, 'LONG', 1.0)
            x_signal = SignalEvent(1, p1, dt, 'SHORT', hr) # Passing info about the hedging ratio around the system
            
        # If we're long the market and between the absolute value of the low zscore threshold
        if abs(zscore_last) <= self.zscore_low and self.long_market:
            self.long_market = False
            y_signal = SignalEvent(1, p0, dt, 'EXIT', 1.0) # All exits are 1.0
            x_signal = SignalEvent(1, p1, dt, 'EXIT', 1.0)
        
        # If we're short the market and above the high zscore threshold
        if zscore_last >= self.zscore_high and not self.short_market:
            self.short_market = True
            y_signal = SignalEvent(1, p0, dt, 'SHORT', 1.0)
            x_signal = SignalEvent(1, p1, dt, 'LONG', hr)
            
        # If we're short the market and between the absolute value of the low zscore threshold
        if abs(zscore_last) <= self.zscore_low and self.short_market:
            self.short_market = False
            y_signal = SignalEvent(1, p0, dt, 'EXIT', 1.0)
            x_signal = SignalEvent(1, p1, dt, 'EXIT', 1.0)
            
        return y_signal, x_signal
            
    def calculate_signals_for_pairs(self):
        """
        Generates a new set of signals based on the mean reversion strategy.
        Calculates the hedge ratio between the pair of tickers. We use OLS for this, 
        although we should ideally use the Cointegrated Augmented Dickey-Fuller test.
        """
        # Obtain the latest window of values for each component of the pair of tickers
        y = self.bars.get_latest_bars_values(self.pair[0], "close", N=self.ols_window)
        x = self.bars.get_latest_bars_values(self.pair[1], "close", N=self.ols_window)
        
        # Check that x and y contain values
        if y is not None and x is not None:
            # Check that all window periods are available
            if len(y) >= self.ols_window and len(x) >= self.ols_window:
                # Calculate the current hedge ratio using OLS. 
                # Don't worry about not having defined self.hedge_ratio, this is valid Python.
                self.hedge_ratio = sm.OLS(y,x).fit().params[0]
                
                # Calculate the current z-score of the residuals, get the last z-score
                spread = y - self.hedge_ratio * x
                zscore_last = ((spread - spread.mean())/spread.std())[-1]
                
                # Calculate signals and add to events queue
                y_signal, x_signal = self.calculate_xy_signals(zscore_last)
                if y_signal is not None and x_signal is not None:
                    self.events.put(y_signal)
                    self.events.put(x_signal)
                    
    def calculate_signals(self, event):
        """
        Calculate the SignalEvents based on market data.
        """
        if event.type == 'MARKET':
            self.calculate_signals_for_pairs()


# In[4]:

if __name__ == "__main__":
    csv_dir = ''
    symbol_list = ['AREX', 'WLL']
    initial_capital = 100000.0
    heartbeat = 0.0
    start_date = datetime.datetime(2007, 11, 8, 10, 41, 0)
    
    # 1. Create the strategy parameter grid using the itertools cartesian product generator (product())
    strat_lookback = [50, 100, 200]
    strat_z_entry  = [2.0, 3.0, 4.0]
    strat_z_exit   = [0.5, 1.0, 1.5]
    strat_params_list = list(product(strat_lookback, strat_z_entry, strat_z_exit)) # Cartesian Product as a list
    
    # 2. Create a list of dictionaries with the correct keyword/value pairs for the strategy parameters
    strat_params_dict_list = [
        dict(ols_window=sp[0], z_score_high=sp[1], zscore_low=sp[2]) for sp in strat_params_list
    ]
    
    # 3. Carry out the set of backtests for all parameter combinations (new parameter, @strat_params_list)
    backtest = Backtest(csv_dir, symbol_list, initial_capital, heartbeat, start_date,
                        HistoricCSVDataHandlerHFT, SimulatedExecutionHandler, PortfolioHFT, IntradayOLSMRStrategy,
                        strat_params_list=strat_params_dict_list)
    
    backtest.simulate_trading()


# In[ ]:



