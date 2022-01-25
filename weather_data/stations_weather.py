def wd_station(stations, years):
    """
    

    Parameters
    ----------
    stations : List of string station name(s)
    years : List of integers

    Returns
    -------
     DataFrame of weather data from the KNMI of the requested years and stations

    """
    
    df_list = []   
    if not type(stations) == list:
        stations = [stations]
    if not type(years) == list:
        years = [years]
    
    for year in years:
        f1 = Download_data_year(year)
        
        for station in stations:         
            f = f1[f1['STN'] == STN(station)[0]]
            df_list.append(f)
         
    return pd.concat(df_list)