
# coding: utf-8

# # Augmented Dickey-Fuller (ADF) Test
# 
# The ADF test takes advantage of the fact that if the price series is mean-reverting, then the next price level will be proportional to the current price level. Mathematically, the ADF test is based on the idea of testing for the presence of a **unit root** in an **autoregressive** time series sample. Recall: <br/><br/>
# _Autoregressive: Future values are based on a weighted sum of previous values_<br/>
# _Unit Root: Indicates whether a time-series variable is non-stationary_<br/><br/>
# We consider a time-series model known as a _linear lag model of order p_. This states that the change in value of a time-series is proportional to a constant, the time, the previous _p_ values, and an error term:
# \begin{align}
# ∆y_t & = \alpha + \beta t+\gamma y_{t-1} + \delta_1∆y_{t-1} + ... + \delta_{p-1} ∆y_{t-p+1} + \epsilon_t \\
# \end{align}
# <br/>
# Where alpha: constant;  beta: coefficient of temporal trend;  *∆y_t: y(t) - y(t-1)*.
# 
# The ADF test is testing for the _null hypothesis_ (H<sub>o</sub>) that gamma = 0, which would indicate (with alpha = beta = 0) that the process is a random walk and thus not mean-reverting.
# 
# ADF test procedure: <br/>
# 1. Calculate the _test statistic, DF<sub>τ</sub>_ , which is used to reject/fail to reject H<sub>o</sub>
# 2. Use the _distribution_ of the test statistic, as well as critical values, in order to decide on H<sub>o</sub>
# 
# Test Statistic: 
# \begin{align}
# DF_{\tau} = \frac{\hat{\gamma}}{SE(\hat{\gamma})}
# \end{align}
# 
# Where gamma is the sample proportionality constant divided by it's _standard error_
# 
# The test statistic can now be calculated. Since we are using a lag model, we must use a value for _p_. For research purposes, _p_ = 1 is usually sufficient.

# In[1]:

# augmented-dickey-fuller.py


# In[8]:

from __future__ import print_function

# Import the Time Series library
import statsmodels.tsa.stattools  as ts

# Import Datetime and the Pandas Datareader
from datetime import datetime
import pandas_datareader.data as web


# In[14]:

# Download the Amazon OHLCV data from 1/1/2000 to 1/1/2015
amzn = web.DataReader("AMZN", "yahoo", datetime(2000,1,1), datetime(2015,1,1))

# Output the results of the Augmented Dickey-Fuller test for Amazon with a lag order value of 1
adf_test_results = ts.adfuller(amzn['Adj Close'], 1)


# 0: The calculated test statistic <br/>
# 1: The _p-value_ <br/>
# 2: _p_ <br/>
# 3: Number of data points in the sample <br/>
# 4: Dictionary: Contains the critical values of the test-statistic at 1, 5, and 10 percent significance levels. <br/>
# 5: The maximized information criterion if autolag is not None. <br/> <br/>

# In[18]:

print("Test Statistic: %s \n" % str(adf_test_results[0]))
for level, value in adf_test_results[4].items():
    if adf_test_results[0] < value:
        print("Reject the Null Hypothesis")
    else:
        print("Fail to reject the Null Hypothesis")
    print("Significance Level: %s, Critical Value: %f \n" % (level, value))


# **Since the value of the test statistic is larger than any of the critical values at the 1, 5, and 10 percent significance levels, we fail to reject the null hypothesis that gamma = 0. Thus, by the Augmented Dickey-Fuller test, this is unlikely to be mean-reverting time-series.**
