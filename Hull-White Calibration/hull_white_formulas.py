# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 09:54:09 2017

@author: Jesus
"""

import numpy as np
from scipy.stats import norm

def B(t, T, a):
    return 1/a*(1 - np.exp(-a*(T - t)))
 
def ZBP(P_T0, P_T1, T0, T1, K, a, sigma):
    # B is in lecture 5 page 26
    sigma_p = sigma*np.sqrt((1-np.exp(-2*a*T0))/(2*a))*B(T0, T1, a)
 
    d1 = np.log(P_T1/(K*P_T0))/sigma_p + (sigma_p/2)
    d2 = d1 - sigma_p
    return K*P_T0*norm.cdf(-d2)-P_T1*norm.cdf(-d1)
 
def hw_caplet(T0, T1, N, K, P_T0, P_T1, a, sigma):
    tau = T1-T0
    return N*(1+K*tau)*ZBP(P_T0, P_T1, T0, T1, 1/(1+K*tau), a, sigma)
 
 
def hw_cap(T0, T1, N, K, P_T0, P_T1, a, sigma):
    caplet = np.zeros(len(T0))
    for i in range(len(T0)):
        caplet[i] = hw_caplet(T0[i], T1[i], N, K, P_T0[i], P_T1[i], a, sigma)
    return sum(caplet)


