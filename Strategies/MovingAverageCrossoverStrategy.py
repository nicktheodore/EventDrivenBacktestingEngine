
# coding: utf-8

# In[1]:

#MovingAverageCrossoverStrategy


# In[2]:

from __future__ import print_function

import datetime

import numpy as np

from EventDrivenBacktester.Backtester import Backtest
from EventDrivenBacktester.DataHandlerABC import HistoricCSVDataHandler
from EventDrivenBacktester.EventClasses import SignalEvent
from EventDrivenBacktester.ExecutionHandler import SimulatedExecutionHandler
from EventDrivenBacktester.StrategyABC import Strategy
from Portfolio.PortfolioBaseClass import Portfolio


# In[3]:

class MovingAverageCrossoverStrategy(Strategy):
    """
    Carries out a basic Moving Average Crossover strategy with a long/short simple weighted moving average.
    Default long/short windows are 400/100 periods respectively.
    """
    
    def __init__(self, bars, events, short_window=100, long_window=400):
        """
        Initializes the Moving Average Crossover Strategy.
        
        Parameters
        ----------
        @bars: The DataHandler object that provides bar information.
        @events: The Event Queue object.
        @short_window: The short moving-average lookback.
        @long_window: The long moving-average lookback.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.short_window = short_window
        self.long_window = long_window
        
        # Set to true if a symbol is in the market
        self.bought = self._calculate_initial_bought()
        
    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols and sets them to 'OUT'.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'
        return bought
    
    def calculate_signals(self, event):
        """
        Generates a new set of signals based on the Moving Average Crossover's SMA with the short window
        crossing the long window, meaning a long entry, and vice-versa for a short entry.
        
        Parameters
        ----------
        @event: A MarketEvent Object.
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars_values(s, "adj_close", N=self.long_window)
                bar_date = self.bars.get_latest_bar_datetime(s)
                
                if bars is not None and bars != []:
                    short_sma = np.mean(bars[-self.short_window:])
                    long_sma  = np.mean(bars[-self.long_window:])
                    
                    symbol = s
                    dt = datetime.datetime.utcnow()
                    sig_dir = ""
                    
                    if short_sma > long_sma and self.bought[s] == 'OUT':
                        print("LONG: %s" % bar_date)
                        sig_dir = 'LONG'
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'LONG'
                    elif short_sma < long_sma and self.bought[s] == 'LONG':
                        print("SHORT: %s" % bar_date)
                        sig_dir = 'EXIT'
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'OUT'


# In[4]:

if __name__ == "__main__":
    csv_dir = '' # Absolute path to the CSV data
    symbol_list = ['AAPL']
    initial_capital = 100000.0
    heartbeat = 0.0
    start_date = datetime.datetime(1990, 1, 1, 0, 0, 0)
    
    backtest = Backtest(csv_dir, symbol_list, initial_capital, heartbeat, start_date,
                          HistoricCSVDataHandler, SimulatedExecutionHandler, Portfolio,
                          MovingAverageCrossoverStrategy)
    
    backtest.simulate_trading()


# In[ ]:



