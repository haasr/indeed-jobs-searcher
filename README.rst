********************
indeed-jobs-searcher
********************

Simple CLI-based tool for extracting and storing relevant job info. from bulk job searches on indeed.com.

It would be remiss of me if I didn't say that I used Sidharth's project (explained here: https://www.pycodemates.com/2022/01/Indeed-jobs-scraping-with-python-bs4-selenium-and-pandas.html)
as the base of this job searcher. Running Sidharth's code showed me a workable proof of concept (after tweaking the code) for extracting
and storing useful job information from Indeed, using Selenium and BeautifulSoup -- neither one of which I have much experience.

From there I scaled up for my needs. I am using my data analytics skills to compile a list of top cities where I wish to live and work
after I graduate (based on a number of factors: different measures of diversity, cost of living, proximity to friends and family, etc.).
Part of my analysis is figuring out which of my prospective cities has the jobs I'm looking for. Hence this project was born. I derive a
CSV file of cities by printing out a dataframe from my analysis and then I plug it into my jobs searcher to capture available jobs for
each location into an Excel workbook which I can import with `pandas` for the next phase in my analysis.

As a current Natural Language Processing (NLP) student, I am interested in ameliorating the usefulness of this program by using sentiment
analysis and classification (perhaps via a neural net) to help gague the viability of jobs per location. Unfortunately that will probably
happen in the distant future as I barely have sufficient time to write this readme file.

.. image:: ./readme_images/job-search-showcase.png
    :width: 800
    :alt: Showcase screenshots of command-line interface and results


A Note for the Instructions
###########################

My examples use the command `python3` which is specific to Linux. If you are using Windows, simply use `python` instead.


Requirements
############

- Device with Internet access and Chrome browser installed
- Python 3.10.6 on device

Setup
#####

Setup virtualenv
----------------

For this project, we want to first set up a virtual environment. This way, we can install
dependencies to this virtual environment rather than our global Python environment. This
will allows us to isolate our dependencies.

1. First, open your terminal to the main folder of this cloned repository and make sure you
have the virtualenv package installed:

``pip install --user virtualenv``

In Ubuntu-based distributions, you can install it using:

``sudo apt install python3-venv``

2. Create the virtualenv (still in the main repo folder):

``python3 -m venv venv``

3. Activate it.

3a. In PowerShell:

``\venv\Scripts\activate``

3b. In Linux:

``source venv/bin/activate```

To deactivate it (when you want to use your user Python environment), simply type
``deactivate``.

4. Install the requirements.

``pip install -r requirements.txt``

(You will have to use ``pip3`` in Linux)


Usage
#####

For Bulk Searching
------------------
For bulk searching, you will need to feed in a CSV file of your locations. The CSV file format is specific:

1. The first (leftmost) column should be labeled as "ID".
2. The second column from the left must contain a location name.
3. The third column from the left may be used to specify a more general region (e.g., state, providence) or it may be left blank.

Refer to the following image as a reference:

.. image:: ./readme_images/location-file-example.png
    :width: 250
    :alt: Screenshot of example CSV location file

Execute!
--------

Refer to the `help menu` depicted below by running `python3 jobsearch.py -h`.

.. code-block::

    Usage (help):              jobsearch.py -h, jobsearch.py --help

    Usage (single search):     jobsearch.py -l "<location name>" [options]
    Options:
        -u, --url <Indeed URL> Taylor URL to country.
        -s, --save <boolean>   True if unspecified. False if false value is given.     

    Usage (batch search):      jobsearch.py -c <locations CSV file> [options]
    Options:
        -u, --url <Indeed URL> Taylor URL to country.
        -s, --save <boolean>   True if unspecified. False if false value is given.     
        --startindex <int>     0-based row index in CSV file to start from (inclusive).
        --stopindex  <int>     0-based row index in CSV file to stop after (inclusive).

    Examples (single search):
    jobsearch.py -l "Johnson City, TN"
    jobsearch.py -l "Tokyo" -u https://jp.indeed.com
    jobsearch.py -l "Bengaluru" -u https://in.indeed.com --save false

    Examples (batch search):
    jobsearch.py -c locations/southeast-cities.csv
    jobsearch.py -c locations/indian-cities.csv -u https://in.indeed.com
    jobsearch.py -c locations/southeast-cities.csv --startindex 10
    jobsearch.py -c locations/southeast-cities.csv --stopindex 10
    jobsearch.py -c locations/southeast-cities.csv --startindex 10 --stopindex 20

    Locations CSV file format
    Each row can have one or two locations (e.g. city or city, region) but no more.
    The first location column should be the second column from the left. The leftmost
    column should be titled as ID.

    The first row may be used as the column names.

    Example file format:
        ID  City        State
        50  Birmingham  AL
        46  Richmond    KY
        38  Georgetown  KY
        36  Greenville  NC

Saved Files
###########
All files are saved in the job_searches folder. For more information, refer to the **Bulk Search Example** below.


Bulk Search Example
###################

Understanding `startindex`, `stopindex`
---------------------------------------

Assume we execute the script as such:

.. code:: bash

    python3 jobsearch.py -c ./locations/indeed_job_search_locations.csv --startindex 1 --stopindex 3

Next we enter our job query. You can use boolean logic if you'd like:

.. code::

    Enter your query >>"mechanical" and "engineer" and not "electrical"

The indexing is zero-based (as a programmer, it's the only way for me!). What that means is that the second, third, and fourth
locations in the file will be searched (the `stopindex` is inclusive):

*locations/indeed_job_search_locations.csv*

.. code-block::

    ID	City		State
    451	Raleigh		NC  <-- Index 0
    445	Nashville	TN  <-- Index 1 (start here)
    442	Norfolk		VA
    438	Hampton		VA  <-- Index 3 (stop after scraping for this location)
    420	Murfreesboro	TN
    . . .


The Results
-----------

The results are stored in the `searched_jobs` folder. The first part of each file name (before the underscore) is a timestamp
of when the data was scraped.

The scraped job-search data are stored in the Excel workbook with `bulk-job-searches.xlsx` in its name. Each sheet in the workbook
features the results for each location searched from the locations CSV file.

.. image:: ./readme_images/job-search-results.png
    :width: 620
    :alt: Screenshot of scraped job search data in Excel worksheet


The locations searched, the entered job query, and the resulting URLs from which the results were scraped are stored in the Excel
workbook with `bulk-urls-searched.xlsx` in its name.

.. image:: ./readme_images/url-search-results.png
    :width: 620
    :alt: Screenshot of locations searched, entered job query, and the resulting URLs in Excel worksheet


Single Searches
################

Single searches produce a similar Excel workbook file except a URL column lists the URL from which the results were scraped
in the same file for convenience.

NOTE: It is important that when you perform a single search, if your location is more than one word, it is enclosed in
quotation marks, e.g.,

.. code:: bash

    python3 jobsearch.py -l "Johnson City, TN"

