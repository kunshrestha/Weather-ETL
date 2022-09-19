#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
import json
# https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API key}
def extract(lat = 33.8688, # Sydney
            lon = 151.2093,
            exclude = ("hourly", "daily"),
            apikey = ""
           ):
    url = "https://api.openweathermap.org/data/2.5/forecast?lat={0}&lon={1}&appid={2}".format(lat, lon, apikey)
    return requests.get(url)


# In[2]:


def transform(jsonrequest):
    parsd = jsonrequest.json()
    
    values = []
    
    for weather_days in parsd["list"]:
        row = []
        for k, v in weather_days.items():
            if isinstance(v, list):
                v = v[0] # Grab the disctionary at 0 position
                
            if isinstance(v, dict):
                for i in v.values():
                    row.append(i)
            else:
                row.append(v)
        
        # Some rows don't have rain information, fill those values with 0 at 20 position
        if(len(row)==22): 
            row.insert(20, 0)
            
        values.append(row)
       
    columns =["dt",     
              "temp",
              "feels_like",
              "temp_min",
              "temp_max",
              "pressure",
              "sea_level",
              "grnd_level",
              "humidity",
              "temp_kf",
              "weather_id",
              "weather_main",
              "weather_description",
              "weather_icon",
              "clouds_all",
              "wind_speed",
              "wind_deg",
              "wind_gust",
              "visibility",
              "pop",
              "rain_3h",
              "sys_pod",
              "dt_txt"]
    
    df = pd.DataFrame(values, columns=columns)
    return df


# In[3]:


def load(data, filename):
    data.to_csv(filename)


# In[5]:


def main():
    weatherjson = extract()
    data = transform(weatherjson)
    load(data,"weather.csv")
    
if __name__ == "__main__":
    main()


# In[ ]:




