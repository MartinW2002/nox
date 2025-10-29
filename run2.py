import lightgbm as lgb
import pandas as pd
import weather_new
import elia

# Load model
model = lgb.Booster(model_file="./out/model2.txt")

weather = weather_new.weather_data()
imbalance = elia.get_last_imbalance()

imbalance["datetime"] = pd.to_datetime(imbalance["datetime"], utc=True, errors="coerce")
weather["datetime"] = pd.to_datetime(weather["datetime"], utc=True, errors="coerce")

# Round imbalance datetime to next quarter-hour
next_quarter = imbalance["datetime"].iloc[0].ceil("15min")

# Select weather row for that timestamp
weather_row = weather[weather["datetime"] == next_quarter].iloc[0]

# Build a single-row DataFrame for prediction
new_data = pd.DataFrame([{
    "System imbalance": imbalance["systemimbalance"].iloc[0],
    "IGCC+": imbalance["igccvolumeup"].iloc[0],
    "aFRR -": imbalance["afrrvolumedown"].iloc[0],
    "aFRR +": imbalance["afrrvolumeup"].iloc[0],
    "wind_speed_10m": weather_row["wind_speed_10m"],
    "direct_radiation": weather_row["direct_radiation"],
    "hour": next_quarter.hour + next_quarter.minute / 60,
    "weekend": int(next_quarter.dayofweek in [5, 6]),
    "price_eur_mwh_dam": 0
}])

# Predict
y_pred = model.predict(new_data)
print("Predicted price (EUR/MWh):", y_pred[0])
