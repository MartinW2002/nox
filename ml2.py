import pandas as pd

# Load
dam = pd.read_csv("data/dam_prices.csv", parse_dates=["datetime_utc"])
imb_fc = pd.read_csv("data/imbalance_forecast.csv", parse_dates=["datetime_utc"])
imb_act = pd.read_csv("data/imbalance_actual.csv", parse_dates=["datetime_utc"])

# Rename to make columns clear
dam = dam.rename(columns={"price_eur_mwh": "dam_price"})
imb_fc = imb_fc.rename(columns={"price_eur_mwh": "imb_fc_price"})
imb_act = imb_act.rename(columns={"price_eur_mwh": "imb_act_price"})

# Merge on datetime
df = imb_act.merge(imb_fc, on="datetime_utc", how="left")
df = df.merge(dam, on="datetime_utc", how="left")

# Sort and drop rows with missing values
df = df.sort_values("datetime_utc").dropna().reset_index(drop=True)
