# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 23:50:05 2017

@author: Jesus
"""


import pandas as pd
import datetime
from cap_vol_strip import CapVolStrip

# read data from spreadsheets (annual and quarterly (keep in mind the column 
# names and formats presented in this test are required to avoid any crash)
cap_data = pd.read_excel('test_data.xlsx',sheetname='cap_data')
forward_data = pd.read_excel('test_data.xlsx',sheetname='forward_data')

print(cap_data)
print(forward_data)

# define valuation date
today = datetime.datetime(2017,8,18)
print(today)

# instantiate the CapVolStrip object passing cap_data and forward_data
vol_stripper = CapVolStrip(cap_data, forward_data)

# convert dates to years for maturity and reset dates inside our class
vol_stripper.add_dates2years(today)
print(vol_stripper._maturities)

# interpolate the annual cap vol.
# (here I'm using linear interpolation you can use other methods availables, 
# such as cubic spline interpolation or extrapolation)
vol_stripper.interpolate_cap_vol()
print(vol_stripper._interpolated_cap_vols)

# compute cap cash prices
vol_stripper.compute_cap_prices()
print(vol_stripper._cap_prices)

# strip the cap volatilities
vol_stripper.strip_cap_vol()
print(vol_stripper._caplet_vols)

