
# coding: utf-8

# In[1]:

# EventClasses

from __future__ import print_function


# In[2]:

class Event(object):
    """
    Event is a base class providing an interface for all subsequent inherited events. Such events will
    trigger further events in the trading infrastructure
    """
    pass


# In[3]:

class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with corresponding bars.
    """
    
    def __init__(self):
        """
        Initializes the market event
        """
        self.type = "MARKET"


# In[4]:

class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and subsequently acted upon.
    """
    
    def __init__(self, strategy_id, symbol, datetime, signal_type, strength):
        """
        Initializes the SignalEvent.
        
        Parameters
        ----------
        @strategy_id: The unique identifier for the strategy that generated the signal.
        @symbol: The ticker symbol, e.g.: 'GOOG'.
        @datetime: The timestamp at which the signal was generated.
        @signal_type: 'LONG' or 'SHORT'.
        @strength: An adjustement factor "suggestion" used to scale quantity at the portfolio level.
            Useful for pairs-based strategies.
        """
        self.type = 'SIGNAL'
        self.strategy_id = strategy_id
        self.datetime = datetime
        self.signal_type = signal_type
        self.strength = strength


# In[5]:

class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g.: 'GOOG'), a type (market or limit), a quantity, and a direction
    """
    
    def __init__(self, symbol, order_type, quantity, direction):
        """
        Initializes the order type, setting whether it is a Market order ('MKT') or Limit order ('LMT'), 
        has a quantity (integral), and its direction ('BUY' or 'SELL') for long or short positions.
        
        Parameters
        ----------
        @symbol: The instrument to trade.
        @order_type: 'MKT' or 'LMT' for Market or Limit, respectively.
        @quantity: Non-negative integer for quantity.
        @direction: 'BUY' or 'SELL' (e.x.: 'SELL' all 'LONG' positions, 'BUY' more 'SHORT' positions, etc...).
        """
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction
        
    def  print_order(self):
        """
        Outputs the values within the Order
        """
        print(
            "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" %
             (self.symbol, self.order_type, self.quantity, self.direction)
             )


# In[6]:

class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores the commission of the trade from the brokerage.
    """
    
    def __init__(self, timeindex, symbol, exchange, quantity, direction, fill_cost, commission=None):
        """
        Initializes the FillEvent object. Sets the symbol, exchange, quantity, direction, cost of fill,
        and an optional commission.
        
        If commission is not provided, the Fill object will calculate it based on the trade size
        and Interactive Brokers fees.
        
        Parameters
        ----------
        @timeindex: The bar-resolution when the order was filled.
        @symbol: The instrument which was filled.
        @exchange: The exchange where the order was filled.
        @quantity: The filled quantity.
        @direction: The direction of fill ('BUY' or 'SELL').
        @fill_cost: The holdings value in dollars ($).
        @commission: An optional commission sent from Interactive Brokers.
        """
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost
        
        # Calculate commission
        if commission is None:
            self.commission = self.calculate_ib_commission()
        else:
            self.commission = commission
        
    def calculate_ib_commission(self):
        """
        Calculates the fees of trading based on an Interactive Brokers fee structure for the API, in $USD.
        
        This does not include any exchange or ECN fees.
        
        Based on "US API Directed Orders":
        https://www.interactivebrokers.com/en/index.php?f=commission&p=stocks2
        """
        full_cost = 1.3
        if self.quantity <= 500:
            full_cost = max(1.3, 0.013 * self.quantity)
        else: # Greater than 500
            full_cost = max(1.3, 0.008 * self.quantity)
        return full_cost


# In[ ]:


