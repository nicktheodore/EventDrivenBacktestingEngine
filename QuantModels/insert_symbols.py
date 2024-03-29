
# coding: utf-8

# In[1]:

#!/usr/bin/python


# insert_symbols.py


# In[2]:

from __future__ import print_function
from math import ceil

import datetime
import bs4
import MySQLdb as mdb
import requests


# In[6]:

def obtain_parse_wiki_sp500():
    """
    Downloas and parse the Wikipedia list of S&P500 constitutents using requests and BeautifulSoup.
    
    Returns a list of tuples to add to MySQL.
    """
    
    # Stores the surrent time, for the created_at record
    now = datetime.datetime.utcnow()
    
    # Use requests and BeautifulSoup to download the list of S&P500 companies and obtain the symbol table
    response = requests.get("http://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    soup = bs4.BeautifulSoup(response.text)
    
    # This selects the first table, using CSS Selector syntax and then ignores the header row ([1:])
    symbolslist = soup.select('table')[0].select('tr')[1:]
    
    # Obtain the symbol information for each row in the S&P500 constituent table
    symbols = []
    for i, symbol in enumerate(symbolslist):
        tds = symbol.select('td')
        symbols.append(
            (
                tds[0].select('a')[0].text, # Ticker
                'stock',
                tds[1].select('a')[0].text, # Name
                tds[3].text,                # Sector
                'USD', now, now
            )
        )
    return symbols


# In[13]:

def insert_sp500_symbols(symbols):
    """
    Insert the S&P500 symbols into the MySQL database
    """
    
    # Connect to the MySQL instance
    db_host = 'localhost'
    db_user = 'ntheodore' # Input appropriate username
    db_pass = 'nick3636' # Input appropriate password
    db_name = 'securities_master'
    conn = mdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)
    
    # Create the insert strings
    column_str = """ticker, instrument, name, sector, currency, created_date, last_updated_date"""
    insert_str = ("%s, " * 7)[:-2]
    final_str  = "INSERT INTO symbol (%s) VALUES (%s)" % (column_str, insert_str)
    
    # Using the MySQL connection, carry out an INSERT INTO for every symbol
    with conn:
        cur = conn.cursor()
        cur.executemany(final_str, symbols)


# In[14]:

if __name__ == "__main__":
    symbols = obtain_parse_wiki_sp500()
    insert_sp500_symbols(symbols)
    print("%s symbols were successfully added." % len(symbols))


# In[ ]:



