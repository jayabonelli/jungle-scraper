# First, all of the necessary imports...
'''Look at the requirements.txt file for all of the required dependencies. 
All of those that don't appear in that doc should be already installed with the Python Standard Library. 
https://pypi.org/'''
from selenium import webdriver #pour le jvaascript 
import sys 
import pandas as pd
import time
from bs4 import BeautifulSoup
from requests import get
import string
from string import *
import csv
import os
import math 
# IMPORTANT: IF USING A MAC, DOWNLOAD 'CHROMEDRIVER' IN THE 'APPLICATIONS' FOLDER (cf the 'driver = webdriver.Chrome("/Applications/chromedriver", options=options)' line).
# https://chromedriver.storage.googleapis.com/index.html?path=75.0.3770.90/


# Now, (in the correct order) all of the helper functions I will be calling.

# First, the helper functions to set up the lists for the search results table.
# Start by setting up a list of all the names. 
# This function returns a list of all of the names of the companies (in string format.)
def name(soup):
    #takes in, from the source code, the parts which will containe the names. 
    names_html = soup.find_all('span', class_='ais-Highlight-nonHighlighted')
    names = []
    # for every "name" appearing: cast it into a string and add it to the list of names.
    for i in range (len(names_html)):
        names.append(names_html[i].text.strip())
    return names


# Set up a list of all the links to the individual welcome_to_the_jungle pages, for each company. 
# This function returns a list of all of the urls for the welcome to the jungle pages (in string format.)
def link(soup):
    #collects all of the parts that will contain the links to the welcometothejungle page of each company. 
    links_html = soup.find_all('a', class_='sc-bRBYWo dHiStY')
    links = []
    #for every link, cast it to a string and complete the url.
    for i in range (len(links_html)):
        links.append('https://www.welcometothejungle.co' + links_html[i].get('href'))
    return links


# Set up a list of all the headquarter locations. 
# This function returns a list of all of the headquarter locations (in string format.)
def location(soup):
    #collects all of the parts of the source code that will contain headquarter locations. 
    locations_html = soup.find_all('li', class_='sc-cHGsZl ghZLDM')
    locations = []
    #for every company, add its headquarter locations to the general list.
    for i in range (int(len(locations_html)/3)):
        locations.append(locations_html[3*i+1].text.strip())
    return locations


# Set up list of all the numbers of job offers - for each company. 
# This function returns a list of all of the numbers of job offers (in string format, so to be formatted to int later.)
def job(soup):
    #collects all of the parts of the source code that will contain number of job offers. 
    jobs_html = soup.find_all('div', class_='sc-1cza0uq-4 ipodvt')
    jobs = []
    #for every company, add the number of job offers to the general list.
    for i in range (len(jobs_html)):
        jobs.append(jobs_html[i].text)
    return jobs


# Now, the info() function which will permit us to gather the information relative to each company based on the search results
# This function returns a pandas dataframe (df) with all of the data of a particular day: 
# But the returned data is only that which can be collected from the search results page directly
# (ie. the total number of employees/websites aren't yet present.)
def info(soup): 
    #It first calls all of the above functions to determine each column, and then zips them in the dataframe.
    table = list(zip(name(soup),link(soup), location(soup),job(soup)))
    table
    df = pd.DataFrame(table, columns = ['name', 'url', 'locations','jobs']) 
    return df
    


# The url_and_employees() function 
# For each company (taking as input the url to its welcome_to_the_jungle page), it returns its link (website) and its total number of employees
# The input 'url' is the link to the individual welcome_to_the_jungle page of the company. 
# if you miss both the number of employees and the link
def url_and_employees(url): 
    try:
        # print(url)
        # First, run the url and collect its source code.
        response = get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        # print(response.text)
        type(html_soup)
        # Default value of number of employees is 0 (normally, this shouldn't cause a problem.)
        employees = "0"
        # Collect number of employees, in string format. 
        employees = (html_soup.find_all('span', class_= "sc-dxZgTM cEZMCX")[1]).text
        # Collect website url, and then add "https://"
        link_x = html_soup.find('a', class_= "sc-hmzhuo cZJKcH")
        link = "https://" + link_x.text
        # If everything worked correctly up until now, return the number of employees and website url, normal case.
        return [link, employees]
    except Exception as e: 
        '''Here there might be an error if the number of employees caused the exception, ie. the number of employees is not indicated. '''
        ''' If it crashed somewhere: this happens rarely enough to be treated "minimally": return default number of employees
        as well as welcometothejungle page url instead of website url.'''
        print(e)
        return[url, employees]

# Now that all of the helper functions are out of the way, we can start the "real", "big" program. 
# First: accessing the Chrome browser driver and "opening a window" (in incognito mode).
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
# The scraper is NOT headless: which means that, when the program runs, it will open a welcometothejungle page. 
# options.add_argument('--headless')
# ******************************************
# Important warning about chromedriver executable. 
driver = webdriver.Chrome("/Applications/chromedriver", options=options)


# Running the browser driver on the relevant welcometothejungle page. 
''' The reason I separate the search into two sets (the companies with < 15 employees & those with 15-50 employees) is because welcometothejungle
only allows 1000 companies to appear on search results, so I need to launch two separate searches to obtain all 1100+ companies. '''
# First, running it on the welcometothejungle search results for all companies of between 15 and 50 employees. 
# This is a link that might be changed - it will then cause an error, so change if necessary.
driver.get('https://www.welcometothejungle.co/fr/companies?refinementList%5Bsize.fr%5D%5B%5D=Entre%2015%20et%2050%20salari%C3%A9s&page=1&configure%5Bfilters%5D=website.reference%3Awttj_fr&configure%5BhitsPerPage%5D=30')

# Run the algorithm on all of the pages (to collect the data on each page, I call the 'info' function.)
# Append, progressively, all of the data to the "un_parsed_search_results" Pandas Dataframe.
un_parsed_search_results = pd.DataFrame()
# Look for all of the "go to: page xxx" buttons, in the source code, in order to later click on to the next page. 
more_buttons = driver.find_elements_by_class_name("ais-Pagination-link")
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')
type(soup)
# Append info of the first page to the dataframe. 
un_parsed_search_results = un_parsed_search_results.append(pd.DataFrame(info(soup)))
j=100
# Iterate through all of the other pages in order to obtain, for each the corresponding info and then add it to the dataframe. 
# The 100 iterations is by convention - normally, only ~40 should be needed to recuperate all of the data. 
''' The reason I put 100 iterations is because I don't know how to recuperate the exact amount of pages I'll be iterating through. 
As such, I hardcoded 100 just to be safe, only thing is it might iterate wayyyyy too many times. '''
for i in range(j): 
    try: 
        if more_buttons[-1].is_displayed():
            # Finds all the 'page' buttons. 
            more_buttons = driver.find_elements_by_class_name("ais-Pagination-link")
            # Sets the driver to click on to the next page. 
            driver.execute_script("arguments[0].click();", more_buttons[-1])
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')           
            type(soup)
            # Appends this page's info to the dataframe.
            un_parsed_search_results = un_parsed_search_results.append(pd.DataFrame(info(soup)))
            # I set the sleep time to 4 seconds in order to allow for time to load the page. 
            time.sleep(4)
    except Exception as e:
            # What happens when there's a StaleELement Exception: print the error, refresh and retry. 
            print(un_parsed_search_results) 
            print(e)
            driver.refresh()
            time.sleep(1)
            more_buttons = driver.find_elements_by_class_name("ais-Pagination-link")

# Same thing as previously, now, on all of the companies of strictly less than 15 employees. 
driver.get('https://www.welcometothejungle.co/fr/companies?refinementList%5Bsize.fr%5D%5B%5D=%3C%2015%20salari%C3%A9s&page=1&configure%5Bfilters%5D=website.reference%3Awttj_fr&configure%5BhitsPerPage%5D=30')
# Look for all of the "go to: page xxx" buttons, in the source code, in order to later click on to the next page. 
more_buttons = driver.find_elements_by_class_name("ais-Pagination-link")
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'lxml')
type(soup)
# Append info of the first page to the dataframe. 
un_parsed_search_results = un_parsed_search_results.append(pd.DataFrame(info(soup)))
j=100
# Iterate through all of the other pages in order to obtain, for each the corresponding info and then add it to the dataframe. 
for i in range(j): 
    try: 
        if more_buttons[-1].is_displayed():
            # Finds all the 'page' buttons. 
            more_buttons = driver.find_elements_by_class_name("ais-Pagination-link")
            # Sets the driver to click on to the next page. 
            driver.execute_script("arguments[0].click();", more_buttons[-1])
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')           
            type(soup)
            # Appends this page's info to the dataframe.
            un_parsed_search_results = un_parsed_search_results.append(pd.DataFrame(info(soup)))
            time.sleep(4)
    except Exception as e:
            # What happens when there's a StaleELement Exception: print the error, refresh and retry.  
            print(e)
            driver.refresh()
            time.sleep(1)
            more_buttons = driver.find_elements_by_class_name("ais-Pagination-link")


# Add the individual page data: for each company, collect the url and the total number of employees. 
# First: regularize the index situation.
un_parsed_search_results.reset_index(inplace=True)
employees =[]
links = []
# Iterate through the dataframe to collect the number of employees and website of each company. 
''' Then: for every company in the dataframe: call the url_and_employees function to obtain the data.
Then append the data into two new columns (links is the list representing the column of the website urls, 
employees is the list representing the column with the number of employees), and then add the columns to the dataframe. '''

for i in range(len(un_parsed_search_results.index)):
    l = url_and_employees(un_parsed_search_results.iloc[i, 2])
    try:
        links.append(l[0])
    except:
        links.append("")
    try:
        employees.append(int(l[1]))
    except:
        employees.append(0)
un_parsed_search_results.insert(len(un_parsed_search_results.columns), 'employees', employees)
un_parsed_search_results.insert(len(un_parsed_search_results.columns), 'website', links)
# Sometimes, a new column is 'randomly' created (so I drop it.)
un_parsed_search_results.drop(columns = ["index"], inplace=True)
# un_parsed_search_results
df = un_parsed_search_results
# df
# Specify the order of the columns. 
cols = ['name', 'url','locations','website','jobs','employees']
df = df[cols]


# Now, take user input for the date. 

date = input("Write the date in the following format: DD-MM ")
print("A guide to the different files created/updated: \n- " + date + '_only.csv is all of the data collected today\n- ' + date + '_diff is all of the new companies that just appeared on the platform\n- ' + date + '_incr_a is all of the companies whose number of job offers increased, sorted with respect to the number of \noffers\n- ' + date + '_incr_b is all of the companies whose number of job offers increased, sorted with respect to the number of\n offers/sqrt(number of employees)\n- database.csv is all of the data since the beginning, up until today'  ) 
      
# Take scraped data and parse the jobs into numbers. 
df['jobs'] = df['jobs'].apply(lambda x: int(((x.strip('jobs')).strip('job')).strip()) if ' job' in x else x)

# Take out all of the commas in the names/locations (it poses problems when you read the file from csv format.)
df['locations'] = df['locations'].apply(lambda x: x.replace(',', ' ') if ',' in x else x)
df['name'] = df['name'].apply(lambda x: x.replace(',', ' ') if ',' in x else x)

# Add the date in some column names.
df.rename(columns={'jobs':(date + ' jobs'), 'employees':(date+ ' employees')}, inplace=True)

# Save this week's data in a new file: DD-MM_only.csv
only = date + '_only' + '.csv'
df.to_csv(r'a.csv', encoding="utf-8")
os.rename('a.csv', date + '_only.csv')


# Read from the "database.csv" file (the file collecting all of the data since when we started collecting it.)
# If it doesn't exist yet, create it, and exit program. 
try: 
    d1 = pd.read_csv('database.csv', quoting=csv.QUOTE_NONE, sep=',')
except Exception as e:
    print(e)
    os.rename(date + '_only.csv', 'database.csv')
    exit(0)

# So d1 is all of the data from past weeks, d2 is the data from today. 
d2 = pd.read_csv(only, quoting=csv.QUOTE_NONE, sep=',')

l = list(d1['website'])

# Iterate through new list and find the new companies
# l = a list of all the urls (I'm comparing the companies based on their website address, less encoding-related errors that way. )
lt = list()
# print(l)
# print(d2['website'])
# Now, I iterate through d2 (only today's data): 
for row in d2.itertuples():
    # For a row in d2, if it isn't in d2, I append it to the list of 'new rows': 
    # ie. if for all rows in d2, their website urls are all different to the row in d2.
    if (any((x == (row.website)) for x in l) is False):
        print(row.website)
        lt.append(row)
# Create strings for the column names (going to turn out super useful for later.)
str1 = date + " jobs"
str2 = date + ' employees'
# 'diff' is the dataframe with all of the new companies.
diff = pd.DataFrame(lt)

# Sometimes, new columns are added (so I need to remove them ...)
try: 
    d1.drop(columns = ["Unnamed: 0"], inplace=True)
    diff.drop(columns = ["Index","_1"], inplace=True)
except:
    pass
# Rename the columns - if necessary (I'm not 100 % sure why I did this.)
try: 
    diff.rename(columns={diff.columns[len(diff.columns)-1]: (str2)}, inplace = True)
    diff.rename(columns={diff.columns[len(diff.columns)-2]: (str1)}, inplace = True)
except Exception as e:
    print(e)

# Save the 'DD-MM_diff.csv' file that has all of the new companies. 
diff.to_csv(r'b.csv')
os.rename('b.csv', date + '_diff.csv')


# Add new companies to database and update values for this time. 
d1 = d1.append(diff,ignore_index = True, sort = False)
# create new columns for this week's values, if necessary.
l = range(d1.shape[0])
try:
    d1.insert(len(d1.columns),str1, l)
    d1.insert(len(d1.columns),str2, l)
except ValueError:
    pass
for i in range (len(d1)):
    for j in range (len(df)):
        if (d1.loc[i, "website"]).lower()==(df.loc[j, "website"]).lower():
            d1.at[i, str1] = df.at[j, str1]
            d1.at[i, str2] = df.at[j, str2]

# If there is no value for a certain date - which means that the company, then, isn't on the platform - write -1.0
d1.fillna(-1.0, inplace= True)

# Save the updated database to a file - update the current 'database.csv' file. 
d1.to_csv('database.csv')

# Select only the increasing rows, and sort them in terms of difference. 
#print(d1)
# Select the name of the column with the number of job offers from last time.
before = (d1.columns.values.tolist())[len(d1.columns)-4]

# Take only the rows where the number of job offers increased since last time. 
inc_a = d1[(d1[before] < d1[str1]) & (d1[before]>-1)]
dl = list()
# For every company whose job offers have increased, calculate the difference between today and last time, and add it to the dl list. 
for i in range(len(inc_a)):
    dl.append(inc_a.at[i, str1] - inc_a.at[i, before])
# Add dl as a column to the incr_a file - it's the column with the differences of job offers between last time and today. 
inc_a.insert(len(inc_a.columns), 'difference', dl)
# Sort the rows with respect to the difference. 
inc_a.sort_values(by =['difference'], ascending = False, inplace = True)
#print(inc)
'''Create the corresponding csv file: DD-MM_incr_a.csv is all of the companies with increasing job offers, 
and the 'difference' is calculated as the subtraction. '''
inc_a.to_csv(r'b.csv')
os.rename('b.csv', date + '_incr_a.csv')


# Take only the rows where the number of job offers increased since last time. 
inc_b = d1[(d1[before] < d1[str1]) & (d1[before]>-1)]
dm = list()

# For every company whose job offers have increased, calculate the difference between today and last time, and add it to the dl list. 
# Here the difference is the ratio of the number of job offers/ sqrt(total number of employees.)
for i in range(len(inc_b)):
    dm.append(inc_b.at[i, str1]/math.sqrt(inc_b.at[i, str2]) - inc_b.at[i, before]/math.sqrt(inc_b.at[i, len(d1.columns)-3]))
# Add dl as a column to the incr_b file - it's the column with the differences of job offers between last time and today. 
inc_b.insert(len(inc_b.columns), 'difference_ratio', dl)
# Sort the rows with respect to the difference. 
inc_b.sort_values(by =['difference_ratio'], ascending = False, inplace = True)
#print(inc)
'''Create the corresponding csv file: DD-MM_incr_b.csv is all of the companies with increasing job offers, 
and the 'difference' is calculated as the subtraction of ratios. '''
inc_b.to_csv(r'b.csv')
os.rename('b.csv', date + '_incr_b.csv')

