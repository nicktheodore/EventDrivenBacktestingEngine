
# coding: utf-8

# In[1]:

# ExecutionHanlder


# In[2]:

from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime

try:
    import Queue as queue
except ImportError:
    import queue

from EventDrivenBacktester.EventClasses import FillEvent, OrderEvent


# In[4]:

class ExecutionHandler(object):
    """
    The ExecutionHandler abstract base class handles the interaction between a set of Order objects
    generated by a Portfolio and the ultimate set of Fill objects that actually occur in the market.
    
    Tha handlers can be used to subclass simulated brokerages or live brokerages, with identical interfaces.
    This allows strategies to be backtested in a very similar manner to the live trading engine.
    """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def execute_order(self, event):
        """
        Takes an Order event and executes it, producing a Fill event that gets placed onto the Events queue.
        
        Parameters
        ----------
        @event: Contains an Event object with order information.
        """
        raise NotImplementedError("Missing implementation for execute_order()")


# In[5]:

class SimulatedExecutionHandler(ExecutionHandler):
    """
    The simulated execution handler simply converts all order objects into
    their equivalent fill objects automatically WITHOUT latency, slippage,
    or fill-ratio issues.
    
    This allows a straightforward "first go" test of any strategy, before implementation
    with a more sophisticated execution handler. 
    
    NOTE: This implementation of an ExecutionHandler is highly unrealistic, and assumes
    that all orders are being filled at current market price for all quantities.
    """
    
    def __init__(self, events):
        """
        Initializes the handler, setting the event queues up internally.
        
        Parameters
        ----------
        @events: The Queue of Event objects.
        """
        self.events = events

    def execute_order(self, event):
        """
        Simply converts Order objects into Fill objects naively, i.e. WITHOUT any
        latency, slippage, or fill-ratio issues.
        
        Parameters
        ----------
        @event: Contains an Event object with order information.
        """
        if event.type == 'ORDER':
            fill_event = FillEvent(datetime.datetime.utcnow(), event.symbol, 'ARCA', 
                                   event.quantity, event.direction, None)
            self.events.put(fill_event)


# In[ ]:



