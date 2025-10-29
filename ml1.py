import pandas as pd
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
import numpy as np

# === 1. Load data ===
dam = pd.read_csv("data/dam_prices.csv", parse_dates=["datetime_utc"])
imb_fc = pd.read_csv("data/imbalance_forecast.csv", parse_dates=["datetime_utc"])
imb_act = pd.read_csv("data/imbalance_actual.csv", parse_dates=["datetime_utc"])

# === 2. Merge datasets on datetime_utc ===
df = imb_act.merge(imb_fc, on="datetime_utc", how="left", suffixes=("_act", "_fc"))
df = df.merge(dam, on="datetime_utc", how="left")
df = df.sort_values("datetime_utc").reset_index(drop=True)

# === 3. Feature engineering ===
df["hour"] = df["datetime_utc"].dt.hour
df["dayofweek"] = df["datetime_utc"].dt.dayofweek

# Lag features (previous imbalance prices)
for lag in [1, 2, 3, 4]:
    df[f"lag_{lag}"] = df["price_eur_mwh_act"].shift(lag)

# Rolling averages
df["roll_mean_4"] = df["price_eur_mwh_act"].rolling(4).mean()
df["roll_std_4"] = df["price_eur_mwh_act"].rolling(4).std()

# Drop NaNs caused by shifting
df = df.dropna().reset_index(drop=True)

# === 4. Prepare data ===
target = "price_eur_mwh_act"
features = [c for c in df.columns if c not in ["datetime_utc", target]]

X = df[features]
y = df[target]

# chronological split (last 1 day for validation)
split_time = df["datetime_utc"].max() - pd.Timedelta(days=1)
X_train = X[df["datetime_utc"] < split_time]
y_train = y[df["datetime_utc"] < split_time]
X_val = X[df["datetime_utc"] >= split_time]
y_val = y[df["datetime_utc"] >= split_time]

# === 5. Train model ===
model = lgb.LGBMRegressor(
    n_estimators=500,
    learning_rate=0.03,
    num_leaves=64,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train, y_train)

# === 6. Evaluate ===
preds_val = model.predict(X_val)
mae = mean_absolute_error(y_val, preds_val)
print(f"Validation MAE: {mae:.2f} EUR/MWh")

# === 7. Predict next 4 steps (example for 15-min intervals) ===
latest = df.iloc[-1:].copy()
future = []

for i in range(4):
    next_time = latest["datetime_utc"].iloc[-1] + pd.Timedelta(minutes=15)
    sample = latest[features].iloc[-1:].copy()
    y_pred = model.predict(sample)[0]

    future.append({"datetime_utc": next_time, "price_eur_mwh": y_pred})

    # shift latest row for next step
    latest = pd.concat([latest, pd.DataFrame({
        "datetime_utc": [next_time],
        "price_eur_mwh_act": [y_pred]
    })], ignore_index=True)
    for lag in [1, 2, 3, 4]:
        col = f"lag_{lag}"
        latest.loc[latest.index[-1], col] = latest["price_eur_mwh_act"].iloc[-lag]

# === 8. Export prediction ===
pred_df = pd.DataFrame(future)
pred_df.to_csv("prediction.csv", index=False)
print(pred_df)
