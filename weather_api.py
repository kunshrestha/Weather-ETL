#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
import json
import pyodbc
from os.path import exists

servername= "{Enter server name here}"


# In[12]:


def extract_weather(lat = -33.8688, # Sydney
            lon = 151.2093,
            exclude = ("hourly", "daily"),
            apikey = "*****************"
           ):
    """Extract 3 hourly weather for next 5 days using following api
    https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API key}
    
    Parameters:
    lat: float, lattitude, default -33.8688
    lon: float, longitude, default 151.2093
    exclude: tuple, do not change the dafault since free account is being used default ("hourly", "daily")
    apikey: str, key to use the API
    
    Returns requests object
    """
    url = "https://api.openweathermap.org/data/2.5/forecast?lat={0}&lon={1}&appid={2}".format(lat, lon, apikey)
    return requests.get(url)


# In[3]:


def extract_latlon(cityname = "sydney",
                  statecode = "nsw",
                  countrycode = "au",
                  limit = 1,
                  apikey = "*****************"):
    """Extract geocoding information for a place using following api
    http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key}
    
    Parameters:
    cityname: str, city name
    statecode: str, state code
    countrycode: str, country code
    limit: int, return city limit if countrycode and statecode is not set where the city name name exists more than once
    apikey: str, key to use the API
    
    Return requests object
    """

    url = "http://api.openweathermap.org/geo/1.0/direct?q={0},{1},{2}&limit={3}&appid={4}".format(cityname,
                                                                                                 statecode,
                                                                                                 countrycode,
                                                                                                 limit,
                                                                                                 apikey)
    return requests.get(url)


# In[5]:


def load_weather(data, filename, db="", db_table=""):
    """Loads dataframe 'data' into a file and database.
    If db or db_table is empty only writes the data to filename.
    
    Parameters:
    data: pandas DataFrame, dataframe to load
    filename: str, path of the csv file to save 'data' into
    db: str, name of the database
    db_table: str, name of the table
    
    Returns nothing
    """
    
    if exists(filename):
        # Checking if their is existing file with the data, concat new data with the existing one.
        
        # Haven't checked if the existing file is from different dataset.
        
        df = pd.read_csv(filename)
        
        # Use following statement if the existing data has wrong date format
        # df["dt_txt"] = [x.strftime("%m-%d-%Y %H:%M:%S") for x in pd.to_datetime(df["dt_txt"])]
        # Use following statement if the existing data has "dt" as second column
        # df = df.iloc[:,1:]
        
        data = pd.concat([df, data], ignore_index=True)
        
        # Drop duplicate entries but keep the latest row
        data = data.drop_duplicates(subset="dt", keep="last")

    data = data.set_index("dt")
    data.to_csv(filename)
    
    if db=="" or db_table=="":
        return
    
    cnxn = msconnect(driver="SQL Server Native Client 11.0",
                 server=servername,
                 database=db,
                 trusted_connection="yes")
    
    # Reset index was necessary because by default "dt" was index.
    data = data.reset_index()
    insertvalues = ""
    for i in range(len(data)):
        insertvalues = insertvalues + "('%s')," % "','".join(data.iloc[i].values.astype(str))
    sqlstmt = """INSERT INTO weather.dbo.weather_sydney
                VALUES""" + insertvalues[:-1]
    cursor = cnxn.cursor()
    
    # I don't know if truncating table everytime was the best idea.
    # Could have used something different to add only new data without
    # violating primary key.
    cursor.execute("TRUNCATE TABLE weather.dbo.weather_sydney")
    cursor.execute(sqlstmt)
    cnxn.commit()
    cnxn.close()


# In[6]:


def msconnect(driver, server, database, trusted_connection="yes"):
    """Connects to MS SQL server
    
    Parameters:
    driver: str, MS SQL server driver
    server: str, server name
    database: str, database name
    trusted_connection: str, yes/no, default "yes"
    
    Return pyodb.connect object
    """

    cnxn_str = ("""
    Driver={%s};
    Server=%s;"#",67800;
    Database=%s;
    Trusted_Connection=%s;"""%(driver,
                               server,
                               database,
                               trusted_connection))
    return pyodbc.connect(cnxn_str)


# In[7]:


def transform_weather(rawdata):
    """Transforms raw requests data 'rawdata'
    
    Parameters:
    rawdata: requests object, object of type requests
    
    Returns pandas.DataFrame
    """
    
    df = pd.json_normalize(json.loads(rawdata.text),
                          record_path=["list"],
                          meta=["cod", "message", "cnt", 
                                ["city", "id"], ["city", "name"],
                                ["city", "coord", "lat"],
                                ["city", "coord", "lon"],
                                ["city", "country"],
                                ["city", "population"],
                                ["city", "timezone"],
                                ["city", "sunrise"],
                                ["city", "sunset"]
                               ],
                           errors="ignore"
                          ).drop("weather", axis =1)
    df["dt_txt"] = [x.strftime("%m-%d-%Y %H:%M:%S") for x in pd.to_datetime(df["dt_txt"])]
    df_weather = pd.json_normalize(json.loads(rawdata.text),
                                  record_path=["list", "weather"]
                                  )
    df_weather = df_weather.rename(columns={"id": "weather.id",
                                           "main": "weather.main",
                                           "description": "weather.description",
                                           "icon": "weather.icon"}
                                  )
    return pd.concat([df, df_weather], axis=1)
    
