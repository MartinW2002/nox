import requests
import pandas as pd

# Location (example: Leuven, Belgium)
latitude = 50.8792
longitude = 4.7012

# Time range
start_date = "2024-05-21"
end_date = "2025-10-20"

# Open-Meteo API endpoint
url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": end_date,
    "end_date": end_date,
    "hourly": "wind_speed_10m,direct_radiation",
    # "timezone": "Europe/Brussels",
}

def weather_data():

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame({
        "datetime": data["hourly"]["time"],
        "wind_speed_10m": data["hourly"]["wind_speed_10m"],
        "direct_radiation": data["hourly"]["direct_radiation"]
    })

    # Convert datetime column to actual datetime objects
    df["datetime"] = pd.to_datetime(df["datetime"])

    # Optionally set datetime as index
    # df = df.set_index("datetime")
    # df = df.resample("15min").interpolate()
    df = df.set_index("datetime").resample("15min").interpolate().reset_index()

    return df