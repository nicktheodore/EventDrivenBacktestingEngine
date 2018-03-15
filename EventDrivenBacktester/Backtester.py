
# coding: utf-8

# In[1]:

# Backtester


# In[2]:

from __future__ import print_function

import datetime
import pprint

try:
    import Queue as queue
except ImportError:
    import queue
    
import time


# In[5]:

class Backtest(object):
    """
    Encapsulates the settings and components for carrying out an event-driven backtest.
    The Backtest object ties together all of the other classes in the system. This class is
    designed to carry out a nested while-loop event-driven system in order to handle the events
    placed on the Event Queue object. 
    
    The outer while-loop is known as the "heartbeat loop", since it decides the temporal resolution
    of the backtest. In a live environment, this is a positive number representing the timeframe for
    updating market data and positions. For historical data, the heartbeat is set to zero.
    The outer loop ends once the DataHandler lets the Backtest object know with continue_backtest = False.
    
    The inner while-loop actually processes the signals and sends them to the correct component depending
    upon the event type. Thus, the Event Queue is continually being populated and depopulated with events.
    
    This is what it means for a system to be EVENT DRIVEN.
    """
    
    def __init__(self, csv_dir, symbol_list, initial_capital, heartbeat, start_date,
                 data_handler, execution_handler, portfolio, strategy, strat_params_list=None):
        """
        Initializes the Backtest. A Queue is used to hold the Events. The Signals, Orders, and Fills are counted.
        
        Parameters
        ----------
        @csv_dir: The hard root to the CSV data directory.
        @symbol_list: The list of symbol strings.
        @initial_capital: The starting capital for the Portfolio.
        @heartbeat: The Backtester's outer-loop "heartbeat" in seconds.
        @start_date: The start datetime of the strategy.
        @data_handler: (Class) Handles the market data feed.
        @execution_handler: (Class) Handles the orders/fills for trades.
        @portfolio: (Class) Keeps track of the portfolio current and prior positions.
        @strategy: (Class) Generates Signals based on market data.
        """
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date
        
        self.data_handler_class = data_handler
        self.execution_handler_class = execution_handler
        self.portfolio_class = portfolio
        self.strategy_class = strategy
        
        self.strat_params_list = strat_params_list
        
        self.events = queue.Queue()
        
        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1
        
        # Call this in the initialization to populate the other classes with our data
        # self._generate_trading_instances()
        
    def _generate_trading_instances(self, strategy_params_dict):
        """
        Generates the trading instance objects from their class types. This method attaches all of the trading
        objects (DataHandler, Strategy, Portfolio, and ExecutionHandler) to various internal members.
        
        This ties together all the other classes to the Backtester object.
        """
        print("Creating DataHandler, Strategy, Portfolio, and ExecutionHandler for")
        print("strategy parameter list: %s..." % strategy_params_dict)
        
        # Set internal data members equal to the classes we passed in earlier, along with necessary parameters.
        # https://softwareengineering.stackexchange.com/questions/131403/what-is-the-name-of-in-python/131415
        self.data_handler = self.data_handler_class(self.events, self.csv_dir, self.symbol_list)
        self.strategy = self.strategy_class(self.data_handler, self.events, **strategy_params_dict)
        self.portfolio = self.portfolio_class(self.data_handler, self.events, self.start_date, self.initial_capital)
        self.execution_handler = self.execution_handler_class(self.events) # The Event Queue sent to ExecutionHandler
        
    def _run_backtest(self):
        """
        Executes the backtest. This is where the signal handling of the Backtesting engine is carried out.
        There are two while loops, the outer-loop (heartbeat) and the nested inner-loop, which checks if there
        is an event in the Event Queue object. The inner loop acts on the Event by calling the appropriate method
        of the appropriate object. For example, upon receiving a:
        
         MarketEvent:
             - The Strategy object is told to recalculate new Signals.
             - The Portfolio object is told to reindex the time.
         
         SignalEvent:
             - The Portfolio object is told to handle the new signal, converting it to a set of OrderEvents,
               if appropriate. 
        
         OrderEvent:
             - The Order is sent to the ExecutionHandler to be transmitted to the brokerage, if in a real
               trading setting.
        
         FillEvent:
             - The Portfolio object updates itself to be aware of the new positions.
        
        The Event Queue is continually being populated and depopulated with events. This is what it means for a 
        system to be EVENT-DRIVEN.
        """
        i = 0
        
        while True:
            i += 1
            print(i)
            
            # Update the market bars
            if self.data_handler.continue_backtest == True:
                self.data_handler.update_bars()
            else:
                break
            
            # Handle the Events
            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    # The inner-loop acts on the events by calling the appropriate method of the appropriate object
                    if event is not None:
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_timeindex(event)
                            
                        elif event.type == 'SIGNAL':
                            self.signals += 1
                            self.portfolio.update_signal(event)
                            
                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.execution_handler.execute_order(event)
                        
                        elif event.type == 'FILL':
                            self.fills += 1
                            self.portfolio.update_fill(event)
            
            # Pauses for a duration of self.heartbeat seconds
            time.sleep(self.heartbeat)
    
    def _output_performance(self):
        """
        Outputs the strategy performance and other metrics from the backtest.
        """
        self.portfolio.create_equity_curve_dataframe()
        
        print("Creating summary statistics...")
        stats = self.portfolio.output_summary_stats()
        
        print("Creating equity curve...")
        print(self.portfolio.equity_curve.tail(10))
        pprint.pprint(stats)
        
        print("Signals: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % self.fills)
    
    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolio performance.
        
        Loops over all variants of strategy parameters of a space generated by a cartesian product
        of hyperparameter values. Generates new instances of all the data handlers, event queues, and portfolio
        objects upon each iteration, in order to ensure a "clean slate" for each trading instance on every
        simulation.
        
        The parameter combinations and their performance metrics are stored in an output CSV file, which will
        subsequently be used to plot performance characteristics.
        """
        # This should be more general in future implementations...
        # Create the file output stream
        out = open("output/opt.csv", "w")
        
        spl = len(self.strat_params_list)
        for i, sp in enumerate(self.strat_params_list): # http://book.pythontips.com/en/latest/enumerate.html
            print("Strategy %s out of %s..." % (i+1, spl))
            self._generate_trading_instances(sp)
            self._run_backtest()
            stats = self._output_performance()
            pprint.pprint(stats)
            
            tot_ret = float(stats[0][1].replace("%",""))
            cagr = float(stats[1][1].replace("%",""))
            sharpe = float(stats[2][1])
            max_dd = float(stats[3][1].replace("%",""))
            dd_cur = int(stats[4][1])
            
            # This should be more general in future implementations...
            out.write(
                "%s,%s,%s,%s,%s,%s,%s,%s\n" % (sp["ols_window"], sp["zscore_high"], sp["zscore_low"],
                                               tot_ret, cagr, sharpe, max_dd, dd_dur)
            )
            
        out.close()


# In[ ]:



