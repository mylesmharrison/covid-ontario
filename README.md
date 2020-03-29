# COVID-ontario

Visualization and tracking of COVID data releases from the Ontario Ministry of Health and Long-term Care (MOHLTC) available here from the 2019 Novel Coronavirus page: https://www.ontario.ca/page/2019-novel-coronavirus

@author mylesmharrison (myles at mylesharrison dot com)

![summaryplot](./plots/summaryplot_2020-03-29.png)

### Other Data Sources

This also relies on data gathered by the MIDAS Network, available here: https://github.com/midas-network/COVID-19/tree/master/data/cases/canada/ontario_situation_updates

### Web Scraping

The web scraper requires the [geckodriver](https://github.com/mozilla/geckodriver/releases/tag/v0.26.0) executable to be in a directory in your PATH

**Usage:**

1. Scrape page and save both HTML and csv
    ```bash
    python py/MOHLTC_covid19_scrape.py
    ```

2. Extract from previously saved HTML
    ```bash
    python py/MOHLTC_covid19_scrape.py --fromfile html/2019-novelcoronavirus_20200329_104219.html
    ```

### TO DO

- <s>Add python scraper using `pd.read_html()`</s>
- <s>Split python scaper into separate python file and automate csv generation</s>
- Test automation of web scraper
- Create .py file for batch plot generation / update
- Organize csv output and MIDAS data
- Tableau dashboarding
