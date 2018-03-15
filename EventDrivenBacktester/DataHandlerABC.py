
# coding: utf-8

# In[4]:

# DataHandlerABC

from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime
import os, os.path

import numpy as np
import pandas as pd

from EventDrivenBacktester.EventClasses import MarketEvent

# Useful links for Abstract Base Classes and decorators:
# https://docs.python.org/3/library/abc.html
# https://isocpp.org/wiki/faq/abcs
# https://realpython.com/blog/python/primer-on-python-decorators/


# In[5]:

class DataHandler(object):
    """
    DataHandler is an abstract base class (ABC) providing an interface for all 
    susequent (inherited) data handlers (both live and historic).
    
    The goal of a (derived) DataHandler object is to output a generated set of bars (OHLCVI)
    for each symbol requested.
    
    This will replace how a live strategy would function as curren market data would be sent 
    "down the pipe". Thus, a historic and live system will be treated identically by the rest
    of the backtesting suite.
    """
    
    # __metaclass__ Lets Python know that this is an ABC
    # @abstractmethod decorator lets Python know that the method will be overridden in subclasses
    # This is identical to a "pure virtual method" in C++
    # Wraps the function by taking it in as an argument and modifying it's behaviour. @decorator is syntactical sugar
    # More information on decorators: https://realpython.com/blog/python/primer-on-python-decorators/
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_latest_bar(self, symbol):
        """
        Returns the last bar updated for a given symbol.
        """
        raise NotImplementedError("Missing implementation for get_latest_bar()")
    
    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars updated for a given symbol.
        """
        raise NotImplementedError("Missing implementation for get_latest_bars()")
        
    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar of a given symbol.
        """
        raise NotImplementedError("Missing implementation for get_latest_bar_datetime()")
    
    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume, or OI (Open Interest) from
        the last bar (val_type).
        
        Note: Open Interest is the total number of outstanding contracts that are held
        by market participants at the end of the day. OI measures the flow of money into the Futures market.
        """
        raise NotImplementedError("Missing implementation for get_latest_bar_value()")
        
    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the latest_symbol list, or N-k if less available.
        """
        raise NotImplementedError("Missing implementation for get_latest_bars_values()")
        
    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bars to the bars_queue for each symbol in a tuple of OHLCVI format:
        (datetime, open, high, low, close, volume, open interest). 
        
        Provides a 'drip-feed' mechanism for placing bar information into the bars_queue data structure.
        """
        raise NotImplementedError("Missing implementation for update_bars()")


# In[7]:

# Create an implementation of the DataHandler ABC. Recall that ABCs cannot be directly implemented.
# ABCs require subclassing for all appropriate interfaces that wish to conform to their functionality.

class HistoricCSVDataHandler(DataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for each requested symbol
    from a disk and provide an interface to obtain the "latest" bar, in a manner
    that is identical to a live trading interface.
    
    HistoricCSVDataHandler processes multiple CSV files, one for each traded symbol, and converts them into
    a dictionary of pandas DataFrames. The DataFramess can then be accessed by the bar methods inherited from 
    the DataHandler abstract base class.
    """
    
    def __init__(self, events, csv_dir, symbol_list):
        """
        Initialized the historic data handler by requesting the location of the CSV files
        and a list of symbols.
        
        It will be assumed that all files are of the form 'symbol.csv', where symbol is a string
        in the list.
        
        Parameters
        ----------
        @events: The Event Queue.
        @csv_dir: Absolute directory path to the CSV files.
        @symbol_list: A list of symbol strings.
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        
        self._open_convert_csv_files()
    
    # Python convention: '_' before a name denotes a non-public (private) part of the API.
    
    def _open_convert_csv_files(self): # private method
        """
        Opens the CSV files from the data directory, converting them into pandas DataFrames within
        a dictionary of symbols.
        
        For this handler, it will be assumed that the data is taken from Yahoo Finance. Thus, its format
        will be respected.
        """
        comb_index = None
        
        # Iterates through all the symbols we're storing in the dictionary of DataFrames
        for s in self.symbol_list:
            # Load the CSV file with no header information, indexed on date
            self.symbol_data[s] = pd.read_csv(
                os.path.join(self.csv_dir, '%.csv', '%s'),
                header=0, index_col=0, parse_dates=True,
                names=['datetime', 'open', 'high', 'low', 'close', 'volume', 'adj_close']
            ).sort()
            
            # Combine the index to pad forward values
            # Merges all the indexes with a union so that the index is completely filled
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)
            
            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []
            
        # Reindex the DataFrames for all symbols and pad missing values
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()
    
    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed. 
        Subsequent calls to this method will 'yield' a new bar until the end of the symbol data is reached.
        """
        for b in self.symbol_data[symbol]:
            yield b

            
    #----- Implementation of abstract methods from the parent abstract base class, DataHandler -----#
    
    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol_data list.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise # Reraise the current exception in an exception handler to be handled further up the call stack.
        else:
            return bars_list[-1]
    
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N::]
        
    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object corresponding to the last bar's timestamp.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1][0]
    
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume, or OI values from the
        pandas Bar series object.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return getattr(bars_list[-1][-1], val_type)
    
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])
    
    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s)) # https://docs.python.org/2/library/functions.html#next
            except StopIteration:
                # Stops the backtest when there are no more bars left
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent()) # Enqueues MarketEvent() to events: https://docs.python.org/2/library/queue.html
        


# In[1]:

# Create an implementation of the DataHandler ABC. Recall that ABCs cannot be directly implemented.
# ABCs require subclassing for all appropriate interfaces that wish to conform to their functionality.

class HistoricCSVDataHandlerHFT(DataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for each requested symbol
    from a disk and provide an interface to obtain the "latest" bar, in a manner
    that is identical to a live trading interface.
    
    HistoricCSVDataHandler processes multiple CSV files, one for each traded symbol, and converts them into
    a dictionary of pandas DataFrames. The DataFramess can then be accessed by the bar methods inherited from 
    the DataHandler abstract base class.
    """
    
    def __init__(self, events, csv_dir, symbol_list):
        """
        Initialized the historic data handler by requesting the location of the CSV files
        and a list of symbols.
        
        It will be assumed that all files are of the form 'symbol.csv', where symbol is a string
        in the list.
        
        Parameters
        ----------
        @events: The Event Queue.
        @csv_dir: Absolute directory path to the CSV files.
        @symbol_list: A list of symbol strings.
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        
        self._open_convert_csv_files()
    
    # Python convention: '_' before a name denotes a non-public (private) part of the API.
    
    def _open_convert_csv_files(self): # private method
        """
        Opens the CSV files from the data directory, converting them into pandas DataFrames within
        a dictionary of symbols.
        
        For this handler, it will be assumed that the data is taken from Yahoo Finance. Thus, its format
        will be respected.
        """
        comb_index = None
        
        # Iterates through all the symbols we're storing in the dictionary of DataFrames
        for s in self.symbol_list:
            # Load the CSV file with no header information, indexed on date
            self.symbol_data[s] = pd.read_csv(
                os.path.join(self.csv_dir, '%.csv', '%s'),
                header=0, index_col=0, parse_dates=True,
                names=['datetime', 'open', 'low', 'high', 'close', 'volume', 'oi']
            ).sort()
            
            # Combine the index to pad forward values
            # Merges all the indexes with a union so that the index is completely filled
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)
            
            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []
            
        # Reindex the DataFrames for all symbols and pad missing values
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()
    
    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed. 
        Subsequent calls to this method will 'yield' a new bar until the end of the symbol data is reached.
        """
        for b in self.symbol_data[symbol]:
            yield b

            
    #----- Implementation of abstract methods from the parent abstract base class, DataHandler -----#
    
    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol_data list.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise # Reraise the current exception in an exception handler to be handled further up the call stack.
        else:
            return bars_list[-1]
    
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-N::]
        
    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object corresponding to the last bar's timestamp.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return bars_list[-1][0]
    
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume, or OI values from the
        pandas Bar series object.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return getattr(bars_list[-1][-1], val_type)
    
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])
    
    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s)) # https://docs.python.org/2/library/functions.html#next
            except StopIteration:
                # Stops the backtest when there are no more bars left
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent()) # Enqueues MarketEvent() to events: https://docs.python.org/2/library/queue.html
        


# In[ ]:



