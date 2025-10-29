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
    print(resp.url)
    resp.raise_for_status()
    js = resp.json()
    # the data is in js["results"] or js["records"] depending on API version
    records = js.get("results") or js.get("records")
    if not records:
        raise ValueError("No records found in response.")
    # flatten into DataFrame
    df = pd.json_normalize(records)
    return df


"""
Merk op: Belgium is een aparte entiteit en niet de som van de rest
"""
def get_total_solar(datetime: str):
    solar_prod = fetch_elia_dataset("ods087", limit=100, where=f"datetime = date'{datetime}'", select="datetime,mostrecentforecast,realtime,dayaheadforecast,region") 

    combined_grouped = solar_prod.groupby('datetime').agg({
            'mostrecentforecast': 'sum',
            'realtime': 'sum',
            'dayaheadforecast': 'sum'
        }).reset_index()
    
    return combined_grouped
    
def get_total_wind(datetime: str):
    wind_wallonia = fetch_elia_dataset("ods086", limit=100, where=f"datetime = date'{datetime}' AND region='Wallonia'", select="datetime,mostrecentforecast,realtime,dayaheadforecast") 
    wind_flanders = fetch_elia_dataset("ods086", limit=100, where=f"datetime = date'{datetime}' AND region='Flanders'", select="datetime,mostrecentforecast,realtime,dayaheadforecast")
    wind_federal = fetch_elia_dataset("ods086", limit=100, where=f"datetime = date'{datetime}' AND region='Federal'", select="datetime,mostrecentforecast,realtime,dayaheadforecast")

    combined = pd.concat([wind_wallonia, wind_flanders, wind_federal])

    combined_grouped = combined.groupby('datetime').agg({
        'mostrecentforecast': 'sum',
        'realtime': 'sum',
        'dayaheadforecast': 'sum'
    }).reset_index()

    return combined_grouped
    

"""
Systemimbalance:
igccvolumeup:   MW
igccvolumedown: MW
afrrvolumeup:   MW
afrrvolumedown: MW
"""
def get_last_imbalance():
    current_imb = fetch_elia_dataset("ods169", limit=1, select="datetime, systemimbalance, afrrvolumeup, afrrvolumedown, igccvolumeup,  igccvolumedown")


    combined_grouped = current_imb.groupby('datetime').agg({
        'systemimbalance': 'sum',
        'igccvolumeup': 'sum',
        'igccvolumedown': 'sum',
        'afrrvolumeup': 'sum',
        'afrrvolumedown': 'sum'
    }).reset_index()

    return combined_grouped

if __name__ == "__main__":
    datetime = '2025-10-29T17:00:00+00:00'
    imbalance = get_last_imbalance()
    total_wind = get_total_wind(datetime)
    total_solar = get_total_solar(datetime)
    print(f'imbalance: {imbalance}')
    print(f'total_wind: {total_wind}')
    print(f'total_solar: {total_solar}')


    