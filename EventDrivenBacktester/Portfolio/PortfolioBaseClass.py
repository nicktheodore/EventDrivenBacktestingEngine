
# coding: utf-8

# In[3]:

# PortfolioBaseClass


# In[4]:

from __future__ import print_function

import datetime
from math import floor
try:
    import Queue as queue
except ImportError:
    import queue

import numpy as np
import pandas as pd

from EventClasses import FillEvent, OrderEvent
from PerformanceTools import create_sharpe_ratio, create_drawdowns


# In[7]:

class Portfolio(object):
    """
    The Portfolio class handles the positions and market value of all instruments at a resolution
    of a "bar"; i.e. secondly, minutely, 5-min, 30-min, 60-min, or EOD.
    
    The positions DataFrame stores a time-index of the quantity of positions held.
    
    The holdings DataFrame stores the cash and total market holdings value of each symbol for a particular
    time-index, as well as the percentage change in portfolio total across bars.
    
    The Portfolio object must be able to handle SignalEvent objects, generate OrderEvent objects, and 
    interpret FillEvent objects to update positions.
    """
    
    def __init__(self, bars, events, start_date, initial_capital=100000.0):
        """
        Initializes the Portfolio with bars and an event queue.
        Also includes a starting datetime index and initial capital ($USD unless otherwise stated).
        
        Parameters
        ----------
        @bars: The DataHandler object with current market data.
        @events: The Event Queue object.
        @start_date: The start date (bar) of the portfolio.
        @initial_capital: The starting capital in USD.
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital
        
        self.all_positions = self.construct_all_positions()
        self.current_positions = dict((k,v) for k,v in [(s,0) for s in self.symbol_list]) # Dictionary comprehension...
        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()
        
    def construct_all_positions(self):
        """
        Construct the positions list using the start_date to determine when the time index will begin.
        """
        # Creates a dictionary for each symbol, sets a value of 0 for each, adds a datetime key, adds it to a list.
        d = dict((k,v) for k,v in [(s,0) for s in self.symbol_list]) # self.current_positions
        d['datetime'] = self.start_date
        
        return [d]
    
    def construct_all_holdings(self):
        """
        Constructs the historical list of all symbol holdings, using the start_date to determine
        when the time index will begin.
        """
        d = dict((k,v) for k,v in [(s,0.0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        
        return [d]
    
    def construct_current_holdings(self):
        """
        Constructs the most up-to-date dictionary for the instantaneous value of the Portfolio across
        all symbol holdings.
        """
        d = dict((k,v) for k,v in [(s,0.0) for s in self.symbol_list])
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        
        return d
    
    def update_timeindex(self, event):
        """
        This method handles the new holdings tracking. It obtains the latest prices from the market data handler,
        and creates a new dictionary of symbols to represent the current positions, by setting the "new" positions
        equal to the "current" positions.
        
        Adds a new record to the positions matrix for the current market data bar.
        This reflects the PREVIOUS bar, i.e. all current market data at this stage is known (OHLCV).
        
        Makes use of a MarketEvent from the events queue.
        """
        latest_datetime = self.bars.get_latest_bar_datetime(self.symbol_list[0])
        
        # Update positions
        # ================
        dp = dict((k,v) for k,v in [(s,0) for s in self.symbol_list])
        dp['datetime'] = latest_datetime
        
        for s in self.symbol_list:
            dp[s] = self.current_positions[s]
            
        # Append the current positions
        self.all_positions.append(dp)
        
        # Update holdings
        # ===============
        dh = dict((k,v) for k,v in [(s,0) for s in self.symbol_list])
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']
        
        for s in self.symbol_list:
            # Approximation to the real value
            market_value = self.current_positions[s] * self.bars.get_latest_bar_value(s, "adj_close")
            dh[s] = market_value
            dh['total'] += market_value
            
        # Append the current holdings
        self.all_holdings.append(dh)
        
    def update_positions_from_fill(self, fill):
        """
        Takes a Fill object and updates the position matrix to reflect the new position.
        Determines whether a Fill event is a Buy or a Sell, the updates the current_positions
        dictionary accordingly by adding/subtracting the correct quantity of shares.
        
        Parameters
        ----------
        @fill: The Fill object to update the positions with.
        """
        # Check whether the Fill is a Buy or a Sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.directoin == 'SELL':
            fill_dir = -1
        
        # Update positions list with new quantities
        self.current_positions[fill.symbol] += fill_dir*fill.quantity
    
    def update_holdings_from_fill(self, fill):
        """
        Takes a Fill object and updates the holdings matrix to reflect the holdings value.
        NOTE: This method does not use the cost associated from the FillEvent. This is because
        the market impact and depth of book are unknown, thus the fill cost is unkown.
        
        Thus, the fill cost is set to the current market price (closing of last bar).
        Fill cost * transacted quantity is a reasonable approximation for low frequency
        strategies in liquid markets.
        
        Once the fill cost is known, current holdings, cash, and total values can all be updated along 
        with cumulative commission.
        
        Parameters
        ----------
        @fill: The Fill object to update the holdings with.
        """
        # Check whether the Fill is a Buy or a Sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
        
        # Update holdings list with new quantities
        fill_cost = self.bars.get_latest_bar_value(fill.symbol, "adj_close")
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)
        
    def udpate_fill(self, event):
        """
        Updates the portfolio current positions and holdings from a FillEvent.
        Calls update_positions_from_fill and update_holdings_from_fill upon receiving
        a fill event.
        
        Parameters
        ----------
        @event: The Event object being passed into subsequent methods as a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)
    
    def generate_naive_order(self, signal):
        """
        Simply files an Order object as a constant quantity sizing of the signal object, 
        WITHOUT risk management or position sizing considerations.
        
        Generates an OrderEvent from a SignalEvent to go long or short on a fixed 100 shares of an asset.
        Since the method is 'naive', 100 is chosen as an arbitrary quantity. In a production system, this will
        depend upon the portfolio's total equity.
        
        Corresponding OrderEvent objects are then generated.
        
        In a realistic implementation, this value will be determined by a risk-management or position-sizing overlay.
        This can be implemented with a more complex Order Management System (OMS).
        
        Parameters
        ----------
        @signal: The tuple containing Signal information.
        """
        order = None
        
        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength
        
        mkt_quantity = 100
        cur_quantity = self.current_positions[symbol]
        order_type = 'MKT'
        
        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
            
        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
            
        return order

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders based on the portfolio logic.
        Calls generate_naive_order() and adds the generated order to the events queue.
        
        Parameters
        ----------
        @event: The SignalEvent being passed to the Portfolio
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings list of dictionaries.
        Creates a returns stream and normalizes the equity curve to be percentage-based.
        Thus, initial account size is 1.0, as opposed to the absolute dollar amount.
        """
        # returns the cumulative product for percent change over every timestamp in the index
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve
    
    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio based on the strategy's performance.
        """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']
        
        sharpe_ratio = create_sharpe_ratio(returns) #, periods=252*6.5*60) ??? 
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown
        
        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)), 
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio), 
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)), 
                 ("Drawdown Duration", "%d" % dd_duration)]
        
        self.equity_curve.to_csv('equity.csv')
        
        return stats


# In[6]:

class PortfolioHFT(object):
    """
    The Portfolio class handles the positions and market value of all instruments at a resolution
    of a "bar"; i.e. secondly, minutely, 5-min, 30-min, 60-min, or EOD.
    
    The positions DataFrame stores a time-index of the quantity of positions held.
    
    The holdings DataFrame stores the cash and total market holdings value of each symbol for a particular
    time-index, as well as the percentage change in portfolio total across bars.
    
    The Portfolio object must be able to handle SignalEvent objects, generate OrderEvent objects, and 
    interpret FillEvent objects to update positions.
    """
    
    def __init__(self, bars, events, start_date, initial_capital=100000.0):
        """
        Initializes the Portfolio with bars and an event queue.
        Also includes a starting datetime index and initial capital ($USD unless otherwise stated).
        
        Parameters
        ----------
        @bars: The DataHandler object with current market data.
        @events: The Event Queue object.
        @start_date: The start date (bar) of the portfolio.
        @initial_capital: The starting capital in USD.
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital
        
        self.all_positions = self.construct_all_positions()
        self.current_positions = dict((k,v) for k,v in [(s,0) for s in self.symbol_list]) # Dictionary comprehension...
        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()
        
    def construct_all_positions(self):
        """
        Construct the positions list using the start_date to determine when the time index will begin.
        """
        # Creates a dictionary for each symbol, sets a value of 0 for each, adds a datetime key, adds it to a list.
        d = dict((k,v) for k,v in [(s,0) for s in self.symbol_list]) # self.current_positions
        d['datetime'] = self.start_date
        
        return [d]
    
    def construct_all_holdings(self):
        """
        Constructs the historical list of all symbol holdings, using the start_date to determine
        when the time index will begin.
        """
        d = dict((k,v) for k,v in [(s,0.0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        
        return [d]
    
    def construct_current_holdings(self):
        """
        Constructs the most up-to-date dictionary for the instantaneous value of the Portfolio across
        all symbol holdings.
        """
        d = dict((k,v) for k,v in [(s,0.0) for s in self.symbol_list])
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        
        return d
    
    def update_timeindex(self, event):
        """
        This method handles the new holdings tracking. It obtains the latest prices from the market data handler,
        and creates a new dictionary of symbols to represent the current positions, by setting the "new" positions
        equal to the "current" positions.
        
        Adds a new record to the positions matrix for the current market data bar.
        This reflects the PREVIOUS bar, i.e. all current market data at this stage is known (OHLCV).
        
        Makes use of a MarketEvent from the events queue.
        """
        latest_datetime = self.bars.get_latest_bar_datetime(self.symbol_list[0])
        
        # Update positions
        # ================
        dp = dict((k,v) for k,v in [(s,0) for s in self.symbol_list])
        dp['datetime'] = latest_datetime
        
        for s in self.symbol_list:
            dp[s] = self.current_positions[s]
            
        # Append the current positions
        self.all_positions.append(dp)
        
        # Update holdings
        # ===============
        dh = dict((k,v) for k,v in [(s,0) for s in self.symbol_list])
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']
        
        for s in self.symbol_list:
            # Approximation to the real value
            market_value = self.current_positions[s] * self.bars.get_latest_bar_value(s, "close")
            dh[s] = market_value
            dh['total'] += market_value
            
        # Append the current holdings
        self.all_holdings.append(dh)
        
    def update_positions_from_fill(self, fill):
        """
        Takes a Fill object and updates the position matrix to reflect the new position.
        Determines whether a Fill event is a Buy or a Sell, the updates the current_positions
        dictionary accordingly by adding/subtracting the correct quantity of shares.
        
        Parameters
        ----------
        @fill: The Fill object to update the positions with.
        """
        # Check whether the Fill is a Buy or a Sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.directoin == 'SELL':
            fill_dir = -1
        
        # Update positions list with new quantities
        self.current_positions[fill.symbol] += fill_dir*fill.quantity
    
    def update_holdings_from_fill(self, fill):
        """
        Takes a Fill object and updates the holdings matrix to reflect the holdings value.
        NOTE: This method does not use the cost associated from the FillEvent. This is because
        the market impact and depth of book are unknown, thus the fill cost is unkown.
        
        Thus, the fill cost is set to the current market price (closing of last bar).
        Fill cost * transacted quantity is a reasonable approximation for low frequency
        strategies in liquid markets.
        
        Once the fill cost is known, current holdings, cash, and total values can all be updated along 
        with cumulative commission.
        
        Parameters
        ----------
        @fill: The Fill object to update the holdings with.
        """
        # Check whether the Fill is a Buy or a Sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
        
        # Update holdings list with new quantities
        fill_cost = self.bars.get_latest_bar_value(fill.symbol, "close")
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)
        
    def udpate_fill(self, event):
        """
        Updates the portfolio current positions and holdings from a FillEvent.
        Calls update_positions_from_fill and update_holdings_from_fill upon receiving
        a fill event.
        
        Parameters
        ----------
        @event: The Event object being passed into subsequent methods as a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)
    
    def generate_naive_order(self, signal):
        """
        Simply files an Order object as a constant quantity sizing of the signal object, 
        WITHOUT risk management or position sizing considerations.
        
        Generates an OrderEvent from a SignalEvent to go long or short on a fixed 100 shares of an asset.
        Since the method is 'naive', 100 is chosen as an arbitrary quantity. In a production system, this will
        depend upon the portfolio's total equity.
        
        Corresponding OrderEvent objects are then generated.
        
        In a realistic implementation, this value will be determined by a risk-management or position-sizing overlay.
        This can be implemented with a more complex Order Management System (OMS).
        
        Parameters
        ----------
        @signal: The tuple containing Signal information.
        """
        order = None
        
        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength
        
        mkt_quantity = 100
        cur_quantity = self.current_positions[symbol]
        order_type = 'MKT'
        
        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
            
        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
            
        return order

    def update_signal(self, event):
        """
        Acts on a SignalEvent to generate new orders based on the portfolio logic.
        Calls generate_naive_order() and adds the generated order to the events queue.
        
        Parameters
        ----------
        @event: The SignalEvent being passed to the Portfolio
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings list of dictionaries.
        Creates a returns stream and normalizes the equity curve to be percentage-based.
        Thus, initial account size is 1.0, as opposed to the absolute dollar amount.
        """
        # returns the cumulative product for percent change over every timestamp in the index
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve
    
    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio based on the strategy's performance.
        """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']
        
        sharpe_ratio = create_sharpe_ratio(returns, periods=252*6.5*60)
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown
        
        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)), 
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio), 
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)), 
                 ("Drawdown Duration", "%d" % dd_duration)]
        
        self.equity_curve.to_csv('equity.csv')
        
        return stats


# In[ ]:



