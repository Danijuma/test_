# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 09:37:10 2020

@author: danij
"""

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


#def wd_station_years(station, years):  
    #y1 = []    
    #for year in years:        
        #y1.append(wd_station(station,str(year)))
  
    #return pd.concat(y1)




def calc_availability(stations, years, Wavelength, Distance, LinkBudget):
    """
    

    Parameters
    ----------
    stations : TList of string station name(s)
    years : List of integers
    Wavelength : Integer
    Distance : Integer
    LinkBudget : Integer

    Returns
    -------
    df_list : Dataframe  with the avaiability for the list of provided stations in the provided years

    """
    df_list1 = []
    df_list2 = []
    
    if not type(years) == list:
        years = [years]
    if not type(stations) == list:
        stations = [stations]
        
    for year in years:       
        for station in stations:
            wd = equations(station,year,Wavelength, Distance, LinkBudget)
            if type(wd) == pd.DataFrame:
                Availability = 100-((wd['Pass/Fail'].sum()/len(wd.index))*100)
           
                df_list1.append(Availability)                
                df_list2.append('%s %i'%(station,year))
               
                print('%s %i availability = %.4f %s'%(station, year , Availability,'%'))
                    
    df_list = pd.DataFrame({'Availability':df_list1, 'Station/year':df_list2})
    return df_list
    

    
    

def availability_all_stations(year, wavelength, distance, linkbudget):
    """
    

    Parameters
    ----------
    year : Integer 
    wavelength : Integer
    distance : Integer
    linkbudget : Integer

    Returns
    -------
   Bar plot and a dataframe with the availability of all stations in the provided year.

    """
    f = pd.read_excel('Stations_names.xlsx')    
    f2 = calc_availability(list(f['NAME']) ,year, wavelength,distance,linkbudget)
    strip = str(year)
    f2['Station/year'] = f2['Station/year'].str.strip(' ' + strip)
   
        
              
    #f['Availability'] = f1
    #gd = f[f['Availability'].notna()]
    plt.figure(figsize=(20,10))
    y_pos = np.arange(len(f2['Station/year']))
    plt.barh(y_pos, f2['Availability'], align='center', alpha=0.5)
    
    plt.yticks(y_pos,f2['Station/year'])
    plt.xlabel('Availability %')
    plt.xlim(97,100,0.1)
    plt.grid(axis='x')
    plt.show()
    return f2










def monthly_availability(stations,years, Wavelength, Distance, LinkBudget):
    """
    Plots monthly availability in a bar graph for the provided years and stations

    Parameters
    ----------
    Stations : list of station in all caps
    year : Integer 
    wavelength : Integer (um)
    distance : Integer (km)
    linkbudget : Integer (dB)

    Returns
    -------
    
    """
    df_list1 = []
    df_list2 = []
    
    if not type(years) == list:
        years = [years]
    if not type(stations) == list:
        stations = [stations]
    for year in years:
        for station in stations:
            wd = equations(station,year,Wavelength, Distance, LinkBudget)    
            wd['month_year'] = wd['YYYYMMDD'].dt.to_period('M')
            
            res = wd.set_index('month_year').groupby(pd.Grouper(freq='M'))['Pass/Fail'].sum().reset_index()
            index = wd.groupby("month_year").size().values
            y1 = []
            A = (1-(res['Pass/Fail']/index))*100
            M = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            B = pd.DataFrame(A)
            B['Month'] = pd.Series(M)
            y =B['Pass/Fail']
            x = B['Month']
            plt.figure(figsize=(20,10))
            x_pos = np.arange(len(B['Month']))
            plt.bar(x_pos, y, align='center', alpha=0.5)
        
            plt.xticks(x_pos,B['Month'])
            plt.ylabel('Availability %')
            plt.ylim(90,100,0.1)
            plt.grid(axis='y')
            for index,data in enumerate(y):
                    plt.text(x=index , y =data-0.2 , s='%.4f %s'%(data,'%') , fontdict=dict(fontsize=12), horizontalalignment='center')
            y2 = str(year)
            plt.title(station + ' ' + y2)  
            plt.show()
            
            
    

    


def daily_availability(stations,years, Wavelength, Distance, LinkBudget):
    """    
    Plots monthly availability in a bar graph for the provided years and stations
    
    Parameters
    ----------
    stations : List of stations in all caps
    years : list of integers
    Wavelength : Integers (um)
    Distance : Integers (km)
    LinkBudget : Integers (dB)

    Returns
    -------
   

    """
    
    if not type(years) == list:
        years = [years]
    if not type(stations) == list:
        stations = [stations]
    for year in years:
        for station in stations:
            wd = equations(station,year,Wavelength, Distance, LinkBudget)   

        
            
            res = wd.groupby(['YYYYMMDD'])['Pass/Fail'].sum()
            res_df = pd.DataFrame(res)
            index = wd.groupby("YYYYMMDD").size().values
            y1 = []
            A = (1-(res_df['Pass/Fail']/index))*100
            B = pd.DataFrame(A)
            a = wd.drop_duplicates(subset="YYYYMMDD")
            #B['Date'] = J
            #plt.figure()
            B.plot(figsize=(20,10),legend=None)
            plt.ylabel('Avialability %')
            plt.xlabel('')
            plt.grid()
            plt.title(station + str(year))
            plt.show()
            
    
def equations(station,year,Wavelength, Distance, LinkBudget):
    """
    Eauations to caclculate the attenuation due to weather conditions and check for Pass/fail

    Parameters
    ----------
    Stations : list of station in all caps
    year : Integer 
    wavelength : Integer (um)
    distance : Integer (km)
    linkbudget : Integer (dB)

    Returns
    -------
    wd : weather data frame with the pass/fail column

    """
    wd = wd_station(station, year)
    wd.reset_index(drop= True, inplace= True)
    F = pd.isnull(wd['VV']).all()
    if F ==False:
        wd = wd[wd['VV'].notna()]
        wd['YYYYMMDD'] = pd.to_datetime(wd['YYYYMMDD'], format='%Y%m%d')
        Threshold = LinkBudget * Distance
    
                #add a column with converted visibility
        wd.loc[wd['VV'] > 80, 'Visibility'] = (wd['VV'] * 5)-370
        wd.loc[wd['VV'] <= 80, 'Visibility'] = wd['VV'] - 50
        wd.loc[wd['VV'] <= 50, 'Visibility'] = wd['VV']* 0.1
        wd.loc[wd['VV'] == 0, 'Visibility'] = 0.1
        
                #Kim model coefficient
        wd.loc[wd['Visibility'] > 50, 'q'] = 1.6
        wd.loc[wd['Visibility'] < 50, 'q'] = 1.3
        wd.loc[wd['Visibility'] < 6, 'q'] = (0.16 * wd['Visibility']) + 0.34
        wd.loc[wd['Visibility'] < 1, 'q'] = wd['Visibility'] -  0.5
        wd.loc[wd['Visibility'] < 0.5, 'q'] = 0
        
                #specific attenuation Fog [dB/km]
        wd.loc[wd['Visibility'] == wd['Visibility'] , 'Att'] = (13/wd['Visibility'])*((Wavelength/550)**(-wd['q']))
        
              
        
                #Converting RH to precipitation
        wd.loc[wd['RH'] == -1, 'Prec'] = 0.05
        wd.loc[wd['RH'] > 0, 'Prec'] = wd['RH']* 0.1
        wd.loc[wd['RH'] == wd['RH'], 'Rain/snow Att']= 1.076*(wd['Prec']**0.67) #if no R and S is available
        wd.loc[wd['R'] == 1, 'Rain/snow Att']= 1.076*(wd['Prec']**0.67)# Rain only
        wd.loc[(wd['S'] == 1) & (wd['R'] == 0), 'Rain/snow Att']= (5.49+(54200*Wavelength*(10**-9)))*(wd['Prec']**1.38)# dry snow
        wd.loc[(wd['S'] == 1) & (wd['R'] == 1), 'Rain/snow Att']= (3.78+(103200*Wavelength*(10**-9)))*(wd['Prec']**0.72)# wet snow
        wd.loc[wd['Rain/snow Att'] > wd['Att'], 'Att'] = wd['Rain/snow Att']
                  #Pass/Fail
        wd.loc[wd['Att'] >= Threshold, 'Pass/Fail'] = 1
        wd.loc[wd['Att'] <= Threshold, 'Pass/Fail'] = 0
        
        return wd
def Linkbudget(stations,years,wavelength,distance,L):  
    """
    Daily plot with different provided linkbudgets

    Parameters
    ----------
    stations : List of station in all caps
    years : list of integers
    wavelength : integer (um)
    distance : integer (km)
    L : integer (dB)

    Returns
    -------
    None.

    """
    if not type(years) == list:
        years = [years]
    if not type(stations) == list:
        stations = [stations]
    if not type(L) == list:
        L = [L]   
    
    for year in years:
        for station in stations:
            plt.figure()
            for LinkBudget in L:
                wd = equations(station,year,wavelength, distance, LinkBudget)   
                LB = str(LinkBudget)
                res = wd.groupby(['YYYYMMDD'])['Pass/Fail'].sum()
                res_df = pd.DataFrame(res)
                index = wd.groupby("YYYYMMDD").size().values
                y1 = []
                A = (1-(res_df['Pass/Fail']/index))*100
                B = pd.DataFrame(A)
                a = wd.drop_duplicates(subset="YYYYMMDD")
                #B['Date'] = J
                #plt.figure()
                plt.plot(B,label=LB)
                plt.ylabel('Avialability %')
                plt.xlabel('')
                
                
                plt.yticks(np.arange(0, 100, 5))
                plt.legend(loc="upper left")
                plt.grid(True)
                plt.title(station +' ' + str(year))
                plt.show()

if __name__ == '__main__':
    
      #Linkbudget(['EINDHOVEN'],[2019],1550,1,[20,40])
      monthly_availability('SCHIPHOL', 2020, 1550, 1, 25)
