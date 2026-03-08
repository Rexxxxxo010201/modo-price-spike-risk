from dataset_builder import build_analysis_dataset


def main():

    df = build_analysis_dataset()

    print("\nDATASET SHAPE")
    print(df.shape)

    print("\nCOLUMNS")
    print(df.columns)

    print("\nMISSING VALUES")
    print(df.isna().sum())

    print("\nTIMESTAMP RANGE")
    print(df["timestamp"].min(), "→", df["timestamp"].max())

    print("\nUNIQUE TIMESTAMPS")
    print(df["timestamp"].nunique())

    print("\nDUPLICATE TIMESTAMPS")
    print(df["timestamp"].duplicated().sum())

    print("\nTIMESTAMP INTERVAL CHECK")
    print(df["timestamp"].diff().value_counts().head())

    print("\nPRICE SUMMARY")
    print(df["price"].describe())

    print("\nDEMAND SUMMARY")
    print(df["demand"].describe())


if __name__ == "__main__":
    main()