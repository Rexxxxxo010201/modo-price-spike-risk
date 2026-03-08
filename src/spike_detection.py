from dataset_builder import build_analysis_dataset


def main():

    df = build_analysis_dataset()

    # spike threshold
    spike_threshold = df["price"].quantile(0.99)

    print("\nSPIKE DETECTION")
    print("Spike threshold (99th percentile):", spike_threshold)

    # create spike indicator
    df["spike"] = df["price"] > spike_threshold

    # spike statistics
    spike_count = df["spike"].sum()
    total_intervals = len(df)

    spike_probability = spike_count / total_intervals

    print("\nSpike statistics")

    print("Number of spikes:", spike_count)
    print("Total intervals:", total_intervals)
    print("Spike probability:", spike_probability)

    # inspect spikes
    print("\nSpike events")

    spikes = df[df["spike"]]

    print(spikes[["timestamp", "price", "demand"]].head(10))


if __name__ == "__main__":
    main()