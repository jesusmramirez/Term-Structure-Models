# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 16:43:32 2017

@author: Jesus
"""
import numpy as np

class HWTree(object):
    """
    Representation of a Hull-White Tree
    
    """
    
    
    def __init__(self, zcb_prices, zcb_maturities, maturity, steps, a, sigma):
        """
        Initialize a Hull- White Tree object
        
        Parameters
        ----------
            zcb_prices : array_like of shape (M, )
                specifies the ZCB prices
            zcb_maturities: array_like of shape (M, )
                specifies the ZCB corresponding maturities
            maturity : longest maturity in the term structure (a positive float)
            steps : number of steps in the three (an positive integer)
            a : Hull-White parameter (a positive float)
            sigma : Hull-White parameter (a positive float)
            
        """
        self._zcb_prices = zcb_prices
        self._zcb_maturities = zcb_maturities
        self._time = maturity
        self._steps = steps
        
        # Tree parameters
        self._a = a
        self._sigma = sigma
        self._jmax = None
        self._dt = None
        self._dR_star = None
        
        # Trees
        self._shor_rate_tree = {}
        self._state_price_tree = {}
        self._discount_factor_tree = {}
                
        # Probabilities
        self._hw_prob = {}        
        
        # Boolean
        self._is_built = False
        
    def update_parameters(self):
        """
        Helper function that updated internal parameters
        """
        self._jmax = np.ceil(0.184 / (self._a*self._time/self._steps)).astype(int)
        self._dt = self._time/self._steps
        self._dR_star = np.sqrt(3*self._sigma**2*self._time/self._steps)
        
    def hw_prob(self):
        """
        Compute the up, middle and down probabilities for all the states
        """
        self.update_parameters()
        
        a2 = self._a**2
        dt2 = self._dt**2
        for j in range(-self._steps - 1, self._steps + 2): # I added one more state
            j2 = j**2
            if j > -self._jmax and j < self._jmax:                
                self._hw_prob[1, j] = 1/6 + 0.5*(a2*j2*dt2 - self._a*j*self._dt)
                self._hw_prob[0, j] = 2/3 - a2*j2*dt2
                self._hw_prob[-1, j] = 1/6 + 0.5*(a2*j2*dt2 + self._a*j*self._dt)                
            elif j <= -self._jmax:
                self._hw_prob[1, j] = 1/6 + 0.5*(a2*j2*dt2 + self._a*j*self._dt)
                self._hw_prob[0, j] = -1/3 - a2*j2*dt2 - 2*self._a*j*self._dt
                self._hw_prob[-1, j] = 7/6 + 0.5*(a2*j2*dt2 + 3*self._a*j*self._dt)
            else:
                self._hw_prob[1, j] = 7/6 + 0.5*(a2*j2*dt2 - 3*self._a*j*self._dt)
                self._hw_prob[0, j] = -1/3 - a2*j2*dt2 + 2*self._a*j*self._dt
                self._hw_prob[-1, j] = 1/6 + 0.5*(a2*j2*dt2 - self._a*j*self._dt)
    
    def prob(self, k, j):
        """
        Helper function that computes the probabilities of going from state k 
        to state j in consecutive time steps
        """
        if k > -self._jmax and k < self._jmax:
            if j - k == -2 or j - k == 2:
                return 0
            else:
                return self._hw_prob[j - k, k]
        elif k <= -self._jmax:
            if j - k < 0:
                return 0
            else:
                return self._hw_prob[j - k - 1, k]
        else:
            if j - k > 0:
                return 0
            else:
                return self._hw_prob[j - k + 1, k]

    def calibrate(self):
        """
        Builds a tree for the short rate, the discount factors and the Arrow-
        Debreu prices
        """
        self._is_built = True
        
        # Initialize the array of alphas
        alphas = np.zeros(shape=self._steps)
        alphas[0] = -np.log(self._zcb_prices[1])/self._dt
        
        # Initialize the Arrow-Debreu tree
        self._state_price_tree[0, 0] = 1
        
        # Initialize the short rate tree
        self._shor_rate_tree[0, 0] = alphas[0]
        
        # Initialize the discount factor tree
        self._discount_factor_tree[0, 0] = np.exp(-alphas[0]*self._dt)
        
        # Build discount factors array for R*
        discount_factors = {}
        
        for j in range(-self._steps, self._steps + 1):
            discount_factors[j] = np.exp(-j*self._dR_star*self._dt)
        
        # Calibrate the trees
        for i in range(1, self._steps):
            
            # Update the Arrow-Debreu tree
            for j in range(-i, i + 1):
                value = 0
                for k in range(j - 2, j + 3):                    
                    if k < i and k > -i:
                        value += self._state_price_tree[i - 1, k]*self.prob(k, j)*self._discount_factor_tree[i - 1, k]                        
                    else:
                        continue
                    
                self._state_price_tree[(i, j)] = value
            
            # Update the array of alphas
            for j in range(-i, i + 1):
                alphas[i] += self._state_price_tree[i, j]*discount_factors[j]
            
            alphas[i] = np.log(alphas[i]/self._zcb_prices[i + 1])/self._dt
            
            # Update the short rate and discount factor trees
            for j in range(-i, i + 1):  
                self._shor_rate_tree[i, j] = alphas[i] + j*self._dR_star
                self._discount_factor_tree[i, j] = np.exp(-self._shor_rate_tree[i, j]*self._dt)
        return alphas