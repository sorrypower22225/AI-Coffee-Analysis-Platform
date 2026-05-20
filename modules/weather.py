import requests
import pandas as pd

# =========================
# 即時天氣
# wttr.in API
# =========================

def get_current_weather(city='New York'):

    url = f'https://wttr.in/{city}?format=j1'

    response = requests.get(url)

    data = response.json()

    current = data['current_condition'][0]

    weather = {

        'city': city,

        'temp_C': current['temp_C'],

        'humidity': current['humidity'],

        'weather': current['weatherDesc'][0]['value'],

        'wind_kph': current['windspeedKmph']
    }

    return weather

# =========================
# 歷史天氣
# Open-Meteo API
# =========================

def get_historical_weather():

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        "?latitude=40.71"
        "&longitude=-74.01"
        "&start_date=2023-01-01"
        "&end_date=2023-12-31"
        "&daily=temperature_2m_mean,precipitation_sum"
        "&timezone=America/New_York"
    )

    response = requests.get(url)

    data = response.json()

    weather_df = pd.DataFrame({

        'date': data['daily']['time'],

        'temperature_mean': data['daily']['temperature_2m_mean'],

        'rainfall': data['daily']['precipitation_sum']
    })

    return weather_df