from lib import searcher
import sys


colors = {
    'cyan':    "\033[36m",
    'green':   "\033[1;32;40m",
    'magenta': "\033[35m",
    'white':   "\033[1;37;40m",
    'yellow':  "\033[33m"
}


def print_usage():
    print(
        f"{colors['green']}Usage (help):              jobsearch.py -h, jobsearch.py --help{colors['white']}"
        f"\n\n{colors['green']}Usage (single search):     jobsearch.py -l \"<location name>\" {colors['yellow']}[options]{colors['white']}"
        f"\n  {colors['yellow']}Options:{colors['white']}"
        f"\n    {colors['yellow']}-f{colors['white']}, {colors['yellow']}--file {colors['cyan']}<file name>{colors['white']} Custom file name (can include path)."
        f"\n    {colors['yellow']}-u{colors['white']}, {colors['yellow']}--url {colors['cyan']}<Indeed URL>{colors['white']} Tailor URL to country."
        f"\n    {colors['yellow']}-s{colors['white']}, {colors['yellow']}--save {colors['cyan']}<boolean>{colors['white']}   True if unspecified. False if false value is given."
        
        f"\n\n{colors['green']}Usage (batch search):      jobsearch.py -c <locations CSV file> {colors['yellow']}[options]{colors['white']}"
        f"\n  {colors['yellow']}Options:{colors['white']}"
        f"\n    {colors['yellow']}-f{colors['white']}, {colors['yellow']}--file {colors['cyan']}<file name>{colors['white']} Custom file name (can include path)."
        f"\n    {colors['yellow']}-u{colors['white']}, {colors['yellow']}--url {colors['cyan']}<Indeed URL>{colors['white']} Tailor URL to country."
        f"\n    {colors['yellow']}-s{colors['white']}, {colors['yellow']}--save {colors['cyan']}<boolean>{colors['white']}   True if unspecified. False if false value is given."
        f"\n    {colors['yellow']}--startindex {colors['cyan']}<int>{colors['white']}     0-based row index in CSV file to start from (inclusive)."
        f"\n    {colors['yellow']}--stopindex  {colors['cyan']}<int>{colors['white']}     0-based row index in CSV file to stop after (inclusive)."

        f"\n\n{colors['magenta']}Examples (single search):{colors['white']}"
        f"\n  jobsearch.py -l \"Johnson City, TN\""
        f"\n  jobsearch.py -l \"Tokyo\" -u https://jp.indeed.com"
        f"\n  jobsearch.py -l \"Tokyo\" -u https://jp.indeed.com -f \"C:\\Users\\User\\Desktop\\ty-job-search\""
        f"\n  jobsearch.py -l \"Tokyo\" -u https://jp.indeed.com -f /home/user/Desktop/ty-job-search"
        f"\n  jobsearch.py -l \"Bengaluru\" -u https://in.indeed.com --save false"

        f"\n\n{colors['magenta']}Examples (batch search):{colors['white']}"
        f"\n  jobsearch.py -c locations/southeast-cities.csv"
        f"\n  jobsearch.py -c locations/southeast-cities.csv -f \"C:\\Users\\User\\Desktop\\SE-jobs-search\""
        f"\n  jobsearch.py -c locations/southeast-cities.csv -f /home/user/Desktop/SE-jobs-search"
        f"\n  jobsearch.py -c locations/indian-cities.csv -u https://in.indeed.com"
        f"\n  jobsearch.py -c locations/southeast-cities.csv --startindex 10"
        f"\n  jobsearch.py -c locations/southeast-cities.csv --stopindex 10"
        f"\n  jobsearch.py -c locations/southeast-cities.csv --startindex 10 --stopindex 20"
        f"\n\n{colors['magenta']}Locations CSV file format{colors['white']}"
        f"\n  Each row can have one or two locations (e.g. city or city, region) but no more."
        f"\n  The first location column should be the second column from the left. {colors['magenta']}The leftmost"
        f"\n  column should be titled as ID.{colors['white']}"
        
        f"\n\n  The first row may be used as the column names."
        
        f"\n\n  Example file format:"
        f"\n    ID	City        State"
        f"\n    50	Birmingham  AL"
        f"\n    46	Richmond    KY"
        f"\n    38	Georgetown  KY"
        f"\n    36	Greenville  NC"
        f"\n\n{colors['magenta']}Saved Files{colors['white']}"
        f"\n  If no file path is specificied (using the -f argument)"
        f"\n  the resulting files are saved in the {colors['cyan']}searched_jobs{colors['white']} folder."
    )
    exit(0)


def main():
    location = "Johnson City, TN"
    url = 'https://indeed.com/'
    filename = None
    single_search = True # Assumed true if CSV locations file not passed
    save_file = True # True by default. Only false if explictly declared false
    start_index = 0
    stop_index = None

    args = sys.argv[1:]
    if len(args) < 2:
        print_usage()

    for i in range((len(args) - 1), -1, -1):
        if args[i] == '-l' or args[i] == '--location':
            location = args[i+1]
            single_search = True
        elif args[i] == '-u' or args[i] == '--url':
            url = args[i+1]
        elif args[i] == '-c' or args[i] == '--csvfile':
            csvfile = args[i+1]
            single_search = False
        elif args[i] == '-f' or args[i] == '--filename': # Custom filename
            filename = args[i+1]
        elif args[i] == '-s' or args[i] == '--save':
            if args[i+1].lower() == 'false':
                save_file = False
        elif args[i] == '--startindex':
            start_index = int(args[i+1])
        elif args[i] == '--stopindex':
            stop_index = int(args[i+1])
        elif args[i].isnumeric():
            continue # Probably a startindex or stopindex arg which will get parsed in next iteration

    job_query = input("\nEnter your query >>")

    ## Commence search:

    searcher.init_driver()
    print(f"\nURL:        {url}"
          f"\nQuery:      {job_query}")

    if single_search:
        print(f"Location:   {location}"
              f"\n\n> Commencing single search...")
        searcher.single_search(location, job_query, url, save_to_file=save_file,
                                scraped_filename=filename)
    else:
        print(f"Locations:  {csvfile}"
              f"\n\n> Commencing bulk search...")
        searcher.batch_search(
            csvfile, job_query, url, start_index=start_index, stop_index=stop_index,
            save_to_file=save_file, scraped_filename=filename
        )

main()