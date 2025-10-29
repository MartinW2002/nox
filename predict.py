import lightgbm as lgb
import pandas as pd
import weather_new
import elia
import datetime

"""
Predict price for a given time (quarter aligned)
"""
def predict(model_file:str, date: datetime) -> float:
    # Load model
    model = lgb.Booster(model_file=model_file)

    weather = weather_new.weather_data()
    imbalance = elia.get_last_imbalance(date)

    imbalance["datetime"] = pd.to_datetime(imbalance["datetime"], utc=True, errors="coerce")
    weather["datetime"] = pd.to_datetime(weather["datetime"], utc=True, errors="coerce")


    # Select weather row for that timestamp
    weather_row = weather[weather["datetime"] == date].iloc[0]

    prices = pd.read_csv("./input/day_ahead_29-10.csv", sep=";")  # adjust path if needed
    prices["price"] = prices["price"].str.replace(",", ".").astype(float)

    price_eur_mwh_dam = elia.get_day_ahead(date.isoformat())

    wind = elia.get_total_wind(date.isoformat())
    solar = elia.get_total_solar(date.isoformat())

    # Build a single-row DataFrame for prediction
    new_data = pd.DataFrame([{
        "System imbalance": imbalance["systemimbalance"].iloc[0],
        "IGCC+": imbalance["igccvolumeup"].iloc[0],
        "IGCC-": imbalance["igccvolumedown"].iloc[0],
        "aFRR -": imbalance["afrrvolumedown"].iloc[0],
        "aFRR +": imbalance["afrrvolumeup"].iloc[0],
        "wind_speed_10m": weather_row["wind_speed_10m"],
        "direct_radiation": weather_row["direct_radiation"],
        "hour": date.hour + date.minute / 60,
        "weekend": int(date.weekday() in [5, 6]),
        "price_eur_mwh_dam": price_eur_mwh_dam,
        "measured_wind": wind["realtime"].iloc[0],
        "most_recent_wind": wind["mostrecentforecast"].iloc[0],
        "day_ahead_wind": wind["dayaheadforecast"].iloc[0],
        "measured_solar": solar["realtime"].iloc[0],
        "most_recent_solar": solar["mostrecentforecast"].iloc[0],
        "day_ahead_solar": solar["realtime"].iloc[0],
    }])

    # Predict
    y_pred = model.predict(new_data)
    return y_pred[0]
