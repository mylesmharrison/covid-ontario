#!/usr/bin/python

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re

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

    # Get the timestamp
    datestring = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save local copy of the HTML
    f = open('./html/2019-novel-coronavirus_'+datestring+'.html', 'w')
    f.write(driver.page_source)
    f.close()

    # Create soup object
    soup = BeautifulSoup(driver.page_source)
    
    # Get the status update table
    status_update = pd.read_html(driver.page_source)[0]

    # Get the updated timestamp for the status updates
    updated_timestamp_p = soup.find(id='pagebody').find_all('p')[4].text.encode('ascii', errors='ignore').decode('utf8')
    updated_timestamp_string = re.search('.*as of(.*)', updated_timestamp_p)[1]
    
    # Convert to ISO
    updated_iso = pd.to_datetime(updated_timestamp_string).isoformat()

    # Take transpose, get columns names and write out
    st2 = status_update.transpose()
    st2.columns = st2.iloc[0,:]
    st2.drop(index=0, axis=0, inplace=True)

    # Add updated timestamp
    st2['updated_timestamp'] = updated_iso

    # Add retrieved timestamp
    st2['retrieved_timestamp'] = pd.to_datetime(datetime.now()).isoformat()

    # Write to csv
    st2.to_csv('test.csv', header=True, index=False)

    # Kill the browser
    driver.quit()