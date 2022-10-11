from . import fileio
from . import scraper

from datetime import datetime as dt
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

import os
import pprint
import re


HEADERS ={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"
}

driver = None
dataframes_map = {}
searched_urls_map = {}


def init_driver():
    global driver
    driver = webdriver.Chrome(ChromeDriverManager().install())


def get_search_timestamp():
    return dt.now().strftime('%y-%m-%dT%H-%M')


def add_to_dataframes_map(sheet_name, df):
    dataframes_map[sheet_name] = df


def add_to_searched_urls_map(search_name, search_url):
    searched_urls_map[search_name] = search_url


def get_searched_page(job_query, location, url='https://indeed.com/'):
    driver.get(url)
    sleep(3)
    query_field = driver.find_element('xpath', '//*[@id="text-input-what"]')
    query_field.send_keys(Keys.CONTROL + "a")
    query_field.send_keys(Keys.DELETE)
    sleep(.6)
    query_field.send_keys(job_query)
    sleep(1)
    
    loc_field = driver.find_element('xpath', '//*[@id="text-input-where"]')
    loc_field.send_keys(Keys.CONTROL + "a")
    loc_field.send_keys(Keys.DELETE)
    sleep(.6)
    loc_field.send_keys(location)
    sleep(1)
    try:
        loc_field.send_keys(Keys.ENTER)
    except:
        driver.find_element('xpath', '//button[@type="submit"]').click()
    sleep(3)

    return driver.current_url, driver.page_source, get_search_timestamp()


def single_search(location, job_query, url='https://indeed.com/', save_to_file=True, scraped_filename=None):
    filename_timestamp = get_search_timestamp()
    
    if scraped_filename == None:
        scraped_filename = 'searched_jobs/' + filename_timestamp + '_job-searches.xlsx'
    try:
        url, source, timestamp = get_searched_page(job_query, location, url)
        results_df = scraper.scrape_job_details(source)
    except Exception as e:
        print(e)
        print("\nURL searched:\n" + url)

    if save_to_file:
        loc = re.sub(r'[^A-Za-z0-9 ]+', '', location)
        tokens = re.split('\s+', loc)
        location_fname = "-".join(tokens)
        search_name = (location_fname + '_' + timestamp)[:30] # Apparently some programs cannot read sheets with names over 31 chars.

        fileio.export_single_dataframe_to_excel(results_df, url, scraped_filename, sheet_name=search_name)
    else:
        print("Search results:")
        pprint(results_df)



def batch_search(locations_file, job_query, url='https://indeed.com/', start_index=0,
                    stop_index=None, save_to_file=True, scraped_filename=None):

    locations_df, file_success = fileio.load_locations_from_CSV(locations_file)
    if not file_success:
        print("The file could not be read. Please check the filepath and format.")
        exit(1)

    print('++++++++++++++++++++++++++++++++')
    print(locations_df.head(5))
    print('++++++++++++++++++++++++++++++++')

    filename_timestamp = get_search_timestamp()

    if scraped_filename == None:
        scraped_filename = 'searched_jobs/' + filename_timestamp  + '_bulk-job-searches.xlsx'

    if stop_index == None:
        stop_index = locations_df.shape[0]
    else:
        stop_index += 1 # Making upper bound inclusive

    for i in range(start_index, stop_index):
        location = locations_df.iloc[i][1]
        try: location += ", " + locations_df.iloc[i][2] # Append loc2 if it exists
        except: pass
        try:
            url, source, timestamp = get_searched_page(job_query, location, url)
            results_df = scraper.scrape_job_details(source)
        except Exception as e:
            print(e)
            print(f"\nError at index {i} (line {i+1}) in locations file.")
            print("Use the index as an arg to start batch search from this location.")
            fileio.export_bulk_dataframes_to_excel(dataframes_map, scraped_filename)
            break

        ## Store data in dictionary:
        loc = re.sub(r'[^A-Za-z0-9 ]+', '', location)
        tokens = re.split('\s+', loc)
        location_fname = "-".join(tokens)
        search_name = (location_fname + '_' + timestamp)[:30] # Apparently some programs cannot read sheets with names over 31 chars.

        add_to_searched_urls_map(search_name=search_name, search_url=url)

        if save_to_file and results_df.shape[0] != 0:
            add_to_dataframes_map(sheet_name=search_name, df=results_df)
    
    ## Save file or at least print out the search names, URLS
    if save_to_file:
        filepath = os.path.split(scraped_filename)[0]
        searched_urls_filename = os.path.join(filepath, filename_timestamp + '_bulk-urls-searched.xlsx') # Works regardless if filepath == '' or not

        fileio.export_bulk_dataframes_to_excel(dataframes_map, scraped_filename)
        fileio.export_search_urls_to_excel(searched_urls_map, searched_urls_filename, job_query)
    else:
        print("Searches:")
        pprint(searched_urls_map)
        os.system(f"rm {scraped_filename}")