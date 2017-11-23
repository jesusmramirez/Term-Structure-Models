# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 09:52:02 2017

@author: Jesus
"""

class CapletPayoff(object):
    def __init__(self, strike):
        self._strike = strike
        
    def __call__(self, price, tau):
        return price*tau*max(1/tau*(1/price - 1) - self._strike, 0)

class FloorletPayoff(object):
    def __init__(self, strike):
        self._strike = strike
        
    def __call__(self, price, tau):
        return price*tau*max(self._strike - 1/tau*(1/price - 1), 0)

class PayerSwaption(object):
    def __init__(self, strike):
        self._strike = strike
    
    def __call__(self, price):
        return max(1.0 - price, 0)
    
class ReceiverSwaption(object):
    def __init__(self, strike):
        self._strike = strike
    
    def __call__(self, price):
        return max(price - 1.0, 0)
    
