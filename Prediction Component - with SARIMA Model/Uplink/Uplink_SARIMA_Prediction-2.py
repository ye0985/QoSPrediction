#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from pylab import rcParams
import statsmodels.api as sm
import warnings
import itertools
from statsmodels.tsa.ar_model import AR
from statsmodels.tsa.arima_model import ARIMA


# In[2]:


#Import data
DATAPATH = '/Users/sim-yeji/Library/Containers/com.microsoft.Excel/Data/Downloads/influxdata_2023-03-06T19_08_56Z_1.csv'
data = pd.read_csv(DATAPATH,comment="#")


# In[3]:


data = data[data['_value'] != -32768]
data = data[data['frequency'] != -9999]
data = data[data['lat'] != -9999]
data = data[data['lon'] != -9999]
data = data[data['uplink'] != -1]
data = data[data['downlink'] != -1]
data = data[data['latency'] != -1]
data = data[data['cellId'] != -9999]


# In[4]:


# Create Dataframe & Clean Data
data = data.loc[:,['_time','uplink']]
data['_time'] = pd.to_datetime(data['_time'])
data = data.sort_values(by='_time')
data.set_index('_time',inplace=True)
data


# In[5]:


#Show data as figure
plt.figure(figsize=(20,8))
plt.plot(data.uplink)
plt.xlabel("Date")
plt.ylabel("Uplink")
plt.show()


# In[7]:


#Split data
train1 = data.loc['2023-03-03 17:30:00+00:00':'2023-03-03 18:10:00+00:00']
test1 = data.loc['2023-03-03 18:10:00+00:00':'2023-03-03 18:32:30+00:00']


# In[8]:


#Find p,q,d parameter
from pmdarima import auto_arima
stepwise_model = auto_arima(train1, start_p=1, start_q=1,
                           max_p=3, max_q=3, m=12,
                           start_P=0, seasonal=True,
                           d=1, D=1, trace=True,
                           error_action='ignore',  
                           suppress_warnings=True, 
                           stepwise=True)


# In[9]:


#Fit SARIMA Model
SARIMA1 = sm.tsa.statespace.SARIMAX(data, order=(2,1,1), seasonal_order=(2,1,1,12) ,enforce_stationarity=False,enforce_invertibility=False)

SARIMA_results = SARIMA1.fit()

SARIMA_results.plot_diagnostics(figsize=(16, 8))
plt.show()


# In[10]:


#Predict, compare predicted datas with test-data
start_index = '2023-03-03 18:10:00+00:00'
end_index = '2023-03-03 18:32:30+00:00'

SARIMA_predict = SARIMA_results.predict(start=start_index, end=end_index)

plt.figure(figsize=(20,10))
plt.plot(data.uplink, label = 'Original')
plt.plot(SARIMA_predict, label = 'Predicted')
plt.xlabel("Date")
plt.ylabel("Uplink")
plt.legend()
plt.show()


# In[11]:


# Prediction: forecast steps after the last value
forecast = SARIMA_results.forecast(steps=test1.shape[0])
print(forecast) 


# In[12]:


#Measure performance of different algorithms (MAE, MSE, RMSE, R2, MAPE)
from sklearn import metrics

def mae(y_true, y_pred):
    return metrics.mean_absolute_error(y_true,y_pred) #MAE
def mse(y_true, y_pred):
    return metrics.mean_squared_error(y_true,y_pred) # MSE
def rmse(y_true, y_pred):    
    return np.sqrt(metrics.mean_squared_error(y_true,y_pred))  # RMSE
def r2(y_true, y_pred):    
    return metrics.r2_score(y_true,y_pred) # R2
def mape(y_true, y_pred):
    return np.mean(np.abs((y_pred - y_true) / y_true)) * 100 # MAPE

def get_score( y_true, y_pred):
    
    mae_val = mae(y_true, y_pred)
    mse_val = mse(y_true, y_pred)
    rmse_val = rmse(y_true, y_pred)
    r2_val = r2(y_true, y_pred)
    mape_val = mape(y_true, y_pred)
    
    score_dict = {
                  "mae" :  mae_val,
                  "mse" :  mse_val,
                  "rmse" : rmse_val,
                  "r2":    r2_val, 
                  "mape" : mape_val
                 }
    return score_dict


get_score(np.array(test1), np.array(forecast) )


# In[13]:


#Check Residuals
residuals = pd.DataFrame(SARIMA_results.resid)
residuals.plot(title = "residuals")


# In[ ]:




