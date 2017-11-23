# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 16:51:19 2017

@author: Jesus
"""

import sys
sys.path.insert(0, 'isda_daycounters/')
import thirty360, actual360
import numpy as np
from simple_bond import Bond, ZCBond


class SimpleDerivative(object):
    """
    Representation of a simple derivative product such as Caplet or Floor
    
    """
    
    
    def __init__(self, payment_dates, payment_steps, reset_dates, reset_steps):
        """
        Initialize a SimpleDerivative object
        
        Parameters
        ----------
            payment_dates : array_like of shape (1, ) with datetime payment 
                dates
            payment_steps : array_like of shape (1, ) with integer payment 
                steps that corresponds to the tree
            exercise_dates : array_like of shape (1, ) with datetime exercise 
                dates
            exercise_steps : array_like of shape (1, ) with integer exercise 
                steps that corresponds to the tree

        """
        self._payment_date = payment_dates
        self._payment_step = payment_steps
        self._reset_date = reset_dates
        self._reset_step = reset_steps
        self._steps = reset_steps[len(reset_steps) - 1]
        self._the_tree = {}
        
#    def discounted_expected_value(self)
        
    def get_price(self, hw_tree, payoff):
        """
        This function computes the derivative price
        
        Parameters
        ----------
            hw_tree: a HWTree class instance
            bond: a Bond class instance
            payoff: a PayOff class instance
        
        Return
        ------
            out: float scalar that specifies the derivative price
        
        """
        # Build the HW tree and construct the underlying tree
        
        bond = ZCBond(self._payment_date, self._payment_step)
        bond.get_price(hw_tree)
        
        # construct the derivative tree
        for i in reversed(range(self._steps + 1)):
            for j in range(-i, i + 1):
                # if this is the first exercise node, then set the 
                # derivative payoff
                if i == self._steps:
                    price = bond._bond_tree[i, j]
                    tau = actual360.year_fraction(self._reset_date[0], self._payment_date[0])
                    self._the_tree[i, j] = payoff(price, tau)
                    continue
                
                # else, compute the discounted expected value (continuation value)
                else:
                    continuation_value = 0
                    for k in range(j - 2, j + 3):
                        if k <= i + 1 and k >= -i - 1:
                            continuation_value += hw_tree.prob(j, k)*self._the_tree[i + 1, k]
                        else:
                            continue
                    continuation_value *= hw_tree._discount_factor_tree[i, j]
                    

                    self._the_tree[i, j] = continuation_value

        return self._the_tree[0, 0]


class SimpleSwaption(object):
    """
    Representation of a simple swaption product such as European or Bermudan 
    Swaption
    
    """
    
    
    def __init__(self, payment_dates, payment_steps, exercise_dates, exercise_steps, frequency=2):
        """
        Initialize a SimpleSwaption object
        
        Parameters
        ----------
            payment_dates : array_like of shape (M, ) with datetime payment 
                dates
            payment_steps : array_like of shape (M, ) with integer payment 
                steps that corresponds to the tree
            exercise_dates : array_like of shape (M, ) with datetime exercise 
                dates
            exercise_steps : array_like of shape (M, ) with integer exercise 
                steps that corresponds to the tree

        """
        self._payment_dates = payment_dates
        self._payment_steps = payment_steps
        self._exercise_dates = exercise_dates
        self._exercise_steps = exercise_steps
        self._steps = exercise_steps[len(exercise_steps) - 1]        
        self._frequency = frequency
        self._the_tree = {}
        
    def get_price(self, hw_tree, payoff):
        """
        This function computes the derivative price
        
        Parameters
        ----------
            hw_tree: a HWTree class instance
            bond: a Bond class instance
            payoff: a PayOff class instance
        
        Return
        ------
            out: float scalar that specifies the derivative price
        
        """
        # Build the HW tree and construct the underlying tree
        
        coupon_rates = np.ones_like(self._payment_steps)*payoff._strike
        bond = Bond(self._payment_dates, self._payment_steps, coupon_rates, self._frequency)
        bond.get_price(hw_tree)
        
        # construct the derivative tree
        for i in reversed(range(self._steps + 1)):
            for j in range(-i, i + 1):
                # if this is the first exercise node, then set the 
                # derivative payoff
                if i == self._steps:
                    index = bond._payment_steps.tolist().index(i)
                    price = bond._bond_tree[i, j] - bond._coupon_rates[index]/bond._frequency
                    self._the_tree[i, j] = payoff(price)
                    continue
                
                # else, compute the discounted expected value (continuation value)
                else:
                    continuation_value = 0
                    for k in range(j - 2, j + 3):
                        if k <= i + 1 and k >= -i - 1:
                            continuation_value += hw_tree.prob(j, k)*self._the_tree[i + 1, k]
                        else:
                            continue
                    continuation_value *= hw_tree._discount_factor_tree[i, j]
                    
                    # if this is an exercise node
                    if i in self._exercise_steps.tolist():
                        # and payment node, then subtract the 
                        # coupon payment from the bond price at that node
                        if i in self._payment_steps.tolist():    
                            index = bond._payment_steps.tolist().index(i)
                            price = bond._bond_tree[i, j] - bond._coupon_rates[index]/bond._frequency
                        else:
                            price = bond._bond_tree[i, j]
                        
                        # set the node value comparing the continuation value with 
                        # call value
                        call_value = payoff(price)
                        self._the_tree[i, j] = max(continuation_value, call_value)
                    else:
                        # else this is the discounted continuation value
                        self._the_tree[i, j] = continuation_value

        return self._the_tree[0, 0]
    

class CallableBond(object):
    """
    Representation of a Callable Bond
    
    """
    
    def __init__(self, payment_dates, payment_steps, exercise_dates, exercise_steps, coupon_rates, frequency=2):
        """
        Initialize a SimpleDerivative object
        
        Parameters
        ----------
            payment_dates : array_like of shape (M, ) with datetime payment 
                dates
            payment_steps : array_like of shape (M, ) with integer payment 
                steps that corresponds to the tree
            exercise_dates : array_like of shape (M, ) with datetime exercise 
                dates
            exercise_steps : array_like of shape (M, ) with integer exercise 
                steps that corresponds to the tree

        """
        self._payment_dates = payment_dates
        self._payment_steps = payment_steps
        self._exercise_dates = exercise_dates
        self._exercise_steps = exercise_steps
        self._steps = exercise_steps[len(exercise_steps) - 1]
        self._coupon_rates = coupon_rates
        self._frequency = frequency
        self._the_tree = {}
        
    def get_price(self, hw_tree):
        """
        This function computes callable bond price
        """
        # Build the HW tree and construct the underlying tree
        
        bond = Bond(self._payment_dates, self._payment_steps, self._coupon_rates, self._frequency)
        bond.get_price(hw_tree)
        
        # construct the tree
        face_value = 1.0
        
        for i in reversed(range(self._steps + 2)):
            for j in range(-i, i + 1):
                if i == self._steps + 1:              
                    self._the_tree[i, j] = bond._bond_tree[i, j]
                    continue
                else:
                    discounted_expected_value = 0
                    for k in range(j - 2, j + 3):
                        if k <= i + 1 and k >= -i - 1:
                            discounted_expected_value += hw_tree.prob(j, k)*self._the_tree[i + 1, k]
                        else:
                            continue
                            
                    discounted_expected_value *= hw_tree._discount_factor_tree[i, j]
                    
                    # if this is an exercise node
                    if i in self._exercise_steps.tolist():
                        # and a payment node, compute the continuation value
                        # adding the coupon payment to the discounted value
                        # the call value is the face value plus coupon payment
                        if i in self._payment_steps.tolist():
                            index = bond._payment_steps.tolist().index(i)
                            coupon_rate = bond._coupon_rates[index]
                            continuation_value = discounted_expected_value + coupon_rate/bond._frequency
                            call_value = face_value + coupon_rate/bond._frequency
                            self._the_tree[i, j] = min(continuation_value, call_value)
                    
                    # else, continuation value is the discounted expected
                        # value and the call value is the face value plus accrued
                        # interest
                        else:
                            e_index = self._exercise_steps.tolist().index(i)
                            accrued_interest = coupon_rate*thirty360.year_fraction(self._payment_dates[index - 1], self._exercise_dates[e_index])
                            continuation_value = discounted_expected_value
                            call_value = face_value + accrued_interest
                            self._the_tree[i, j] = min(continuation_value, call_value)
                    
                    # else, 
                    else:
                        # if this is a payment node, set the node value as the
                        # discounted expected value plus coupon payment
                        if i in self._payment_steps.tolist():
                            index = bond._payment_steps.tolist().index(i)
                            coupon_rate = bond._coupon_rates[index]
                            self._the_tree[i, j] = discounted_expected_value + coupon_rate/bond._frequency
                        
                        # else, set the node value as the discounted expected value
                        else:
                            self._the_tree[i, j] = discounted_expected_value
                
        return self._the_tree[0, 0]