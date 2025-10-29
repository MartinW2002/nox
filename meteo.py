import requests
import pandas as pd

def get_current_weather(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,        # fetch current weather
        "timezone": "UTC"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    cw = data.get("current_weather", {})
    # Example fields: time, temperature, windspeed, winddirection, weathercode
    df = pd.DataFrame([{
        "datetime_utc": cw.get("time"),
        "temperature_C": cw.get("temperature"),
        "windspeed_mps": cw.get("windspeed"),
        "winddirection_deg": cw.get("winddirection"),
        "weathercode": cw.get("weathercode")
    }])
    df["datetime_utc"] = pd.to_datetime(df["datetime_utc"])
    return df

if __name__ == "__main__":
    # Coordinates for Leuven, Belgium (~50.8798 N, 4.7005 E)
    weather_df = get_current_weather(50.8798, 4.7005)
    print(weather_df)
