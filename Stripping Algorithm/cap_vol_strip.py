# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 22:57:39 2017

@author: Jesus
"""

from black_formulas import black_cap_price, black_caplet
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import bisect

NUM_DAYS = 360

class CapVolStrip(object):
    """
    This class hold annual and quarterly data for caps and caplets, respectively.
    Its main purpose if carry out the stripping algorithm to strip caplet volati-
    lities from flat cap volatilities.
    To get those volatilities, there are some intermediates steps, such as inter-
    polation of annual cap flat volatilities and computation of cap cash prices
    using Black formulas. Caplet and Cap Black formulas are imported from the mo-
    dule black_formulas.
    """
    def __init__(self, cap_data, data):
        # cap data, annual data
        self._cap_vols = cap_data['Cap Vol']
        self._cap_maturity_dates = cap_data['Maturity Date']
        self._cap_maturities =  None
        
        # caplet data, quarterly (assuming each cap is comprised by quarterly
        # caples)
        self._maturity_dates = data['Maturity Date']
        self._reset_dates = data['Reset Date']
        self._discounts = data['ZCB']
        self._forwards = data['Forward']
        self._strikes = data['Strike']
        self._interpolated_cap_vols = None
        self._maturities =  None
        self._resets =  None
        self._cap_prices =  None
        self._caplet_vols = None
        
        self._num_obs = len(data)

    def _days2year(self, data):
        """
        Helper function
        Convert an array_like of days to years
        
        Parameters
        ----------
            data: array_like of shape(M, )

        Return
        ------
            out: array_like of shape(M, )
        
        """
        return np.array([data[i].days/NUM_DAYS for i in range(len(data))])

    def _date2year(self, data, today):
        """
        Helper function
        Convert an array_like of string dates to years
        
        Parameters
        ----------
            data: array_like of shape(M, )

        Return
        ------
            out: array_like of shape(M, )
        
        """
        data = pd.to_datetime(data) - today
        return self._days2year(data)
    
    def add_dates2years(self, today):
        """
        Convert reset and maturity date array to years
        
        Parameters
        ----------
            today: datetime.datetime
                it could be the trading date or settlement date

        Return
        ------
            out: array_like of shape(M, )
        
        """
        self._resets = self._date2year(self._reset_dates, today)
        self._maturities = self._date2year(self._maturity_dates, today)
        self._cap_maturities = self._date2year(self._cap_maturity_dates, today)
    
    def interpolate_cap_vol(self, kind='linear', extrapolate=False):
        """
        Interpolate cap flat volatilities
        
        Parameters
        ----------            
            kind: str or int, optional
                specifies the kind of interpolation as a string (‘linear’, 
                ‘nearest’, ‘zero’, ‘slinear’, ‘quadratic’, 'cubic')
            extrapolate: boolean
                if False, it will repeat the first cap volatility for periods < 1yr
                 
        Return
        ------
            out: array_like of shape(M, )
                interpolated cap volatilities
        
        """
        if extrapolate:
            fill_value='extrapolate'
        else:
            fill_value=self._cap_vols[0]
            
        x = self._cap_maturities
        y = self._cap_vols
        new_x = self._maturities
        
        # call interp1d scipy function that does the interpolation
        f = interp1d(x, y, kind=kind, bounds_error=False, fill_value=fill_value)
        self._interpolated_cap_vols = f(new_x)
        
        return self._interpolated_cap_vols
    
    def compute_cap_prices(self, notional=1000000):
        """
        Helper function
        
        Parameters
        ----------
            data:  array_like of shape(M, )

        Return
        ------
            out: array_like of shape(M, )
        
        """
        n = self._num_obs
        cap_prices = np.zeros(n)
        
        # compute all the cap prices one by one
        for i in range(n):
            # set all the arguments that Black's formula requires to compute cap
            # price
            discounts = self._discounts[:i + 1]        
            forwards = self._forwards[:i + 1]
            strike = self._strikes[i]        
            cap_vol = self._interpolated_cap_vols[i]
            resets = self._resets[:i + 1]
            maturities = self._maturities[:i + 1]
            
            # compute the cap price
            cap_prices[i] = black_cap_price(discounts, forwards, strike, cap_vol, resets, maturities, notional)
        
        self._cap_prices = cap_prices
        return cap_prices
    
    def strip_cap_vol(self):
        """
        Compute caplet volatilities
        Parameters
        ----------
            None

        Return
        ------
            out: array_like of shape(M, )
                caplet volatilities
        
        """
        num_stripped_vol = self._num_obs
        self._caplet_vols = self._interpolated_cap_vols.copy()
        # stripping algorith
        for i in range(1, num_stripped_vol):
            # bisection method procedure 
            # define a function that depends on new volatility that bisection will find
            def func(new_vol):
                result = self._cap_prices[i]
                for j in range(i + 1):
                    discount = self._discounts[j]
                    forward = self._forwards[j]
                    strike = self._strikes[i]
                    caplet_vol = self._caplet_vols[j]
                    reset = self._resets[j]                
                    maturity = self._maturities[j]
                    notional = 1000000.0
                    
                    if j < i:
                        result -= black_caplet(discount, forward, strike, caplet_vol, reset, maturity, notional)
                    else:
                        result -= black_caplet(discount, forward, strike, new_vol, reset, maturity, notional)
                        
                return result
            
            # use bisection method to compute the caplet volatility that match the cap price.
            a = 1.e-8
            b = 2.0
            self._caplet_vols[i] = bisect(func, a, b)
        return self._caplet_vols
    