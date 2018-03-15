
# coding: utf-8

# In[1]:

#!/usr/bin/python


#price_retrieval.py


# In[1]:

from __future__ import print_function

import datetime
import warnings

import MySQLdb as mdb
import requests


# In[12]:

# Obtain a database connection to the MySQL instance
db_host = 'localhost'
db_user = 'ntheodore' # Replace with appropriate username
db_pass = 'nick3636' # Replace with appropriate password
db_name = 'securities_master'
conn = mdb.connect(db_host, db_user, db_pass, db_name)


# In[17]:

def obtain_list_of_db_tickers():
    """
    Obtains a list of the ticker symbols in the database
    """
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id, ticker FROM symbol")
        data = cur.fetchall()
        return [(d[0], d[1]) for d in data]


# In[31]:

def get_daily_historical_data_yahoo(ticker, start_date=(2000,1,1), end_date=datetime.date.today().timetuple()[0:3]):
    """
    Obtains data from Yahoo Finance and returns a list of tuples
    
    Parameters
    -----------
    ticker: Yahoo Finance ticker symbol, e.g. "GOOG" for Google, Inc.
    start_date: Start date in (YYYY, M, D) format
    end_date: End date in (YYYY, M, D) format
    """
    # Construct the Yahoo URL with the correct integer query parameters for start and end dates.
    # Note: Some parameters are zero-based!
    ticker_tuple = (
        ticker, 
        start_date[1]-1, start_date[2], start_date[0],
        end_date[1]-1, end_date[2], end_date[0]
    )
    
    yahoo_url = "http://ichart.finance.yahoo.com/table.csv"
    yahoo_url += "?s=%s&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s"
    yahoo_url = yahoo_url % ticker_tuple
    
    # Try connecting to Yahoo Finance and obtaining the data
    # On failure, print and error message
    prices = []

    try:
        yf_data = requests.get(yahoo_url).text.split("\n")[1:-1]
        for y in yf_data:
            p = y.strip().split(",")
            prices.append(
                (datetime.datetime.strptime(p[0], '%Y-%m-%d'),
                p[1], p[2], p[3], p[4], p[5], p[6]
            ))
    except Exception as e:
        print("Could not download the Yahoo data: %s" % e)
    return prices


# In[32]:

def insert_daily_data_into_db(data_vendor_id, symbol_id, daily_data):
    """
    Takes a list of tuples of daily data and adds it to the MySQL database.
    Appends a vendor ID and symbol ID to the data.
    
    daily_data: List of tuples of the OHLC data (with adj_close and volume)
    """
    # Create the time now
    now = datetime.datetime.utcnow()
    
    # Amend the data to include the vendor ID and symbol ID
    daily_data = [(data_vendor_id, symbol_id, d[0], now, now, d[1], d[2], d[3], d[4], d[5], d[6]) for d in daily_data]
    
    # Create the inser strings
    column_str = """data_vendor_id, symbol_id, price_date, created_date,
                    last_updated_date, open_price, high_price, low_price,
                    close_price, volume, adj_close_price"""
    insert_str = ("%s, " * 11)[:-2]
    final_str = "INSERT INTO daily_price (%s) VALUES (%s)" % (column_str, insert_str)
    
    # Using the MySQL connection, carry out and INSERT INTO for every symbol
    with conn:
        cur = conn.cursor()
        cur.executemany(final_str, daily_data)


# In[33]:

if __name__ == "__main__":
    # This ignore the warning regarding Data Truncation from the Yahoo precision to Decimal(19,4) datatypes
    warnings.filterwarnings("ignore")
    
    # Loop over the tickers and insert the daily historical data into the database
    tickers = obtain_list_of_db_tickers()
    lentickers = len(tickers)
    for i, t in enumerate(tickers):
        print(
            "adding data for %s: %s out of %s" % (t[1], i+1, lentickers)
            )
        yf_data = get_daily_historical_data_yahoo(t[1])
        insert_daily_data_into_db('1', t[0], yf_data)
    print("Successfully added Yahoo Finance pricing data to DB")


# In[ ]:



