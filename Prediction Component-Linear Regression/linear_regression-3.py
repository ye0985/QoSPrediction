#!/usr/bin/env python
# coding: utf-8

# In[50]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from pylab import rcParams
import statsmodels.api as sm
import warnings
import itertools
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

#Import data
DATAPATH = '/Users/sim-yeji/Library/Mobile Documents/com~apple~CloudDocs/Downloads/NewGPS2T.csv'

data = pd.read_csv(DATAPATH,comment="#")

X = data[['lon', 'lat', 'cellId', 'switch']] # Predictor variables
y_lat = data['latency'] # Target variable - latency
y_ul = data['uplink'] # Target variable - uplink
y_dl = data['downlink'] # Target variable - downlink


# In[51]:


# Split the data into train and test sets

X_train, X_test, y_lat_train, y_lat_test, y_ul_train, y_ul_test, y_dl_train, y_dl_test = train_test_split(X, y_lat, y_ul, y_dl, test_size=0.2, random_state=42)


# In[52]:


# Fit a linear regression model to predict latency
lr_lat = LinearRegression()
lr_lat.fit(X_train, y_lat_train)
preds_lat = lr_lat.predict(X_test)

print('Predicted Latency:', preds_lat)


# In[53]:


import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

plt.scatter(y_lat_test, preds_lat, alpha=0.4)
plt.xlabel("Actual latency")
plt.ylabel("Predicted latency")
plt.title("LINEAR REGRESSION")
plt.show()


# In[54]:


# Fit a linear regression model to predict uplink
lr_ul = LinearRegression()
lr_ul.fit(X_train, y_ul_train)

# Make predictions on the test set
preds_ul = lr_ul.predict(X_test)

print('Predicted Uplink:', preds_ul)


# In[55]:


plt.scatter(y_ul_test, preds_ul, alpha=0.4)
plt.xlabel("Actual uplink")
plt.ylabel("Predicted uplink")
plt.title("LINEAR REGRESSION")
plt.show()


# In[56]:


# Fit a linear regression model to predict downlink
lr_dl = LinearRegression()
lr_dl.fit(X_train, y_dl_train)

# Make predictions on the test set 
preds_dl = lr_dl.predict(X_test)

print('Predicted Downlink:', preds_dl)


# In[57]:


#Check how fit the predicted datas look like actual datas
plt.scatter(y_dl_test, preds_dl, alpha=0.4)
plt.xlabel("Actual downlink")
plt.ylabel("Predicted downlink")
plt.title("LINEAR REGRESSION")
plt.show()


# In[58]:


# Load and prepare new data
new_data = pd.read_csv('/Users/sim-yeji/Library/Mobile Documents/com~apple~CloudDocs/Downloads/Sample.csv')
X_new = new_data[['lon', 'lat', 'cellId', 'switch']] # Predictor variables


# In[59]:


## Once we have trained regression model using the historical data, 
## we can use it to make predictions on new data, 
## which includes longitude, latitude, celled, and switch values but does not include the latency, uplink, and downlink values.

# Make predictions on the new data to predict latency
new_preds_lat = lr_lat.predict(X_new)

# Make predictions on the new data to predict uplink
new_preds_ul = lr_ul.predict(X_new)

# Make predictions on the new data to predict downlink
new_preds_dl = lr_dl.predict(X_new)

print('Predicted Latency:', new_preds_lat)
print('Predicted Uplink:', new_preds_ul)
print('Predicted Downlink:', new_preds_dl)


# In[60]:


#prediction dataframe
split_index = int(len(data) * 0.8)
test = data.iloc[split_index:]

d = pd.DataFrame({
    'lon' : test.lon,
    'lat' : test.lat,
    'predicted Latency': preds_lat,
    'predicted Uplink': preds_ul,
    'predicted Downlink': preds_dl
    
})
d


# In[61]:


d.to_csv('LinearRegression.csv',index = False)


# In[62]:


#new-prediction dataframe
d2 = pd.DataFrame({
    'lon' : new_data.lon,
    'lat' : new_data.lat,
    'new predicted Latency': new_preds_lat,
    'new predicted Uplink': new_preds_ul,
    'new predicted Downlink': new_preds_dl
    
})
d2


# In[ ]:




