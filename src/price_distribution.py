from dataset_builder import build_analysis_dataset


def main():

    df = build_analysis_dataset()

    print("\nPRICE DISTRIBUTION SUMMARY")

    print("\nBasic statistics")
    print(df["price"].describe())

    print("\nAdditional statistics")

    print("Mean:", df["price"].mean())
    print("Median:", df["price"].median())
    print("Std:", df["price"].std())

    print("\nShape statistics")

    print("Skewness:", df["price"].skew())
    print("Kurtosis:", df["price"].kurtosis())

    print("\nPrice percentiles")

    percentiles = df["price"].quantile([0.90, 0.95, 0.99])

    print(percentiles)

    print("\nTop 10 highest prices")

    print(df.sort_values("price", ascending=False).head(10)[["timestamp", "price", "demand"]])

    print("\nLowest prices")

    print(df.sort_values("price").head(5)[["timestamp", "price", "demand"]])


if __name__ == "__main__":
    main()