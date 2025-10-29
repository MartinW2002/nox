import requests
from datetime import datetime, timedelta, timezone

# -----------------------------
# CONFIG
# -----------------------------
latitude = 50.879  # Example: Leuven
longitude = 4.700
parameter = "ghi"  # Global Horizontal Irradiance, can use 'dni', 'dhi', etc.
api_user = "nox_wiesner_martin"
api_pass = "Q8XQ5ErFs16ncx8752lg"

# -----------------------------
# TIME DEFINITIONS
# -----------------------------
now = datetime.now(timezone.utc)
next_hour = now + timedelta(hours=1)
one_day_ago = now - timedelta(days=1)

# Meteomatics uses format: YYYY-MM-DDTHH:MM:SSZ
next_hour_str = next_hour.strftime("%Y-%m-%dT%H:%M:%SZ")
one_day_ago_str = one_day_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

# -----------------------------
# ENDPOINTS
# -----------------------------
# 1) Forecast for next hour
url_forecast = f"https://api.meteomatics.com/{next_hour_str}/{next_hour_str}:PT1H/{parameter}/{latitude},{longitude}/json"
print(url_forecast)
# 2) Forecast issued 24h earlier for the same hour (archive forecast)
url_forecast_24h_ago = f"https://api.meteomatics.com/{one_day_ago_str}/{one_day_ago_str}:PT1H/{parameter}/{latitude},{longitude}/json?model=forecast"

# -----------------------------
# REQUESTS
# -----------------------------
def get_data(url):
    response = requests.get(url, auth=(api_user, api_pass))
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None

forecast_next_hour = get_data(url_forecast)
forecast_24h_ago = get_data(url_forecast_24h_ago)

# -----------------------------
# OUTPUT
# -----------------------------
print("Forecast for next hour:")
print(forecast_next_hour)

print("\nForecast issued 24h ago for same hour:")
print(forecast_24h_ago)
