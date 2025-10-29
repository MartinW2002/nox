import requests
import pandas as pd

# Location (example: Leuven, Belgium)
latitude = 50.8792
longitude = 4.7012

# Time range
start_date = "2024-05-01"
end_date = "2025-10-29"

# Open-Meteo API endpoint
# url = "https://archive-api.open-meteo.com/v1/archive"
url = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": end_date,
    "end_date": end_date,
    "minutely_15": "wind_speed_10m,direct_radiation",
    # "timezone": "Europe/Brussels",
}

def weather_data():
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame({
        "datetime": data["minutely_15"]["time"],
        "wind_speed_10m": data["minutely_15"]["wind_speed_10m"],
        "direct_radiation": data["minutely_15"]["direct_radiation"]
    })

    # Convert datetime column to actual datetime objects
    df["datetime"] = pd.to_datetime(df["datetime"])

    # Optionally set datetime as index
    # df = df.set_index("datetime")
    return df