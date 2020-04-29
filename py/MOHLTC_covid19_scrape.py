#!/usr/bin/python

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import re
import argparse
import glob
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
        driver.get('https://www.ontario.ca/page/how-ontario-is-responding-covid-19#section-0')
        
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
    status_update = pd.read_html(htmlsource)[0]

    try:
        # The below returns in this format, taken from the page: March 28, 2020 at 5:30 p.m. ET
        updated_timestamp_string = BeautifulSoup(re.search('.*Last\ updated:\ (.*)', htmlsource)[1], features="lxml").text
        # Remove the 'ET'
        updated_timestamp_string = updated_timestamp_string.rsplit(' ', 1)[0]
        print(updated_timestamp_string)
    except:
        updated_timestamp_string = ''
    
    # Convert to ISO
    updated_iso = pd.to_datetime(updated_timestamp_string).isoformat()

    # Take transpose, get columns names and write out
    st2 = status_update.transpose()
    st2.columns = st2.iloc[0,:]
    st2.drop(index=0, axis=0, inplace=True)

    # Add updated timestamp
    st2['updated_timestamp'] = updated_iso

    # Add retrieved timestamp
    st2['retrieved_timestamp'] = pd.to_datetime(datetime.now().replace(microsecond=0)).isoformat()

    # Write to csv
    st2.to_csv(outputfilename, header=True, index=False, quoting=QUOTE_ALL)
    
    ###################################
    ## NEW CONFIRMED POSITIVE CASES ###
    ###################################

    # TODO - missing on Ministry site since 2020-03-27

def process_html_directory(dirpath: str, outputpath: str = './csv/'):

    # Get path of all HTML files in the directory
    all_files = glob.glob(dirpath + "*.html")

    for filename in all_files:
        
        print(f"Reading {filename}")
        
        # Generate the outputfilename 
        file_basename = path.basename(filename).split('.')[0]
        outputfilename = outputpath + file_basename + '.csv'
        
        # Process the file
        process_html_file(filename, outputfilename)
        
        print(f"Writing {outputfilename}")

    
if __name__ == '__main__':

    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetchonly", help="Fetch and save HTML only", action="store_true")
    parser.add_argument("--fromfile", help="Process saved HTML file", type=str)
    parser.add_argument("--processdir", help="Process all saved HTML in a specified directory", type=str)
    parser.add_argument("--outputdir", help="Path to save csvs for processing directory of HTML", type=str)
    parser.add_argument("--nosavecsv", help="Flag to toggle saving of csv", action="store_true")
    args = parser.parse_args()

    if(args.processdir):
        # Process directory of saved HTML files in batch
        process_html_directory(args.processdir, args.outputdir)
    else:
        # Otherwise
        if(args.fromfile is None):
            # Get the page and save in the HTML directory
            saved_html_path = fetch_html()    
        else:
            saved_html_path = args.fromfile

        process_html_file(saved_html_path)
