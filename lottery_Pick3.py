#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 16:54:42 2021

@author: scott
"""
# IMPORTS

from itertools import product
import statistics
import matplotlib.pyplot as plt

# FUNCTIONS

# creates all possible combinations of sum-it-up numbers for two games in a row
def dd_sum_it_up(topNum):
    sums = [i for i in range(topNum+1)]
    doubleDrawSums = tuple(product(sums,repeat=2))
    return doubleDrawSums

# MAIN CODE BODY

ddOptions = dd_sum_it_up(27) # see function above 
# print(f'All sum orders for two games: \n{ddOptions}')

# intitialze game prizes and odds
sumPrizeDict = {0:500,1:168,2:84,3:50,4:34,5:24,6:18,7:14,8:12,9:10,
                10:8,11:8,12:6,13:6,14:6,15:6,16:8,17:8,18:10,19:12,
                20:14,21:18,22:24,23:34,24:50,25:84,26:168,27:500}

sumOddsDict = {0:1000,1:333,2:167,3:100,4:67,5:48,6:36,7:28,8:22,9:18,
                10:16,11:14,12:14,13:13,14:13,15:14,16:14,17:16,18:18,19:22,
                20:28,21:36,22:48,23:67,24:100,25:167,26:333,27:1000}

# Return on investment loop

ddroi = [] # intitalize list for loop below
# takes all game possiblities and assigns the ROI based on the value of each sum-it-up prize and odds
for dd in ddOptions:
    prizeReturn = []
    for s_i_u in dd:
        prizeReturn.append(sumPrizeDict[s_i_u]/sumOddsDict[s_i_u])
    ddroi.append(round(sum(prizeReturn),2))    
ddroiMean = statistics.mean(ddroi)
# print(f'All ROIs avaiable: \n{ddroi}')

# Return on investment probability loop

posROI = 0 # initialize variable for loop below
neutROI = 0 # initialize variable for loop below
negROI = 0 # initialize variable for loop below
# counts each ROI to be positive, neutral, or negative
for roi in ddroi:
    if roi > 1.0:
        posROI += 1
    if roi == 1.0:
        neutROI += 1
    if roi < 1.0:
        negROI += 1

# console displays
print(f'Average return is: {round(ddroiMean,2)*100}%')
print('Positive return probability:', round(posROI/len(ddroi),2))
print('Neutral return probability:', round(neutROI/len(ddroi),2))
print('Negative return probability:', round(negROI/len(ddroi),2))

# Plotting    

pos = [] # intitialize y for loop below
keys = {} # intitalize x for loop below
# creates a data set to be used on a plot
for roi in ddroi:
    if roi not in keys:
        keys[roi] = 1
        pos.append(1)
    else:
        keys[roi]+=1
        pos.append(keys[roi])

x = ddroi
y = pos
xMean = [ddroiMean]*len(y) # create mean line to be vertical
fig,ax = plt.subplots() # setup the figure with one subplot
data_line = ax.plot(x,y, label='Frequency',linestyle="None", marker='o') # stacked frequency points
mean_line = ax.plot(xMean,y, label='Mean') # average line as second curve
legend = ax.legend(loc='upper right') # legend location on figure
plt.show() # display plot
        