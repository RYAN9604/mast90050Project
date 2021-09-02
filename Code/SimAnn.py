#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 11:04:48 2021

@author: hess
"""
################################################################
# Quick example of simulated annealing code
#
# I wanted to show you an example of how easy it is to code
# the acceptance/rejection part of simulated annealing
#
# The "costs" of new candidate solutions are simulated randomly
# 
################################################################

import numpy
import math

sol = 10 # initial solution
T = 20 # temperature
while T>0:
    cand = numpy.random.randint(21)
    if cand<sol:
        sol = cand
        print("New solution:", sol)
    else:
        #Acception/rejection step
        A = math.exp(-(cand-sol)/T) # Acceptance probability
        U = numpy.random.uniform(0,1)
        if U<A:
            sol = cand
            print("New solution:", sol)
    T -=1

    
    