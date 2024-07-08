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
        print(post)
        data = {
            "job_title": post.find('span', id=lambda x: x and x.startswith('jobTitle')).text,
            "company": post.find('span', class_='css-63koeb').text,
            "location": post.find('div', class_='css-1p0sjhy').text,
            "posted_date":  post.find('span', attrs={'data-testid': 'myJobsStateDate'}).text,
            "job_description": post.find('div', class_='css-9446fg').text
        }

        try: data["rating"] = post.find('span', attrs={'data-testid': 'holistic-rating'}).text
        except: data["rating"] = 0
        jobs_list.append(data)

    df = pd.DataFrame(jobs_list)
    if 'rating' in df.columns:
        convert_columns_data_type(df, ['rating'], np.float32) # Convert rating to float

    return df