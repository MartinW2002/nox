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

currentDt = imbalance["datetime"].dt.ceil("15min")

weather = weather[weather["datetime"].isin(currentDt)]
print(weather)
print(imbalance)
new_data = pd.DataFrame({
    "System imbalance": imbalance["systemimbalance"],
    "IGCC+": imbalance["igccvolumeup"],
    "aFRR -": imbalance["afrrvolumedown"],
    "aFRR +": imbalance["afrrvolumeup"],
    "wind_speed_10m": weather["wind_speed_10m"],
    "direct_radiation": weather["direct_radiation"],
    "hour": [16],
    "weekend": [0],
    "price_eur_mwh_dam": [0]
})

# Predict
y_pred = model.predict(new_data)
print("Predicted price (EUR/MWh):", y_pred[0])