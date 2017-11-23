# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 16:49:06 2017

@author: Jesus
"""

class ZCBond(object):
    """
    Representation of a Zero Coupon Bond
    """    
    
    def __init__(self, payment_dates, payment_steps):
        """
        Initialize a Zero Coupon Bond object
        
        Parameters
        ----------
            payment_dates : array_like of shape (1, ) with datetime payment 
                dates
            payment_steps : array_like of shape (1, ) with integer payment 
                steps that corresponds to the tree
            coupon_rates : scalar or array_like of shape (1, ) with the coupon 
                rates
            frequency : integer scalar that specifies the number of payment for
                each year, default value is 2

        """
        self._payment_dates = payment_dates
        self._payment_steps = payment_steps
        self._maturity = payment_dates[len(payment_dates) - 1]
        self._steps = payment_steps[len(payment_steps) - 1]
        self._bond_tree = {}
    
    def build_hw_tree(self, hw_tree):
        """
        Helper function that builds and calibrate a Hull-White tree
        
        Parameters
        ----------
            hw_tree: a HWTree class instance
            
        """
        if not hw_tree._is_built:
            hw_tree.hw_prob()
            hw_tree.calibrate()
    
    def get_price(self, hw_tree):
        """
        This function computes the bond price
        
        Parameters
        ----------
            hw_tree: an HWTree class instance
        
        Return
        ------
            out: float scalar that specifies the bond price
        
        """
        # Build the HW tree
        self.build_hw_tree(hw_tree)

        # construct the bond tree
        for i in reversed(range(self._steps + 1)):
            for j in range(-i, i + 1):
                # if this is the final node, then set the bond final payoff
                if i == self._steps:
                    self._bond_tree[i, j] = 1
                    continue
                # else, compute the discounted expected value
                else:
                    discounted_expected_value = 0
                    for k in range(j - 2, j + 3):
                        if k <= i + 1 and k >= -i - 1:
                            discounted_expected_value += hw_tree.prob(j, k)*self._bond_tree[i + 1, k]
                        else:
                            continue
                    discounted_expected_value *= hw_tree._discount_factor_tree[i, j]
                    
                    # set the node value as the disccounted expected value
                    self._bond_tree[i, j] = discounted_expected_value

        return self._bond_tree[0, 0]


class Bond(object):
    """
    Representation of a Bond
    """    
    
    def __init__(self, payment_dates, payment_steps, coupon_rates, frequency=2):
        """
        Initialize a Bond object
        
        Parameters
        ----------
            payment_dates : array_like of shape (M, ) with datetime payment 
                dates
            payment_steps : array_like of shape (M, ) with integer payment 
                steps that corresponds to the tree
            coupon_rates : scalar or array_like of shape (M, ) with the coupon 
                rates
            frequency : integer scalar that specifies the number of payment for
                each year, default value is 2

        """
        self._payment_dates = payment_dates
        self._payment_steps = payment_steps
        self._maturity = payment_dates[len(payment_dates) - 1]
        self._steps = payment_steps[len(payment_steps) - 1]
        self._coupon_rates = coupon_rates
        self._frequency = frequency
        self._bond_tree = {}
    
    def build_hw_tree(self, hw_tree):
        """
        Helper function that builds and calibrate a Hull-White tree
        
        Parameters
        ----------
            hw_tree: a HWTree class instance
            
        """
        if not hw_tree._is_built:
            hw_tree.hw_prob()
            hw_tree.calibrate()
    
    def get_price(self, hw_tree):
        """
        This function computes the bond price
        
        Parameters
        ----------
            hw_tree: an HWTree class instance
        
        Return
        ------
            out: float scalar that specifies the bond price
        
        """
        # Build the HW tree
        self.build_hw_tree(hw_tree)

        # construct the bond tree
        for i in reversed(range(self._steps + 1)):
            for j in range(-i, i + 1):
                # if this is the final node, then set the bond final payoff
                if i == self._steps:
                    index = self._payment_steps.tolist().index(i)
                    self._bond_tree[i, j] = 1 + self._coupon_rates[index]/self._frequency
                    continue
                # else, compute the discounted expected value
                else:
                    discounted_expected_value = 0
                    for k in range(j - 2, j + 3):
                        if k <= i + 1 and k >= -i - 1:
                            discounted_expected_value += hw_tree.prob(j, k)*self._bond_tree[i + 1, k]
                        else:
                            continue
                    discounted_expected_value *= hw_tree._discount_factor_tree[i, j]
                
                    # if this is a payment node, then add the coupon payment to 
                    # the discounted expected value and set this value as the node
                    # value
                    if i in self._payment_steps.tolist():
                        index = self._payment_steps.tolist().index(i)
                        self._bond_tree[i, j] = discounted_expected_value + self._coupon_rates[index]/self._frequency
                    # else, set the discounted expected value as the node value
                    else:
                        self._bond_tree[i, j] = discounted_expected_value

        return self._bond_tree[0, 0]