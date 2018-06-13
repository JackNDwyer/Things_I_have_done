import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.pylab import rcParams
from statsmodels.tsa.statespace.sarimax import SARIMAX, SARIMAXResults
from statsmodels.tsa.arima_model import ARIMA
import statsmodels.api as sm

from dateutil.relativedelta import relativedelta

ts = pd.read_csv('~/Downloads/rbff.csv')

#df['dates']
#df['values']

#set up orders that will be iterated through
order_arima = [0,1,2,3]
seasonal_diff = [0,1,2]
ma_param = [0,1,2,3]
s_ar = [0,1,2,3]
s_s_d = [0,1,2]
s_ma = [0,1,2]
months_forecast = 12
ts = ts.dropna()

#statsmodels like floats, so we make it floats. It also like dt index
ts['Amount'] = ts['Amount'].astype('float64')
ts = ts.set_index(['Date'])
ts.index = pd.to_datetime(ts.index, format = '%m/%d/%y', errors= 'coerce')

#base aic score that will be starting point for model
aic = 10000

#if we have a data frame with many different sets of data, we could iterate through it.
#comment the next 5 lines (and fix indents) if you don't have a bunch of different dfs
vals = ts.Objective.unique()
diction = {}
for val in vals:
	diction[val] = ts[ts['Objective'] == val].copy()
for key,ts in diction.iteritems():
	for ar in order_arima:
		for ma in ma_param:
			for i in seasonal_diff:
	#
	 			try:
                    #we are finding the best score AR,I, and MA terms here
					model=sm.tsa.ARIMA(endog=ts['Amount'],order=(ar,i,ma))
			# 							model = SARIMAX(ts.sales.values, order=(ar, i, ma), seasonal_order = (0,0,0,0))
			# 							score = SARIMAXResults(model).aic()
					score = model.fit(disp=0).aic
					if score < aic:
						aic = score
						order = ar
						diff = i
						mov_av = ma
			# 			seasonal_ar = sar
	# 					seasonsal_diff = s_i
	# 					seasonal_ma = sma
	 			except:
	 				continue

#this is being finicky with my data, but this is roughly the correct implementation of an SARAIMAX
#model using the statsmodels package
	mod = sm.tsa.statespace.SARIMAX(ts.Amount.values, order=(order,diff,mov_av), seasonsal_diff = (1,1,1,12), enforce_stationarity=False, enforce_invertibility = False)
	res = mod.fit(disp = 0)
	forecasts = res.forecast(12)
	print forecasts
