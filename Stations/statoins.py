def STN( stations ):
    """
    

    Parameters
    ----------
    Station : list of station name(s) as string in all caps

    Returns
    -------
    Station number(s) in a list as int64.

    """
    df_list = []
    if not type(stations) == list:
        stations = [stations]
    for station in stations:
        df = pd.read_excel('Stations_names.xlsx')
        r = df[df['NAME'] == station].index[0]
        df_list.append(df.iloc[r,1])
       
    return df_list