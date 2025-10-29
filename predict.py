import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import weather_old

# --- Load and merge data ---
imbalance = pd.read_csv("./input/historical_imbalance.csv", sep=";")  # columns: datetime, imbalance_mwh, price
imbalance_actual = pd.read_csv("./data/imbalance_actual.csv")  # columns: datetime, imbalance_mwh, price
wind = pd.read_csv("./input/historical_wind.csv", sep=";")\
    .groupby("Datetime", as_index=False)\
    .sum(numeric_only=True)
solar = pd.read_csv("./input/historical_solar.csv", sep=";")\
    .groupby("Datetime", as_index=False)\
    .sum(numeric_only=True)
historical_dam = pd.read_csv("./input/historical_dam.csv") # 
weather = weather_old.weather_data()  # columns: datetime, windspeed, radiation

# Ensure datetime alignment
imbalance["datetime"] = pd.to_datetime(imbalance["Datetime"], utc=True, errors="coerce")
weather["datetime"] = pd.to_datetime(weather["datetime"], utc=True, errors="coerce")
imbalance_actual["datetime"] = pd.to_datetime(imbalance_actual["datetime_utc"], utc=True, errors="coerce")
historical_dam["datetime"] = pd.to_datetime(historical_dam["datetime_utc"], utc=True, errors="coerce")
wind["datetime"] = pd.to_datetime(wind["Datetime"], utc=True, errors="coerce")
solar["datetime"] = pd.to_datetime(solar["Datetime"], utc=True, errors="coerce")

# Merge on nearest timestamp (15-min data)
# --- Ensure datetime column and proper dtype ---
for df in (imbalance, weather, imbalance_actual, historical_dam, wind, solar):
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df.sort_values("datetime", inplace=True)

tmp = pd.merge_asof(
    imbalance,
    weather,
    on="datetime",
    direction="nearest",
)

tmp2 = pd.merge_asof(
    tmp,
    imbalance_actual,
    on="datetime",
    direction="nearest",
)

tmp3 = pd.merge_asof(
    tmp2,
    historical_dam,
    on="datetime",
    direction="nearest",
)

tmp4 = pd.merge_asof(
    tmp3,
    wind,
    on="datetime",
    direction="nearest",
)

df = pd.merge_asof(
    tmp4,
    solar,
    on="datetime",
    direction="nearest",
)


df["hour"] = df["datetime"].dt.hour + df["datetime"].dt.minute / 60  # fractional hour (15-min steps)
df["weekend"] = df["datetime"].dt.dayofweek.isin([5, 6]).astype(int)  # Sat/Sun = 1 else 0

features = ["System imbalance", "IGCC+", "IGCC-", "aFRR -", "aFRR +", "wind_speed_10m", "direct_radiation", "hour", "weekend", "price_eur_mwh_dam", "measured_wind", "most_recent_wind","day_ahead_wind", "measured_solar", "most_recent_solar","day_ahead_solar"]
target = "price_eur_mwh"

# Drop missing rows
df = df.dropna(subset=features + [target])

# --- 80/20 chronological split ---
X_train, X_test, y_train, y_test = train_test_split(
    df[features],
    df[target],
    test_size=0.1,
    shuffle=False
)

# --- Train LightGBM model ---
train_data = lgb.Dataset(X_train, label=y_train)
test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

params = {
    "objective": "regression",
    "metric": "mae",
    "learning_rate": 0.03,
    "num_leaves": 63,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "lambda_l1": 0.5,
    "lambda_l2": 0.5,
    "min_data_in_leaf": 50,
    "max_depth": 8,
    "verbose": -1
}

model = lgb.train(
    params,
    train_data,
    valid_sets=[test_data],
    num_boost_round=500,
)

# --- Evaluate ---
y_pred = model.predict(X_test, num_iteration=model.best_iteration)
mae = mean_absolute_error(y_test, y_pred)
print(f"MAE: {mae:.2f}")

model.save_model('out/model1.txt')
