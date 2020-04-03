#!/usr/bin/python

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import re
import argparse
from os import path
from csv import QUOTE_ALL

from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

def fetch_html() -> str:
    '''
    Fetch the HTML from the MOHLTC page and save into the html/ directory
    '''

    # Get the timestamp
    datestring = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Create the outputfilename
    outputfilename = './html/2019-novel-coronavirus_'+datestring+'.html'

    # Add headless option for geckodriver
    options = Options()
    options.add_argument("--headless")

    # Fetch the page
    try:
        driver = webdriver.Firefox(options=options)
        driver.get('https://www.ontario.ca/page/2019-novel-coronavirus')
        
        # Wait until the 'Status of Cases in Ontario' element has finished loading
        element_present = EC.presence_of_element_located((By.ID, 'section-0'))
        WebDriverWait(driver, 10).until(element_present)
    
    except:
        print('Failed to get page')

    # Save local copy of the HTML
    f = open(outputfilename, 'w')
    f.write(driver.page_source)
    f.close()

    # Kill the browser
    driver.quit()

    # Return the filename of the written file
    return outputfilename

def process_html_file(filepath: str, outputfilename: str = None):
    '''
    Processes the html source and saves the COVID data contained to CSV

    INPUTS:
        filepath (str) : the relative path of the saved page to process
        outputfilename (str): the output filename (and path) for the csv
    '''
    
    # If no outputfilename is specified, use the default
    if outputfilename is None:
        filename = path.basename(filepath).split('.')[0]
        outputfilename = './csv/' + filename + '.csv'

    # Read in the file
    f = open(filepath, 'r')
    htmlsource = f.read()
    f.close()

    # Create soup object
    soup = BeautifulSoup(htmlsource, features="lxml")
    
    ###################################
    #### STATUS OF CASES IN ONTARIO ###
    ###################################
    # Get the status update table
    iPHIS_table = pd.read_html(htmlsource)[0]
    
    # Take transpose, get columns names and write out
    iPHIS2 = iPHIS_table.transpose().reset_index()
    iPHIS2.columns = iPHIS2.iloc[0, :]
    
    # Get the updated timestamp for the status updates
    updated_timestamp_caption = soup.find_all('table')[0].find('caption').text
    # The below returns in this format, taken from the page: March 28, 2020 at 5:30 p.m. ET
    updated_timestamp_string = re.search('.*to\ (.*)', updated_timestamp_caption)[1]
    print(updated_timestamp_string)
    
    # Convert to ISO
    updated_iso = pd.to_datetime(updated_timestamp_string).isoformat()
    
    # Drop the column name row and % daily change row
    iPHIS2.drop(index=[0, 2], axis=0, inplace=True)

    # Process iPHIS data to be in line with old case status format
    # Reorder columns
    iPHIS3 = iPHIS2[['Currently Under Investigation5','Number of cases1','Resolved2', 'Deceased3', 'Total Tested4']]
    # Total approved for testing = total tested + under investigation
    iPHIS3['Total number of patients approved for COVID-19 testing to date'] = iPHIS3['Currently Under Investigation5'] + iPHIS3['Total Tested4'] 
    # Negative = Total Tested - (Positive + Resolved + Deceased)
    iPHIS3['Negative1'] = iPHIS3['Total Tested4'] - (iPHIS3['Number of cases1'] + iPHIS3['Resolved2'] + iPHIS3['Deceased3'])
    # Rename and order columns
    iPHIS4 = iPHIS3[['Negative1', 'Currently Under Investigation5', 'Number of cases1', 'Resolved2', 'Deceased3', 'Total number of patients approved for COVID-19 testing to date']]
    iPHIS4.columns = ['Negative1', 'Currently under investigation2', 'Confirmed positive3', 'Resolved4', 'Deceased', 'Total number of patients approved for COVID-19 testing to date']

    # Cast to int64
    iPHIS4 = iPHIS4.astype(int)

    # Add updated timestamp
    iPHIS4['updated_timestamp'] = updated_iso

    # Add retrieved timestamp
    iPHIS4['retrieved_timestamp'] = pd.to_datetime(datetime.now().replace(microsecond=0)).isoformat()

    # Write to csv
    iPHIS4.to_csv(outputfilename, header=True, index=False, quoting=QUOTE_ALL)
    
    ###################################
    ## NEW CONFIRMED POSITIVE CASES ###
    ###################################

    # TODO - missing on Ministry site since 2020-03-27

def process_html_directory():
    '''
    TODO: This function will process a whole directory of saved copies of the page and batch output csv
    '''

    pass

    
if __name__ == '__main__':

    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetchonly", help="Fetch and save HTML only", action="store_true")
    parser.add_argument("--fromfile", help="Process saved HTML file", type=str)
    parser.add_argument("--processdir", help="Process all saved HTML in a specified directory", type=str)
    parser.add_argument("--nosavecsv", help="Flag to toggle saving of csv", action="store_true")
    args = parser.parse_args()

    # Get the page and save in the HTML directory
    if(args.fromfile is None):
        saved_html_path = fetch_html()    
    else:
        saved_html_path = args.fromfile

    process_html_file(saved_html_path)
