
# coding: utf-8

# In[1]:

#!/usr/bin/python


# retrieving_data.py


# In[4]:

from __future__ import print_function

import pandas as pd
import MySQLdb as mdb

if __name__ == "__main__":
    # Connect to the MySQL instance
    db_host = 'localhost'
    db_user = 'username' # Input appropriate username
    db_pass = 'password' # Input appropriate password
    db_name = 'securities_master'
    conn = mdb.connect(db_host, db_user, db_pass, db_name)

    # Select all of the historic Google adjusted close data
    sql = """SELECT dp.price_date, dp.adj_close_price
             FROM symbol AS sym
             INNER JOIN daily_price AS dp
             ON dp.symbol_id = sym.id
             WHERE sym.ticker = 'GOOG'
             ORDER BY dp.price_date ASC;"""

    # Create a pandas dataframe from the SQL query
    goog = pd.read_sql_query(sql, con=conn, index_col='price_date')

    # Output the dataframe tail
    print(goog.tail())


# In[ ]:
