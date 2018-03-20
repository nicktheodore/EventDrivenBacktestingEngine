
# coding: utf-8

# In[3]:

from __future__ import print_function

import datetime
import pandas_datareader.data as web

if __name__ == "__main__":
    spy = web.DataReader("SPY", "yahoo", datetime.datetime(2007,1,1), datetime.datetime(2015,6,15))
    print(spy.tail())


# In[ ]:



