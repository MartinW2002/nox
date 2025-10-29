import requests
import pandas as pd

def fetch_elia_dataset(dataset_id: str, limit: int = 10000, **params):
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
    query = {
        "limit": limit,
        # you might want to order by datetime descending:
        # "order_by": "datetime DESC"
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

if __name__ == "__main__":
    # Example 1: Imbalance prices per quarter-hour (dataset ods134) :contentReference[oaicite:1]{index=1}
    # df_qh = fetch_elia_dataset("ods134", limit=5000)
    # print("Quarter-hour imbalance prices sample:")
    # print(df_qh.head())

    # Example 2: Imbalance prices per minute (near real-time) (e.g., dataset ods161) :contentReference[oaicite:2]{index=2}
    df_min = fetch_elia_dataset("ods161", limit=100)
    print("Minute-level imbalance prices sample:")
    print(df_min.head())

    # Example 3: Current system imbalance (e.g., dataset ods126) :contentReference[oaicite:3]{index=3}
    # df_sysimb = fetch_elia_dataset("ods126", limit=5000)
    # print("System imbalance sample:")
    # print(df_sysimb.head())
