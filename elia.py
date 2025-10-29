import requests
import pandas as pd

def fetch_elia_dataset(dataset_id: str, select: str = None, where: str = '1=1', limit: int = 10000, **params) -> pd.DataFrame:
    """
    Fetch data from Elia Open Data API for a given dataset identifier.
    Args:
        dataset_id: e.g. "ods134" (imbalance prices per quarter-hour) or "ods161" (1-min imbalance price).
        limit: number of records to fetch (max depends on API).
        params: additional GET parameters (e.g., order_by, filters).
    Returns:
        pandas.DataFrame of results.
    """
    url = f"https://opendata.elia.be/api/explore/v2.1/catalog/datasets/{dataset_id}/records"
    if (select == None):
        query = {
        "limit": limit,
        "order_by": "datetime DESC",
        "where": where
        }
    else:
        query = {
            "limit": limit,
            "select": select,
            "order_by": "datetime DESC",
            "where": where
        }
    # add any extra params
    query.update(params)
    resp = requests.get(url, params=query)
    resp.raise_for_status()
    js = resp.json()
    # the data is in js["results"] or js["records"] depending on API version
    records = js.get("results") or js.get("records")
    if not records:
        raise ValueError("No records found in response.")
    # flatten into DataFrame
    df = pd.json_normalize(records)
    return df

def get_total_wind():
    wind_wallonia = fetch_elia_dataset("ods086", limit=10, where="region='Wallonia'", select="datetime,mostrecentforecast") 
    wind_flanders = fetch_elia_dataset("ods086", limit=10, where="region='Flanders'", select="datetime,mostrecentforecast")
    wind_federal = fetch_elia_dataset("ods086", limit=10, where="region='Federal'", select="datetime,mostrecentforecast")

    combined = pd.concat([wind_wallonia, wind_flanders, wind_federal])

    return combined.groupby('datetime')['mostrecentforecast'].sum()

if __name__ == "__main__":
    # Example 1: Imbalance prices per quarter-hour (dataset ods134) :contentReference[oaicite:1]{index=1}
    # df_qh = fetch_elia_dataset("ods134", limit=5000)
    # print("Quarter-hour imbalance prices sample:")
    # print(df_qh.head())

    # df_min = fetch_elia_dataset("ods161", limit=1) # Live minute per minute
    # print("Minute-level imbalance prices sample:")
    # print(df_min.head())

    # wind_prod = fetch_elia_dataset("ods086", limit=10, where="region='Wallonia'") # 031
    # print("Wind prod:")
    # print(wind_prod.head())

    # solar_prod = fetch_elia_dataset("ods087", limit=1) # 031
    # print("Solar prod:")
    # print(solar_prod.head())

    # total_gen = fetch_elia_dataset("ods201", limit=1)
    # print("Total Gen:")
    # print(total_gen.head())

    # current_imb = fetch_elia_dataset("ods169", limit=1, select="datetime, systemimbalance, afrrvolumeup, afrrvolumedown, igccvolumeup,  igccvolumedown")
    # print("Current Imb:")
    # print(current_imb.head())

    # forecast_imb = fetch_elia_dataset("ods136", limit=1, select="datetime, systemimbalance, afrrvolumeup, afrrvolumedown, igccvolumeup,  igccvolumedown")
    # print("Current Imb:")
    # print(current_imb.head())

    get_total_wind()
    # load_live_forecast = fetch_elia_dataset("ods002", limit=100, select="datetime, mostrecentforecast")
    # print("Load live:")
    # print(load_live_forecast)



    # Example 3: Current system imbalance (e.g., dataset ods126) :contentReference[oaicite:3]{index=3}
    # df_sysimb = fetch_elia_dataset("ods126", limit=5000)
    # print("System imbalance sample:")
    # print(df_sysimb.head())



    