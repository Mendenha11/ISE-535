#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 10:22:40 2021

@author: scott
"""

# IMPORTS

import pandas as pd
from itertools import combinations
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# FUNCTIONS

# creates combinations of a number set for matching 5, 4, 3, or 2
def combination_maker(ticket):
    ticketCombos = set()
    for i in [5,4,3,2]:
        combos = combinations(ticket,i)
        for combo in combos:
            combo = tuple(sorted(combo))
            ticketCombos.add(combo)
    return ticketCombos

# creates a desired number of randomly generated tickets according to avaible numbers in the game
def tickets_maker(count):
    tickets = []
    for i in range(count):    
        ticket = tuple(sorted(random.sample(range(1,36),5)))
        tickets.append(ticket)
    return tickets

# compares combinations of each ticket to the winning number combinations
def ticket_checker(winningCombinations, tickets):
    winningNumberOfBalls = []
    for ticket in tickets:
        ticketCombinations = combination_maker(ticket)
        
        ballsCorrect = set()
        for combo in ticketCombinations:
            if combo in winningCombinations:
                ballsCorrect.add(len(combo))
            else:
                ballsCorrect.add(0)
        winningNumberOfBalls.append(max(ballsCorrect))
    return winningNumberOfBalls

# MAIN CODE BODY

# Opening the file

df = pd.read_csv('./Fantasy5_Analysis.csv') # read in the csv file from the working directory path

# Winning ticket matching loop

df['My Cost'] = 0 # initialize a column to be altered in loop below
df['My Winners'] = 0 # initialize a column to be altered in loop below
myTicketCount = 376992 # initialize my total tickets for the experiment
match2 = 0 # initialize '2-of-5' matches, which is euqivalent to free tickets to the next day
for i in range(0,len(df),4):
    print(f'Starting row {i} of {len(df)} in steps of 4 at a time') # update while running
    winningNumber = tuple([df['First'][i], df['Second'][i], df['Third'][i], df['Fourth'][i], df['Fifth'][i]]) # combines each number from the row and column to be the winning number
    winningCombos = combination_maker(winningNumber) # see function above
    
    # Number of tickets purchased each Rolldown
    
    myCost = (myTicketCount - match2) * 1 # calculate daily cost by reducing out previous day free tickets
    df['My Cost'][i:i+4] = myCost
    match2 = 0 # resets '2-of-5' matches
    match3 = 0 # initializes and resets '3-of-5' matches
    match4 = 0 # initializes and resets '4-of-5' matches
    match5 = 0 # intitalizes and resets '5-of-5' matches
    myTickets = tickets_maker(myTicketCount) # see function above
    matched = ticket_checker(winningCombos, myTickets) # see function above    
    for match in matched:
        if match == 2:
            match2 +=1 # counts '2-of-5' matches
        elif match == 3:
            match3 +=1 # counts '3-of-5' matches
        elif match == 4:
            match4 +=1 # counts '4-of-5' matches
        elif match == 5:
            match5 +=1 # counts '5-of-5' matches
    df['My Winners'][i] = match5
    df['My Winners'][i+1] = match4
    df['My Winners'][i+2] = match3
    df['My Winners'][i+3] = match2
    print(f'Counted winning tickets for row {i}') 
df['Experiment Winners'] = df['Winners'] + df['My Winners'] # calculate the total winners from the original data and my tickets

# Prize level creation loop

df['Experiment Prize Amount'] = 0 # initialize a column to be altered in loop below
for i in range(0,len(df),4):
    df['Experiment Prize Amount'][i] = np.where(df['Experiment Winners'][i] == 0, # check for full experiment having no winners to be a rolldown
                                                0, # $0 in prizes for top category in rolldown
                                                200000/df['Experiment Winners'][i]) # aproximately correct on the average of a normal distribution
    df['Experiment Prize Amount'][i+1] = np.where(df['Experiment Winners'][i] == 0, # check for full experiment having no winners to be a rolldown
                                                  555, # rules specify maximum of $555 prizes which is constant from data for rolldowns
                                                  np.where(df['Winners'][i] > 0, # if day was already not a rolldown
                                                           df['Prize Amount'][i+1]+ ((df['My Cost'][i+1] * df['Ratio Prize Amount'][i+1]) / df['Experiment Winners'][i+1]) , # use same measured ratio with addition of my costs buying more tickets
                                                           (0.075 * (df['Estimated Ticket Sales'][i+1] + df['My Cost'][i+1])) / df['Experiment Winners'][i+1])) # if day was a rolldown and 'My Winners' changed it to not a rolldown. Used average ratio amount for this level.
    df['Experiment Prize Amount'][i+2] = np.where(df['Experiment Winners'][i] == 0, # check for full experiment having no winners to be a rolldown
                                                  df['Prize Amount'][i+2]+  (((df['My Cost'][i+2]  * 0.665) - (df['My Winners'][i+3] + (555 * df['My Winners'][i+1]))) / df['My Winners'][i+2]), # use same measured ratio with addition of my costs buying more tickets
                                                  np.where(df['Winners'][i] > 0,# if day was already not a rolldown
                                                           df['Prize Amount'][i+2]+ ((df['My Cost'][i+2] * df['Ratio Prize Amount'][i+2]) / df['Experiment Winners'][i+2]), # if day was a rolldown and 'My Winners' changed it to not a rolldown. Used average ratio amount for this level.
                                                           (0.20 * (df['Estimated Ticket Sales'][i+2] + df['My Cost'][i+2])) / df['Experiment Winners'][i+2]))
    # value of $1 per free ticket is constant but already reduced from next day's cost so 0 will remain

# Data analysis

dfExperiment = df.filter(['Date', 'Prize Level', 'Winners', 'My Winners', 'Prize Amount', 'Experiment Prize Amount', 'My Cost' ], axis=1) # new df with experiment simulation results
dfExperiment['My Prize'] = dfExperiment['My Winners'] * dfExperiment['Experiment Prize Amount'] # the prize amount per prize level

dfDateReturn = dfExperiment.groupby(['Date','My Cost']).agg({'My Prize':sum}).reset_index() # new df to quickly sum the daily prize money 'My Prize'
dfDateReturn['My Return'] = dfDateReturn['My Prize'] - dfDateReturn['My Cost'] # daily cash flow
dfDateReturn.at[0, 'My Cumulative Return'] = dfDateReturn.at[0,'My Return'] # initializes the first day for the loop below
for i in range(1,len(dfDateReturn)): # populates the column with the return of the day plus days prior
    dfDateReturn['My Cumulative Return'][i] = dfDateReturn['My Return'][i]+ dfDateReturn['My Cumulative Return'][i-1]
dfDateReturn['My ROI %'] = (dfDateReturn['My Return'] / dfDateReturn['My Cost']) * 100 # daily percent return 
dfDateReturn.loc['Total'] = dfDateReturn[['My Cost', 'My Prize', 'My Return', 'My Cumulative Return']].sum() # total each column in the date range
dfDateReturn.at['Total', 'My ROI %'] = (dfDateReturn.at['Total', 'My Return'] / dfDateReturn.at['Total', 'My Cost']) * 100 # total percent return over entire date range
dataTypes = {'Date':'datetime64', 'My Cost': int, 'My Return': int, 'My Cumulative Return': int } # dictionary of desired data types
dfDateReturn = dfDateReturn.astype(dataTypes) # change column data types to selection

# print(dfDateReturn)

# Saving data to csv file

fileName = 'Fantasy5_Experiment.csv' # intialize the new file name
dfExperiment.to_csv(fileName, index = False) # creates a csv file of selected data
print(f'\nCSV file {fileName} created') # confirmation of the file creation

fileName = 'Fantasy5_Return.csv' # intialize the new file name
dfDateReturn.to_csv(fileName, index = True) # creates a csv file of selected data with Total row
print(f'\nCSV file {fileName} created') # confirmation of the file creation


# Plotting

months = mdates.MonthLocator()  # Every month
fmt = mdates.DateFormatter('%b') # Specify the format - %m gives us 01, 02
fig, ax1 = plt.subplots() # setup the figure with one subplot
fig.suptitle('Fantasy5 Experiment') # title the figure

ax1.plot(dfDateReturn['Date'],dfDateReturn['My Cost'],lw=1, marker='o', ms=2,label = 'Cost') # first curve
ax1.plot(dfDateReturn['Date'],dfDateReturn['My Return'],lw=1, marker='o', ms=2,label = 'Return') # second curve
ax1.plot(dfDateReturn['Date'],dfDateReturn['My Cumulative Return'],lw=1, marker='o', ms=2,label = 'Cumulative') # third curve
ax1.legend(loc="lower left") # legend location on figure

# making the month markers the only x axis display
X = plt.gca().xaxis
X.set_major_locator(months)
X.set_major_formatter(fmt)

plt.show() # display plot

