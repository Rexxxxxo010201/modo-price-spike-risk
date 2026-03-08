import numpy as np
import pandas as pd
from scipy.stats import genpareto

from dataset_builder import build_analysis_dataset


def threshold_stability(prices):

    print("\nTHRESHOLD STABILITY ANALYSIS")

    thresholds = prices.quantile([0.90, 0.925, 0.95, 0.975])

    results = []

    for q, u in thresholds.items():

        exceedances = prices[prices > u] - u

        shape, loc, scale = genpareto.fit(exceedances)

        results.append({
            "quantile": q,
            "threshold": u,
            "num_exceedances": len(exceedances),
            "shape_xi": shape,
            "scale_beta": scale
        })

    results_df = pd.DataFrame(results)

    print(results_df)


def mean_excess_analysis(prices):

    print("\nMEAN EXCESS ANALYSIS")

    thresholds = prices.quantile(np.linspace(0.85, 0.97, 10))

    rows = []

    for u in thresholds:

        exceedances = prices[prices > u] - u

        mean_excess = exceedances.mean()

        rows.append({
            "threshold": u,
            "mean_excess": mean_excess,
            "num_exceedances": len(exceedances)
        })

    df = pd.DataFrame(rows)

    print(df)


def gpd_fit(prices):

    print("\nGPD FIT")

    u = prices.quantile(0.95)

    print("Selected threshold:", u)

    exceedances = prices[prices > u] - u

    print("Number of exceedances:", len(exceedances))

    shape, loc, scale = genpareto.fit(exceedances)

    print("\nGPD parameters")

    print("Shape (xi):", shape)
    print("Scale (beta):", scale)

    return u, shape, scale, len(exceedances)


def extreme_probability(prices, u, shape, scale, n_exceed):

    print("\nEXTREME PRICE PROBABILITY")

    target_price = 500

    excess = target_price - u

    tail_prob = genpareto.sf(excess, shape, loc=0, scale=scale)

    exceedance_rate = n_exceed / len(prices)

    probability = exceedance_rate * tail_prob

    print("Estimated probability(price >", target_price, ") =", probability)


def return_level(prices, u, shape, scale):

    print("\nRETURN LEVEL ESTIMATE")

    intervals_per_day = 288

    return_period_days = 1

    p = 1 / (intervals_per_day * return_period_days)

    return_level = u + (scale / shape) * ((p ** (-shape)) - 1)

    print("Estimated 1-day return level:", return_level)


def demand_conditioned_evt(df):

    print("\nDEMAND CONDITIONED EVT")

    demand_threshold = df["demand"].quantile(0.90)

    high_demand = df[df["demand"] > demand_threshold]
    normal_demand = df[df["demand"] <= demand_threshold]

    for label, subset in [("High demand", high_demand), ("Normal demand", normal_demand)]:

        prices = subset["price"]

        u = prices.quantile(0.95)

        exceedances = prices[prices > u] - u

        shape, loc, scale = genpareto.fit(exceedances)

        print("\n", label)

        print("threshold:", u)
        print("exceedances:", len(exceedances))
        print("shape:", shape)
        print("scale:", scale)


def main():

    df = build_analysis_dataset()

    prices = df["price"]

    print("\nEXTREME VALUE ANALYSIS")

    threshold_stability(prices)

    mean_excess_analysis(prices)

    u, shape, scale, n_exceed = gpd_fit(prices)

    extreme_probability(prices, u, shape, scale, n_exceed)

    return_level(prices, u, shape, scale)

    demand_conditioned_evt(df)


if __name__ == "__main__":
    main()