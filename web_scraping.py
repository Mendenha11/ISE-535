
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 08:14:14 2021

@author: scott
"""

# IMPORTS

from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from datetime import date, timedelta

# FUNCTIONS

# creates a list of days from the start to the end by a day at a time
def date_ranger(start, end):
    return pd.date_range(start,end-timedelta(days=1),freq='d')

# creates a list of URLs based on the date range selected
def URL_maker(URLdates):
    frontHalf = 'https://flalottery.com/site/winningNumberSearch?searchTypeIn=date&gameNameIn=FANTASY5&singleDateIn=' 
    backHalf = '&fromDateIn=&toDateIn=&n1=&n2=&n3=&n4=&n5=&n6=&pb=&mb=&submitForm=Submit'
    URLs = [frontHalf+URLdate+backHalf for URLdate in URLdates]
    return URLs

# MAIN CODE BODY

# Web Scrapping

# select date range for web scraping data set including one day prior to desired start date
startDate = date(2020,12,31) # chose end of the year to use a value from it in the new year
endDate = date.today() # chose current date 12/1/21 as end date


dateRange = [d.strftime('%m/%d/%Y') for d in date_ranger(startDate,endDate)] # format date range to be used in file
dateRangeURL= [d.strftime('%m'+'%%2F'+'%d'+'%%2F'+'%Y') for d in date_ranger(startDate,endDate)] # format date range to be used in URL 
URLs = URL_maker(dateRangeURL) # complete list of formatted URLs for chosen dates


driver = webdriver.Safari() # initiate selenium driver
driver.get(URLs[0]) # opens a new window at the given website the first of the URLs
soup = BeautifulSoup(driver.page_source, "html.parser") # pass the HTML contents to Beautiful Soup for parsing

# extract the titles from the table of the winner information
titlePrizeLevel = soup.find('th', {'class': 'column1'}).text
titleWinners = soup.find('th', {'class': 'column2'}).text
titleAmount = soup.find('th', {'class': 'column3'}).text 

driver.close() # closes the website after information is collected

# intitalize table contents as lists
firstBalls = []
secondBalls = []
thirdBalls = []
fourthBalls = []
fifthBalls = []
prizeLevel = []
winners = []
prizeAmount = []

for URL in URLs:
    driver = webdriver.Safari() # initiate selenium driver
    driver.get(URL) # opens a new window at the given website in the list of websites
    soup = BeautifulSoup(driver.page_source, "html.parser") # pass the HTML contents to Beautiful Soup for parsing
    winningSet = []
    winningSet.append([info.text for info in soup.find_all('span', {'class': 'balls'})]) # extracts more than the numbers on each of the winning balls
    winningNumbers = [val for sublist in winningSet for val in sublist] # gets rid of all other non-winning number info
    intWinningNumbers = [int(val) for val in winningNumbers[:5]] # turns the winning numbers into integers
    
    # sends each winning number to its respective list
    firstBalls.append(intWinningNumbers[0])
    secondBalls.append(intWinningNumbers[1])
    thirdBalls.append(intWinningNumbers[2])
    fourthBalls.append(intWinningNumbers[3])
    fifthBalls.append(intWinningNumbers[4])
   
    prizeLevel.append([info.text for info in soup.find_all('td', {'class': 'column1'})]) # extract how many balls were matched to the list
    winners.append([info.text for info in soup.find_all('td', {'class': 'column2'})]) # extract number of winners to the list
    prizeAmount.append([info.text for info in soup.find_all('td', {'class': 'column3 columnLast'})]) # extract winning $ amount to the list
    
    driver.close() # closes the website each time after information is collected

# Data compilation

# creates a pandas DataFrame of the dates and table content lists with the column headings that were extracted
df = pd.DataFrame(zip(dateRange,firstBalls, secondBalls, thirdBalls, fourthBalls, fifthBalls, prizeLevel, winners, prizeAmount), 
                  columns=['Date','First', 'Second', 'Third', 'Fourth', 'Fifth', str(titlePrizeLevel), str(titleWinners[:-1]), str(titleAmount)])

# Data cleaning

# pandas 1.3.0 or higher required for pandas.DataFrame.explode(list(column_names))
# Otherwise .explode() can do only one column at a time
df = df.explode(['Prize Level', 'Winners','Prize Amount'], ignore_index= True) # lists that were all on signle rows are expanded to be on multiple rows

columnTitles = df.columns # list of column titles
df[columnTitles] = df[columnTitles].replace({',': '','\$':'','Free Ticket':'1.00'}, regex = True) # repace each instance of the dictionary key with the value across the list

dataTypes = {'Date':'datetime64', 'First':int, 'Second':int, 'Third':int, 'Fourth':int, 'Fifth':int, 'Winners':int, 'Prize Amount':float} # dictionary of desired data types
df = df.astype(dataTypes) # change column data types to selection

# Saving data to csv file

fileName = 'Fantasy5_Data.csv' # intialize the new file name
df.to_csv(fileName, index = False) # creates a csv file of selected data
print(f'\nCSV file {fileName} created') # confirmation of the file creation
