import openmeteo_requests
from sqlalchemy import create_engine
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime
from dateutil.relativedelta import relativedelta


class LocationData:

    def __init__(self, latV, longV, currentDate, startDate):
        
        # Initialises the variables of interest
        self.latV = latV
        self.longV = longV
        self.currentDate = currentDate
        self.startDate = startDate

        # Creates an engine which connects to our local database, we are using a local database to store 
        engine = create_engine("mysql+mysqlconnector://root:password1@localhost/stations")
        connection = engine.connect()


    def generateData(self,latV,longV,end,start):

        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        openmeteo = openmeteo_requests.Client(session = retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://customer-api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latV,
            "longitude": longV,
            "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "precipitation_probability", "cloud_cover", "wind_speed_10m", "shortwave_radiation_instant"],
            "daily": "daylight_duration",
            "start_date": start, 
            "end_date": end,
            "apikey": "cT6q5PVYRUhaDb4A"
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        """
        print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
        """
        
        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_dew_point_2m = hourly.Variables(2).ValuesAsNumpy()
        hourly_precipitation_probability = hourly.Variables(3).ValuesAsNumpy()
        hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(5).ValuesAsNumpy()
        hourly_shortwave_radiation_instant = hourly.Variables(6).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s"),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["dew_point_2m"] = hourly_dew_point_2m
        hourly_data["precipitation_probability"] = hourly_precipitation_probability
        hourly_data["cloud_cover"] = hourly_cloud_cover
        hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
        hourly_data["shortwave_radiation_instant"] = hourly_shortwave_radiation_instant

        hourly_dataframe = pd.DataFrame(data = hourly_data)

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_daylight_duration = daily.Variables(0).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}
        daily_data["daylight_duration"] = daily_daylight_duration

        # Sets the index of the hourly and daily dataframes as the date of the reading
        daily_dataframe = pd.DataFrame(data = daily_data)
        daily_dataframe.set_index('date', inplace=True)
        daily_dataframe.index = daily_dataframe.index.strftime('%Y-%m-%d')
        daily_dataframe.index = pd.to_datetime(daily_dataframe.index)
        hourly_dataframe.set_index('date', inplace=True)

        # Finds the daily averages for the hourly weather variables
        final_dataframe = hourly_dataframe.resample('D').mean()
        final_dataframe.index = final_dataframe.index.dayofyear

        print(final_dataframe)


        return final_dataframe

    def getSunData(self,latV,longV,currentDate,startDate):

        # Creates an engine which connects to our local database, we are using a local database to store 
        engine = create_engine("mysql+mysqlconnector://root:password1@localhost/stations")
        connection = engine.connect()
        
        # Calls the generateData method to produce the dataframe for the location of interest
        final_dataframe = self.generateData(latV,longV,currentDate,startDate)

        # Uploads the dataframe to the local database
        try:
            final_dataframe.to_sql("("+str(latV)+"),("+str(longV)+")", connection) 
        except:
            print("These coordinates have already been mapped")
        
        """
        # Generates the dataframe for the next 7 days
        currentDatetime = datetime.strptime(currentDate, '%Y-%m-%d')
        forcastLim = currentDatetime + relativedelta(days=7)
        forcastLim = str(forcastLim.strftime('%Y-%m-%d'))
        forcastData = self.generateData(latV,longV,forcastLim,currentDate)
        """
        
        forcastData = self.getPredictions(latV,longV,currentDate,startDate)

        return forcastData
    
    def getPredictions(self,latV,longV,currentDate,startDate):

        # Generates the dataframe for the next 7 days
        currentDatetime = datetime.strptime(currentDate, '%Y-%m-%d')
        forcastLim = currentDatetime + relativedelta(days=7)
        forcastLim = str(forcastLim.strftime('%Y-%m-%d'))
        forcastData = self.generateData(latV,longV,forcastLim,currentDate)

        return forcastData