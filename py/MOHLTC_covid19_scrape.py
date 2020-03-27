#!/usr/bin/python

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd

if __name__ == '__main__':
    
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

    # Get the status update table
    status_update = pd.read_html(driver.page_source)[0]

    # Take transpose, get columns names and write out
    st2 = status_update.transpose()
    st2.columns = st2.iloc[0,:]
    st2.drop(index=0, axis=0, inplace=True)
    st2.to_csv('test.csv', header=True)