import requests
import pandas as pd

def get_nl_demand_production_data(limit: int = 100):
    base_url = "https://developer.tennet.eu/open-api"  # example base — check actual endpoint
    # According to TenneT API docs, “Metered injections” gives load (consumption) per time unit. :contentReference[oaicite:3]{index=3}
    endpoint = "/data/metered-injections"  # placeholder path — you’ll need to confirm
    params = {
        "limit": limit,
        "order_by": "time DESC"
    }
    resp = requests.get(base_url + endpoint, params=params)
    resp.raise_for_status()
    data = resp.json()
    # Let's assume the JSON contains a list of entries under key “data” or similar
    records = data.get("data", [])
    df = pd.json_normalize(records)
    # Convert time fields
    if "time" in df.columns:
        df["datetime_utc"] = pd.to_datetime(df["time"], utc=True)
    return df

if __name__ == "__main__":
    nl_df = get_nl_demand_production_data(limit=10)
    print(nl_df.head())
