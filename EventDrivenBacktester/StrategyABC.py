
# coding: utf-8

# In[2]:

# StrategyABC

from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime

try:
    import Queue as queue
except ImportError:
    import queue

import numpy as np
import pandas as pd

from EventDrivenBacktester.EventClasses import SignalEvent


# In[3]:

# A Strategy object encapsulates all calculation on market data that generate 'advisory' signals to a Portfolio object.
# All of the strategy logic resides within this class.
# Strategy is separate from Portfolio object. This facilitates the process of multiple strategies feeding "ideas"
# into a larger Portfolio. The Portfolio can then handle its own risk (e.g. sector allocation, leverage, etc...).
# At this stage, there is no concept of an 'indicator' or 'filter', such as those found in technical trading.
# Such mechanisms will be used directly in subsequently derived Strategy objects.


# In[4]:

class Strategy(object):
    """
    Strategy is an abstract base class providing an interface for all susequent
    (inherited) strategy handling objects.
    
    The goal of a (derived) Strategy object is to generate Signal objects for particular
    symbols based on the inputs of Bars (OHLCV) generated by a DataHandler object.
    
    This is designed to work both with historic and live data as the Strategy object is 
    agnostic to where the data came from. This is because it obtains the bar tuples from
    a queue object.
    """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def calculate_signals(self, event):
        """
        Provides the mechanisms to calculate the list of signals.
        """
        raise NotImplementedError("Missing implementation for calculate_signals()")


# In[ ]:



