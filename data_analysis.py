#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 10:43:15 2021

@author: scott
"""

# IMPORTS
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# MAIN CODE BODY

# Gathered information from Fantasy5 lottery
percentDollar = 0.665 # percent of every dollar in prize pool according to https://www.flalottery.com/education

# Opening the file

df = pd.read_csv('./Fantasy5_Data.csv') # read in the csv file from the working directory path

# Data analysis

# intialize the distingushing information for each prize level to be used as an index
row_indexes_5 = df[df['Prize Level']== '5-of-5'].index 
row_indexes_4 = df[df['Prize Level']== '4-of-5'].index
row_indexes_3 = df[df['Prize Level']== '3-of-5'].index 
row_indexes_2 = df[df['Prize Level']== '2-of-5'].index  
#  assign a new value to the 'Odds' column based on criteria above
df.loc[row_indexes_5,'Odds']= 1/376992  
df.loc[row_indexes_4,'Odds']= 1/2432.21
df.loc[row_indexes_3,'Odds']= 1/81.07
df.loc[row_indexes_2,'Odds']= 1/8.39
df['Prize Level Total'] = df['Winners'] * df['Prize Amount'] # Amount of prizes per category

# create new df to account for free tickets rolling over from one day to the next
dfFreeTicket = df[df['Prize Level'] == '2-of-5'].reset_index(drop = True)
dfFreeTicket['Winners'] = dfFreeTicket['Winners'].shift(1) # shifts the values down by 1 so that the day before lines up with current day

# creates a new df to add up the prizes for each day
dfDateSum = df.groupby(['Date']).agg({'Prize Level Total':sum}).reset_index()
dfDateSum['Free Ticket'] = dfFreeTicket['Winners']
dfDateSum = pd.concat([dfDateSum]*4, ignore_index=True).sort_values('Date', ignore_index=True)

df['Date Prize Sum'] = dfDateSum['Prize Level Total'] # brings the summed prizes for the day back into the original df
df['Previous Free Tickets'] = dfDateSum['Free Ticket'] # brings the free tickets for the day back into the original df
df = df[4:].reset_index(drop = True).astype({'Previous Free Tickets': int}) # drops the first day from the df
df['Eligible Tickets'] = ((df['Date Prize Sum'] / percentDollar).round(0).astype(int)) + df['Previous Free Tickets'] # estimate the tickets in the day's game 
df['Estimated Ticket Sales'] = df['Eligible Tickets'] - df['Previous Free Tickets'] # estimate the sales by subtracting the free tickets

# check the accuracy of the estimations above
df['Estimated Winners'] = df['Odds'] * df['Eligible Tickets'] # calculate the winners based on the odds
df['Winners % Difference'] = (df['Winners'] - df['Estimated Winners'])/df['Estimated Winners'] # % difference formula
df['Ratio Winners'] = df['Winners']/df['Eligible Tickets'] # ratio of winners out of total tickets per game
df['Ratio Estimated Winners'] = df['Odds'] # ratio of winners out of total estimated tickets per game
df['Ratio Prize Amount'] = df['Prize Level Total']/df['Estimated Ticket Sales'] # ratio of prize money per level out of total prize pool

# setup for experiment in next code
df['Experiment Tickets'] = df['Eligible Tickets'] + 376992 # there is 1/376992 odds to win '5-of-5' per game so that will be the number of my tickets 


# Saving data to csv file

fileName = 'Fantasy5_Analysis.csv' # intialize the new file name
df.to_csv(fileName, index = False) # creates a csv file of selected data
print(f'\nCSV file {fileName} created') # confirmation of the file creation

dfRolldown = df[(df['Prize Level'] == '5-of-5') & (df['Winners'] == 0)] # creates a new df for plotting the rolldowns

# Plotting results

months = mdates.MonthLocator()  # Every month
fmt = mdates.DateFormatter('%b') # Specify the format to be shorthand months

fig, (ax1, ax2) = plt.subplots(2, sharex=True) # setup the figure with two subplots
fig.suptitle('Fantasy5 Analysis') # title the figure

# subplot 1: displaying the sales data and eleigible tickets for each game with rolldowns marked
ax1.plot(df['Date'][::4],df['Estimated Ticket Sales'][::4],lw=1, marker='o', ms=2,label = 'Sales') # first curve
ax1.plot(df['Date'][::4],df['Eligible Tickets'][::4],lw=1, marker='o', ms=2,label = 'Tickets') # second curve
ax1.plot(dfRolldown['Date'],dfRolldown['Eligible Tickets'], linestyle="None",marker='o', ms=4,label = 'Rolldown') # marked rolldowns
ax1.legend(loc="best", bbox_to_anchor=(1, 1)) # legend location on figure

# subplot 2: comparing the estimated number of winners to actual for each prize level
# '5-of-5' prize level comparison
ax2.plot(df['Date'][0::4],df['Ratio Estimated Winners'][0::4],lw=1,linestyle='dashed', label = '5-of-5 Est. Ratio')
ax2.plot(df['Date'][0::4],df['Ratio Winners'][0::4],lw=1,c='C0',label = '5-of-5 Actual Ratio')
# '4-of-5' prize level comparison
ax2.plot(df['Date'][1::4],df['Ratio Estimated Winners'][1::4],lw=1,linestyle='dashed', label = '4-of-5 Est. Ratio')
ax2.plot(df['Date'][1::4],df['Ratio Winners'][1::4],lw=1,c='C1',label = '4-of-5 Actual Ratio')
# '3-of-5' prize level comparison
ax2.plot(df['Date'][2::4],df['Ratio Estimated Winners'][2::4],lw=1,linestyle='dashed', label = '3-of-5 Est. Ratio')
ax2.plot(df['Date'][2::4],df['Ratio Winners'][2::4],lw=1,c='C2',label = '3-of-5 Actual Ratio')
# '2-of-5' prize level comparison
ax2.plot(df['Date'][3::4],df['Ratio Estimated Winners'][3::4],lw=1,linestyle='dashed', label = '2-of-5 Est. Ratio')
ax2.plot(df['Date'][3::4],df['Ratio Winners'][3::4],lw=1,c='C3',label = '2-of-5 Actual Ratio')
ax2.legend(loc="best", bbox_to_anchor=(1, 1)) # legend location on figure

# making the month markers the only x axis display
X = plt.gca().xaxis
X.set_major_locator(months)
X.set_major_formatter(fmt)

plt.yscale("log") # log scale the y axis to show each prize level category
plt.tight_layout() # for clean formating of figure
plt.show() # display plot
