import pandas as pd


locations_df = pd.DataFrame(columns=['loc1', 'loc2'])
locations_df.index.rename('ID', inplace=True)


def clear_locations():
    locations_df.drop(locations_df.index, inplace=True)
    return True


def load_locations_from_CSV(file):
    try:
        global locations_df
        locations_df =  pd.read_csv(file)
        return True, locations_df
    except:
        return False, pd.DataFrame()


def export_single_dataframe_to_excel(df, url, filename, sheet_name):
    df['URL'] = url
    with pd.ExcelWriter(
        filename,
        engine="xlsxwriter",
        engine_kwargs={"options": {"nan_inf_to_errors": True}}
    ) as writer:
        df.to_excel(writer, sheet_name=sheet_name)


def export_bulk_dataframes_to_excel(dataframes_map, filename):
    with pd.ExcelWriter(
        filename,
        engine="xlsxwriter",
        engine_kwargs={"options": {"nan_inf_to_errors": True}}
    ) as writer:
        for sheet_name, df in dataframes_map.items():
            df.to_excel(writer, sheet_name=sheet_name)


def export_search_urls_to_excel(searched_urls_map, filename, search_query):
    searched_urls_df = pd.DataFrame(columns=['Location Name', 'Search Query', 'Timestamp', 'URL'])
    search_names = []
    timestamps   = []
    for name in searched_urls_map.keys():
        s = name.split('_')
        search_names.append(s[0]); timestamps.append(s[1])

    searched_urls_df['Location Name'] = search_names
    searched_urls_df['Search Query'] = search_query
    searched_urls_df['Timestamp'] = timestamps
    searched_urls_df['URL'] = searched_urls_map.values()

    with pd.ExcelWriter(filename) as writer:
        searched_urls_df.to_excel(writer, sheet_name='searches')