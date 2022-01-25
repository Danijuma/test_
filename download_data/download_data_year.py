import pandas as pd
import requests
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import datetime
from Models import *

# -*- coding: utf-8 -*-









def Download_data_year(years):
    """
    

    Parameters
    ----------
    years : List of integers.

    Returns
    -------
    DataFrame of weather data from the KNMI of the requested years

    """
    df_list = []
    
    # Puts the argument in a list
    if not type(years) == list:
        years = [years]
    
    # Downloads the data for each year and saves them to the file path    
    for year in years:
        year = str(year)
        file = Path('WD_' + year + '.csv')
        if not file.exists():
            r = requests.get('http://projects.knmi.nl/klimatologie/uurgegevens/getdata_uur.cgi?vars=VICL:PRCP:WEER&byear=' + year +'&bmonth=1&bday=1&eyear=' + year + '&emonth=12&eday=31')
            output = open('WD_'+ year + '.csv', 'wb')
            output.write(r.content)
            output.close()
        
        # Cleans the file and appends all the years requested in 1 dataframe
        f = pd.read_csv('WD_' + year + '.csv', skiprows=71, skipinitialspace=(True))
        f = f.drop([0,0])
        f = pd.DataFrame(f.rename(columns=lambda x:x.strip('# ')))
        f = f.apply(pd.to_numeric, errors='ignore')                
        df_list.append(f)
        return pd.concat(df_list)