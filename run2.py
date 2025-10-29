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

prices = pd.read_csv("./input/day_ahead_29-10.csv", sep=";")  # adjust path if needed
prices["price"] = prices["price"].str.replace(",", ".").astype(float)

price_eur_mwh_dam = elia.get_day_ahead(elia.next_quarter_iso())

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
    "price_eur_mwh_dam": price_eur_mwh_dam
}])

# Predict
y_pred = model.predict(new_data)
print("Predicted price (EUR/MWh):", y_pred[0])
