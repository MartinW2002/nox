import pandas as pd

# Load data
dam = pd.read_csv('data/dam_prices.csv')
dam['datetime_utc'] = pd.to_datetime(dam['datetime_utc'])

# Basic analysis
print(f"Average price: {dam['price_eur_mwh'].mean():.2f} EUR/MWh")
print(f"Min price: {dam['price_eur_mwh'].min():.2f} EUR/MWh")
print(f"Max price: {dam['price_eur_mwh'].max():.2f} EUR/MWh")