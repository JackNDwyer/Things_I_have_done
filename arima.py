import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from matplotlib.pylab import rcParams
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima_model import ARIMA
import statsmodels.api as sm

from dateutil.relativedelta import relativedelta

ts = pd.read_csv('~/Desktop/ts_data.csv')

#df['dates']
#df['values']
order_arima = [0,1,2,3]
seasonal_diff = [0,1,2]
ma_param = [0,1,2,3]
months_forecast = 6
ts = ts.dropna()
ts['sales'] = ts['sales'].astype('float64')
ts = ts.set_index(['Month'])
ts_log = np.log(ts)
ts_log.index = pd.to_datetime(ts_log.index, format = '%m/%d/%y', errors= 'coerce')
#ts_log_diff = ts_log - ts_log.shift()
#ts_log_diff['sales'][0] = 0
aic = 10000
for ar in order_arima:
	for ma in ma_param:
		for i in seasonal_diff:
			try:
				model=sm.tsa.ARIMA(endog=ts['sales'],order=(ar,i,ma))
				score = model.fit().aic
				#model = SARIMAX(ts['sales'], order=(ar, i, ma))
				if score < aic:
					aic = score
					order = ar
					diff = i
					mov_av = ma
			except:
				continue

#model = ARIMA(ts['sales'], exog = ts['extra'], order = (order, diff, mov_av), missing = 'drop')

model = ARIMA(ts['sales'], order = (order, diff, mov_av), missing = 'drop')
results_ARIMA = model.fit()

predictions_value = 
