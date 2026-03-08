from dataset_builder import build_analysis_dataset


def main():

    df = build_analysis_dataset()

    # spike threshold
    spike_threshold = df["price"].quantile(0.99)

    # spike indicator
    df["spike"] = df["price"] > spike_threshold

    # define high demand
    demand_threshold = df["demand"].quantile(0.90)

    print("\nDEMAND THRESHOLD (90th percentile):", demand_threshold)

    df["high_demand"] = df["demand"] > demand_threshold

    # split groups
    high_demand_df = df[df["high_demand"]]
    normal_demand_df = df[~df["high_demand"]]

    # probabilities
    p_spike_high = high_demand_df["spike"].mean()
    p_spike_normal = normal_demand_df["spike"].mean()

    print("\nCONDITIONAL SPIKE PROBABILITIES")

    print("P(spike | high demand):", p_spike_high)
    print("P(spike | normal demand):", p_spike_normal)

    # counts
    print("\nCounts")

    print("High demand intervals:", len(high_demand_df))
    print("Normal demand intervals:", len(normal_demand_df))

    print("Spikes during high demand:", high_demand_df["spike"].sum())
    print("Spikes during normal demand:", normal_demand_df["spike"].sum())


if __name__ == "__main__":
    main()