"""
==========================
Multinomial HMM of stock data
==========================

This script shows how to use Multinomial HMM.
It uses stock price data, which can be obtained from yahoo finance.
For more information on how to get stock prices with matplotlib, please refer
to date_demo1.py of matplotlib.

"""

from __future__ import print_function

import datetime
import numpy as np
import pylab as pl
from matplotlib.finance import quotes_historical_yahoo
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from hmmlearn.hmm import MultinomialHMM

print(__doc__)

###############################################################################
# Downloading the data
date1 = datetime.date(1995, 1, 1)  # start date
date2 = datetime.date(2012, 1, 6)  # end date
# get quotes from yahoo finance
quotes = quotes_historical_yahoo("INTC", date1, date2)
if len(quotes) == 0:
    raise SystemExit

# unpack quotes. this is where the relevant data is grabbed from the 
# much larger "quotes" object
dates = np.array([q[0] for q in quotes], dtype=int)
close_v = np.array([q[2] for q in quotes])
volume = np.array([q[5] for q in quotes])[1:]

'''
quotes[0]=
 
(728296.0,					<-- Date
 2.8940862745098035,		
 2.8999999999999999,		<-- Close Volume (close_V)
 2.9122823529411761,
 2.8658823529411763,
 41721600.0)				<-- Volume
'''
# take diff of close value
# this makes len(diff) = len(close_v) - 1
# therefore, others quantity also need to be shifted
diff = close_v[1:] - close_v[:-1]
dates = dates[1:]
close_v = close_v[1:]

# pack diff and volume for training
X = np.column_stack([diff, volume])
print(X.shape)

###############################################################################
# Run Gaussian HMM
print("fitting to HMM and decoding ...", end='')
n_components = 5

# make an HMM instance and execute fit
model = MultinomialHMM(n_components, n_iter=1000)

model.fit([X])

# predict the optimal sequence of internal hidden state
hidden_states = model.predict(X)
