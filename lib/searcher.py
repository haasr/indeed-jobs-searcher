
from . import fileio
from . import scraper

from datetime import datetime as dt
from pprint import pprint
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import os
import re


driver = None
dataframes_map = {}
searched_urls_map = {}

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# TODO: Convert this module to IndeedSearch class eventually. That way this can be more
# than a command line tool. I should be able to integrate it with other code.

def init_driver():
    global driver
    #driver = webdriver.Chrome()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def close_driver():
    global driver
    driver.close()


def add_to_dataframes_map(sheet_name, df):
    dataframes_map[sheet_name] = df


def add_to_searched_urls_map(search_name, search_url):
    searched_urls_map[search_name] = search_url


def get_search_timestamp():
    return dt.now().strftime('%y-%m-%dT%H-%M')


def get_stop_index(stop_index, num_rows):
    if stop_index == None:
        return num_rows
    else:
        return stop_index + 1 # Making upper bound inclusive


def get_XLSX_filename(filename):
    if '.' in filename:
        ext_len = len(filename.split('.')[-1])
        return filename[:len(filename)-ext_len] + 'xlsx'
    else:
        return filename + '.xlsx'


def get_scraped_filename(filename, timestamp, suffix='_bulk-job-searches.xlsx'):
    if filename == None:
        return os.path.join('searched_jobs', timestamp  + suffix)
    else:
        return get_XLSX_filename(filename) # Guarantee Excel workbook (all fileio uses)


def get_search_sheet_name(location, timestamp):
    # Apparently some programs cannot read sheets with names over 31 chars so timestamp length will just be 30.
    loc = re.sub(r'[^A-Za-z0-9 ]+', '', location[:16]) # If name too long, shorten it to get full timestamp
    tokens = re.split('\s+', loc)
    location_fname = "-".join(tokens)
    return (location_fname + '_' + timestamp)


def save_dataframes_map_to_file(filename, filename_timestamp, job_query):
    f = os.path.split(filename) # The URLS file is going into the same folder (hence the use of os.path.split)
    if "bulk-job-searches" in filename: # Default filename used --> use the default format for URLs file.
        searched_urls_filename = os.path.join(f[0], filename_timestamp + '_bulk-urls-searched.xlsx') # Works regardless if filepath == '' or not
    else: # Custom filename used --> just add _urls.xlsx
        searched_urls_filename = os.path.join(f[0], f[1][:len(f[1])-5] + '_urls.xlsx')
    fileio.export_bulk_dataframes_to_excel(dataframes_map, filename)
    fileio.export_search_urls_to_excel(searched_urls_map, searched_urls_filename, job_query)


def get_searched_page(job_query, location, url='https://indeed.com/'):
    driver.get(url)
    sleep(4)
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
    scraped_filename = get_scraped_filename(scraped_filename, get_search_timestamp(), 
                                                suffix='_single-job-searches.xlsx')

    results_df = None

    try:
        url, source, timestamp = get_searched_page(job_query, location, url)
        results_df = scraper.scrape_job_details(source)
    except KeyError as ke:
        print("KeyError: " + str(ke))
        print("\nURL searched:\n" + url)
    except Exception as e:
        print(e)
        print("\nURL searched:\n" + url)

    if save_to_file:
        search_name = get_search_sheet_name(location, timestamp)
        fileio.export_single_dataframe_to_excel(results_df, url, scraped_filename, sheet_name=search_name)
    else:
        print("Search results:")
        pprint(results_df)

    close_driver()


def batch_search(locations_file, job_query, url='https://indeed.com/', start_index=0,
                    stop_index=None, save_to_file=True, scraped_filename=None):

    file_success, locations_df = fileio.load_locations_from_CSV(locations_file)
    if not file_success: # Will then close driver at end of method execution
        print("The file could not be read. Please check the filepath and format.")
    else: # Proceed into the loop
        print('++++++++++++++++++++++++++++++++')
        print(locations_df.head(5))
        print('++++++++++++++++++++++++++++++++')

        filename_timestamp = get_search_timestamp()

        scraped_filename = get_scraped_filename(scraped_filename, timestamp=filename_timestamp)
        stop_index = get_stop_index(stop_index, num_rows=locations_df.shape[0])

        for i in range(start_index, stop_index):
            location = locations_df.iloc[i][0]
            try: location += ", " + locations_df.iloc[i][1] # Append loc2 if it exists
            except: pass

            try:
                url, source, timestamp = get_searched_page(job_query, location, url)
                results_df = scraper.scrape_job_details(source)
            except Exception as e:
                print(e)
                print(f"\nError at index {i} (line {i+1}) in locations file.")
                print("Use the index as an arg to start batch search from this location.")
                break # Break to send to save the data.

            # Name indicates location searched + time of search.
            # Will match to URL used in URLS file and name of the sheet in workbook where job searches stored.
            search_name = get_search_sheet_name(location, timestamp)
            
            add_to_searched_urls_map(search_name=search_name, search_url=url) # Store data in dictionary

            if results_df.shape[0] != 0:
                if save_to_file:
                    # Add to map (sheet names as keys, DataFrames as values) to export to file at end:
                    add_to_dataframes_map(sheet_name=search_name, df=results_df)
                else:
                    pprint(results_df) # Pretty print the results
        
        ## Save file or at least print out the search names, URLS
        if save_to_file:
            save_dataframes_map_to_file(scraped_filename, filename_timestamp, job_query)
        else:
            print("Searches:")
            pprint(searched_urls_map)

    close_driver()
