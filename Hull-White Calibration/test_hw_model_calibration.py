# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 16:30:43 2017

@author: Jesus
"""

import pandas as pd
from HWCalibration import HWModel

cap_data = pd.read_excel('data_test.xlsx',sheetname='cap_data')
caplet_data = pd.read_excel('data_test.xlsx',sheetname='caplet_data')

model = HWModel(cap_data, caplet_data)

initial = [0.001,0.05]
model.calibration(initial)