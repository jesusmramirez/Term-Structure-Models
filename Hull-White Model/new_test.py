# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 18:57:18 2017

@author: Jesus
"""

import pandas as pd
from simple_hull_white import HWTree
from simple_payoff import PayerSwaption, CapletPayoff, FloorletPayoff
from simple_bond import ZCBond, Bond
from simple_derivatives import SimpleDerivative, SimpleSwaption, CallableBond

############################### HULL-WHITE TREE ###############################

# load a term structure for the Hull-White tree calibration
term_structure = pd.read_excel('sample_data.xlsx',sheetname='hw_data_monthly')
term_structure.head()
term_structure.tail()

# set parameters and instantiate a Hull-White tree
a = 0.00000001
sigma = 0.00517541046919369
maturity = 5.0
steps = 60
zcb_prices = term_structure['ZCB']
zcb_maturities = term_structure['Maturity']

hw = HWTree(zcb_prices, zcb_maturities, maturity, steps, a, sigma)


#################### ZERO COUPON BONDS (with ZCBond class) ####################

# load bond payment dates
bond_dates = pd.read_excel('sample_data.xlsx', sheetname='zero_bond_dates')
bond_dates.tail()

# set parameters and instantiate a Bond  
payment_dates = bond_dates['Payment Date']
payment_steps = bond_dates['Payment Step']

zero_coupon_bond = ZCBond(payment_dates, payment_steps)

# get the Bond price
print('Zero Coupon Bond price: {:1.8f}'.format(zero_coupon_bond.get_price(hw)))


##################### ZERO COUPON BONDS (with Bond class) #####################

# load bond payment dates
bond_dates = pd.read_excel('sample_data.xlsx', sheetname='zero_bond_dates')
bond_dates.tail()

# set parameters and instantiate a Bond  
payment_dates = bond_dates['Payment Date']
payment_steps = bond_dates['Payment Step']
coupon_rates = bond_dates['Coupon']

bond = Bond(payment_dates, payment_steps, coupon_rates)

# get the Bond price
print('Bond price: {:1.8f}'.format(bond.get_price(hw)))


################################ COUPON BONDS #################################

# load bond payment dates
bond_dates = pd.read_excel('sample_data.xlsx', sheetname='bond_dates')
bond_dates.tail()

# set parameters and instantiate a Bond  
payment_dates = bond_dates['Payment Date']
payment_steps = bond_dates['Payment Step']
coupon_rates = bond_dates['Coupon']

bond = Bond(payment_dates, payment_steps, coupon_rates, frequency=2)

# get the Bond price
print('Bond price: {:1.8f}'.format(bond.get_price(hw)))


################################### CAPLETS ###################################

# load caplet payment dates
caplet_dates = pd.read_excel('sample_data.xlsx', sheetname='caplet_dates')
caplet_dates.tail()

# set parameters and instantiate a Caplet  
payment_dates = pd.to_datetime(caplet_dates['Payment Date'])
payment_steps = caplet_dates['Payment Step']
reset_dates = pd.to_datetime(caplet_dates['Reset Date'])
reset_steps = caplet_dates['Reset Step']


simple_derivative = SimpleDerivative(payment_dates, payment_steps, reset_dates, 
                            reset_steps)

# get the Caplet and Floorlet price
strike = 0.00955952490457184

payoff = CapletPayoff(strike)
print('Caplet  : {:1.8f}'.format(simple_derivative.get_price(hw, payoff)))
payoff = FloorletPayoff(strike)
print('Floorlet: {:1.8f}'.format(simple_derivative.get_price(hw, payoff)))


############################## EUROPEAN SWAPTIONS #############################

# load Swaption payment and exercise dates
european_exercise_dates = pd.read_excel('sample_data.xlsx', 
                                        sheetname='european_exercise_dates')
european_payment_dates = pd.read_excel('sample_data.xlsx', 
                                       sheetname='payment_dates')

# set parameters and instatiate a Swaption
exercise_dates = european_exercise_dates['Exercise Date']
exercise_steps = european_exercise_dates['Exercise Step']
payment_dates = european_payment_dates['Payment Date']
payment_steps = european_payment_dates['Payment Step']

swaption = SimpleSwaption(payment_dates, payment_steps, exercise_dates, 
                            exercise_steps, frequency=4)

# get the European Swaption price
strike = 0.013122450511296
payoff = PayerSwaption(strike)
print('European Swaption price: {:1.8f}'.format(swaption.get_price(hw, payoff)))


############################## BERMUDAN SWAPTIONS #############################

# load Swaption payment and exercise dates
bermudan_exercise_dates = pd.read_excel('sample_data.xlsx', 
                                        sheetname='bermudan_exercise_dates')
bermudan_payment_dates = pd.read_excel('sample_data.xlsx', 
                                       sheetname='payment_dates')

# set parameters and instatiate a Swaption
exercise_dates = bermudan_exercise_dates['Exercise Date']
exercise_steps = bermudan_exercise_dates['Exercise Step']
payment_dates = bermudan_payment_dates['Payment Date']
payment_steps = bermudan_payment_dates['Payment Step']

swaption = SimpleSwaption(payment_dates, payment_steps, exercise_dates, 
                            exercise_steps, frequency=4)

# get the European Swaption price
strike = 0.013122450511296
payoff = PayerSwaption(strike)
print('Bermudan Swaption price: {:1.8f}'.format(swaption.get_price(hw, payoff)))


############################### CALLABLE BONDS ################################

# load callable bond payment and exercise dates
callable_exercise_dates = pd.read_excel('sample_data.xlsx',
                                        sheetname='callable_exercise_dates')
callable_payment_dates = pd.read_excel('sample_data.xlsx', 
                                       sheetname='callable_payment_dates')


# set parameters and instatiate a Callable Bond
exercise_dates = pd.to_datetime(callable_exercise_dates['Exercise Date'])
exercise_steps = callable_exercise_dates['Exercise Step']
payment_dates = pd.to_datetime(callable_payment_dates['Payment Date'])
payment_steps = callable_payment_dates['Payment Step']
coupon_rates = callable_payment_dates['Coupon']

callable_bond = CallableBond(payment_dates, payment_steps, exercise_dates, 
                             exercise_steps, coupon_rates, frequency=2)

# get the Callable Bond price

print('Callable Bond price: {:1.8f}'.format(callable_bond.get_price(hw)))

############################### CALLABLE BONDS ################################

# load callable bond payment and exercise dates
callable_exercise_dates = pd.read_excel('sample_data.xlsx',
                                        sheetname='callable_exercise_dates')
callable_payment_dates = pd.read_excel('sample_data.xlsx', 
                                       sheetname='payment_dates')


# set parameters and instatiate a Callable Bond
exercise_dates = pd.to_datetime(callable_exercise_dates['Exercise Date'])
exercise_steps = callable_exercise_dates['Exercise Step']
payment_dates = pd.to_datetime(callable_payment_dates['Payment Date'])
payment_steps = callable_payment_dates['Payment Step']
coupon_rates = callable_payment_dates['Coupon']

callable_bond = CallableBond(payment_dates, payment_steps, exercise_dates, 
                             exercise_steps, coupon_rates, frequency=4)

# get the Callable Bond price

print('Callable Bond price: {:1.8f}'.format(callable_bond.get_price(hw)))