# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 09:58:11 2017

@author: Jesus
"""

import numpy as np
from scipy.optimize import minimize
from hull_white_formulas import hw_cap


class HWModel(object):
    def __init__(self, cap_data, caplet_data):
        # cap data
        self._black_prices = cap_data['Cap']
        self._strikes = cap_data['Strike']
        # caplet data
        self._resets = caplet_data['Reset']
        self._maturities = caplet_data['Maturity']
        self._discounts_reset = caplet_data['ZCB at reset']
        self._discounts_maturity = caplet_data['ZCB at maturity']
        # calibrated parameters
        self._a = None
        self._sigma = None
        
    def calibration(self, initial, notional=1.0, method='SLSQP', display=False):
        """
        """
        EPSILON = 1.e-8
        
        resets = [] 
        maturities = []
        strikes = self._strikes
        discounts_reset = []
        discounts_maturity = []
        
        num_caps = len(self._black_prices)
        
        for j in range(num_caps):
            resets.append(self._resets[:3 + j*4])
            maturities.append(self._maturities[:3 + j*4])
            discounts_reset.append(self._discounts_reset[:3 + j*4])
            discounts_maturity.append(self._discounts_maturity[:3 + j*4])
        
        def func(param):
            hw_prices = np.zeros(num_caps)
            for i in range(num_caps):

                hw_prices[i] = hw_cap(resets[i], maturities[i], notional, strikes[i], 
                         discounts_reset[i], discounts_maturity[i], param[0], param[1])
                
            return sum(np.square((self._black_prices - hw_prices)/self._black_prices))
    
        # setting up constraints as dictionary
        cons = ({'type': 'ineq',
               'fun': lambda x: x[0] - EPSILON})
        
        if method=='SLSQP':
            # Sequential Least SQuares Programming (SLSQP)
            return minimize(func, initial, constraints=cons, method='SLSQP', options={'disp': True})
        else:
            print('Please, introduce a valid method')
            return None