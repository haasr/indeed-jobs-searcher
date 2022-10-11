from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def convert_columns_data_type(df, cols, datatype):
    for col in cols:
        df[col] = df[col].astype(datatype)


def scrape_job_details(page_source):
    content = BeautifulSoup(page_source, 'lxml')
   
    jobs_list = []    
    for post in content.select('.job_seen_beacon'):
        try:
            data = {
                "job_title":post.select('.jobTitle')[0].get_text().strip(),
                "company":post.select('.companyName')[0].get_text().strip(),
                "rating":post.select('.ratingNumber')[0].get_text().strip(),
                "location":post.select('.companyLocation')[0].get_text().strip(),
                "date":post.select('.date')[0].get_text().strip(),
                "job_desc":post.select('.job-snippet')[0].get_text().strip()
            }
        except IndexError:
            continue          
        jobs_list.append(data)
    df = pd.DataFrame(jobs_list)
    convert_columns_data_type(df, ['rating'], np.float32) # Convert rating to float

    return df