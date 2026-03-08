from dataset_builder import build_analysis_dataset
from visualizations import (
    price_time_series,
    price_distribution_plot,
    demand_price_scatter
)


def main():

    df = build_analysis_dataset()

    spike_threshold = df["price"].quantile(0.99)

    fig1 = price_time_series(df, spike_threshold)
    fig1.show()

    fig2 = price_distribution_plot(df)
    fig2.show()

    fig3 = demand_price_scatter(df)
    fig3.show()


if __name__ == "__main__":
    main()