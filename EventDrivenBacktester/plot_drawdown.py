
# coding: utf-8

# In[1]:

# plot_drawdown


# In[2]:

import matplotlib.pyplot as plt
import numpy as np


# In[3]:

def create_data_matrix(csv_ref, col_index):
    data = np.zeros((3,3))
    for i in range(0,3):
        for j in range(0,3):
            data[i][j] = float(csv_ref[i*3+j][col_index])
    return data


# In[4]:

# Recall, we are slicing everything at w_l=100 in order to visualize the data in two dimensions
# Looks like these two plot_* files can be condensed by passing appropriate data parameters...
if __name__ == "__main__":
    # Open the CSV file and obtain only the lines with a lookback value of 100
    csv_file = open("", "r").readlines()
    csv_ref = [c.strip().split(",") for c in csv_file if c[:3] == "100"]
    data = create_data_matrix(csv_ref, 6)
    
    fig, ax = plt.subplots()
    heatmap = ax.pcolor(data, cmap=plt.cm.Reds)
    row_labels = [0.5, 1.0, 1.5]
    column_labels = [2.0, 3.0, 4.0]
    
    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            # Tags in the boxes
            plt.text(x + 0.5, y + 0.5, '%.2f' % dat[y,x], horizontalalignment='center', verticalalignment='center',)
    
    plt.colorbar(heatmap)
            
    ax.set_xticks(np.arange(data.shape[0])+0.5, minor=False)
    ax.set_yticks(np.arange(data.shape[1])+0.5, minor=False)
    ax.set_xticklabels(row_labels, minor=False)
    ax.set_yticklabels(column_labels, minor=False)
    
    plt.suptitle('Maximum Drawdown Heatmap', fontsize=18)
    plt.xlabel('Z-Score Exit Threshold', fontsize=14)
    plt.ylabel('Z-Score Entry Threshold', fontsize=14)
    
    plt.show()


# In[ ]:



