from __future__ import annotations

import pandas as pd

try:
    from demand_loader import load_operational_demand
    from price_loader import load_dispatch_prices
except ModuleNotFoundError:
    from src.demand_loader import load_operational_demand
    from src.price_loader import load_dispatch_prices


def build_analysis_dataset() -> pd.DataFrame:
    prices = load_dispatch_prices()
    prices = prices[prices["region"] == "NSW1"].copy()

    demand = load_operational_demand()
    demand = demand[demand["region"] == "NSW1"].copy()

    overlap_start = max(prices["timestamp"].min(), demand["timestamp"].min())
    overlap_end = min(prices["timestamp"].max(), demand["timestamp"].max())

    prices = prices[
        (prices["timestamp"] >= overlap_start) & (prices["timestamp"] <= overlap_end)
    ].copy()
    demand = demand[
        (demand["timestamp"] >= overlap_start) & (demand["timestamp"] <= overlap_end)
    ].copy()

    demand = (
        demand.sort_values("timestamp")
        .set_index("timestamp")[["demand"]]
        .resample("5min")
        .ffill()
        .reset_index()
    )

    merged = prices[["timestamp", "price"]].merge(demand, on="timestamp", how="inner")
    merged = merged[["timestamp", "price", "demand"]].sort_values("timestamp").reset_index(
        drop=True
    )

    print(f"number of rows in merged dataset: {len(merged)}")
    if not merged.empty:
        print(f"min timestamp: {merged['timestamp'].min()}")
        print(f"max timestamp: {merged['timestamp'].max()}")
    else:
        print("min timestamp: NaT")
        print("max timestamp: NaT")

    return merged


if __name__ == "__main__":
    dataset = build_analysis_dataset()
    print(dataset.head())
