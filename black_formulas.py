# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 22:59:27 2017

@author: Jesus
"""

import numpy as np
from scipy.stats import norm

def black_caplet(discount, forward, strike, caplet_vol, reset, maturity, 
                 notional = 1000000):
    """
    Computes caplet price using Black's formula
    
    Parameters
    ----------
        discount: scalar, ZCB price that matures at payment date
        forward: scalar, forward rate
        strike: scalar
        caplet_vol: scalar, caplet volatility
        reset: scalar, reset date in years
        maturity: scalar, maturity date in years
        notional: scalar, default value is 1,000,000.00
        
    Return
    ------
        out: scalar, caplet price
    
    """
    tau = maturity - reset
    d1 = (np.log(forward/strike) + 0.5*caplet_vol**2*reset)/(caplet_vol*np.sqrt(reset))
    d2 = d1 - caplet_vol*np.sqrt(reset)
    return (forward*norm.cdf(d1) - strike*norm.cdf(d2))*discount*tau*notional


def black_cap_price(discounts, forwards, strike, cap_vol, resets, maturities, 
                    notional=1000000):
    """
    Computes caplet price using Black's formula
    
    Parameters
    ----------
        discounts: array_like of shape(M, ), ZCB prices that matures at payment 
            dates. M corresponds to the number of caplets that comprise the cap
        forwards: array_like of shape(M, ), forward rates
        strike: scalar, if it is at-the-money then it is the swap rate
        caplet_vol: scalar, cap flat volatility
        resets: array_like of shape(M, ), reset dates in years
        maturities: array_like of shape(M, ), maturity dates in years
        notional: scalar, default value is 1,000,000.00
        
    Return
    ------
        out: scalar, caplet price
    
    """
    num_caplets = len(forwards)
    caplets = np.zeros(num_caplets)
    for i in range(num_caplets):
        caplets[i] = black_caplet(discounts[i], forwards[i], strike, cap_vol, 
               resets[i], maturities[i], notional)
        
    return sum(caplets)