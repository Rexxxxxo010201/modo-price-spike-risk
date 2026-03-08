import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import genpareto
from src.dataset_builder import build_analysis_dataset

st.set_page_config(layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------

df = build_analysis_dataset()
df["timestamp"] = pd.to_datetime(df["timestamp"])

# -----------------------------
# SPIKE DEFINITION
# -----------------------------

spike_threshold = df["price"].quantile(0.99)
df["is_spike"] = df["price"] > spike_threshold

# -----------------------------
# DEMAND REGIME
# -----------------------------

demand_threshold = df["demand"].quantile(0.90)

df["demand_regime"] = np.where(
    df["demand"] >= demand_threshold,
    "High demand",
    "Normal demand"
)

# -----------------------------
# CONDITIONAL SPIKE PROBABILITY
# -----------------------------

spike_probabilities = (
    df.groupby("demand_regime")["is_spike"]
    .mean()
    .reset_index()
)

high_demand_prob = spike_probabilities.loc[
    spike_probabilities["demand_regime"] == "High demand", "is_spike"
].values[0]

normal_demand_prob = spike_probabilities.loc[
    spike_probabilities["demand_regime"] == "Normal demand", "is_spike"
].values[0]

risk_multiplier = high_demand_prob / normal_demand_prob

# -----------------------------
# EVT FIT
# -----------------------------

evt_threshold = df["price"].quantile(0.95)

exceedances = df[df["price"] > evt_threshold]["price"] - evt_threshold
num_exceedances = len(exceedances)
total_observations = len(df)
exceedance_prob = num_exceedances / total_observations

shape, loc, scale = genpareto.fit(exceedances)

# -----------------------------
# HEADER
# -----------------------------

st.title("Electricity Price Risk Explorer")

col1, col2, col3 = st.columns(3)

col1.metric("Observations", len(df))
col2.metric("Spike Threshold ($/MWh)", round(spike_threshold, 2))
col3.metric(
    "Date Range",
    f"{df['timestamp'].min().date()} → {df['timestamp'].max().date()}"
)

# -----------------------------
# PRICE TIME SERIES
# -----------------------------

st.subheader("Electricity Prices Over Time")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df["timestamp"],
        y=df["price"],
        mode="lines",
        name="Price"
    )
)

spikes = df[df["is_spike"]]

fig.add_trace(
    go.Scatter(
        x=spikes["timestamp"],
        y=spikes["price"],
        mode="markers",
        marker=dict(color="red"),
        name="Spikes"
    )
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
"""
### Insights

• Prices show mean reverting behaviour around normal operating levels.  
• Using the 99th percentile threshold ($221.85/MWh), there are **21 spike intervals** in the sample.  
• Spikes appear in short clusters, indicating extreme events are rare but can persist briefly.
"""
)

# -----------------------------
# PRICE DISTRIBUTION
# -----------------------------

st.subheader("Price Distribution")

p95 = df["price"].quantile(0.95)
p99 = df["price"].quantile(0.99)

fig = px.histogram(
    df,
    x="price",
    nbins=40,
    labels={"price": "Price ($/MWh)", "count": "Frequency"}
)
fig.update_traces(marker_color="lightblue")

fig.add_vline(
    x=p95,
    line_width=3,
    line_dash="dash",
    line_color="orange",
    annotation_text="95th percentile",
    annotation_position="top left"
)
fig.add_vline(
    x=p99,
    line_width=3,
    line_dash="dash",
    line_color="red",
    annotation_text="99th percentile",
    annotation_position="top right"
)

st.plotly_chart(fig, use_container_width=True)

skewness = df["price"].skew()
kurtosis = df["price"].kurtosis()

st.markdown(
f"""
### Insights

• The price distribution is **right skewed** (skewness: {skewness:.2f}).  
• Heavy tails are evident (kurtosis: {kurtosis:.2f}), indicating extreme prices occur more often than under a normal distribution.  
• Percentile thresholds at **P95 ({df["price"].quantile(0.95):.2f})** and **P99 ({spike_threshold:.2f})** provide practical spike definitions.
"""
)

# -----------------------------
# DEMAND VS PRICE
# -----------------------------

st.subheader("Demand vs Price")

fig = px.scatter(df, x="demand", y="price")

st.plotly_chart(fig, use_container_width=True)

correlation = df["price"].corr(df["demand"])

st.markdown(
f"""
### Insights

• The demand price relationship is **nonlinear** (correlation: {correlation:.2f}).  
• Prices remain relatively stable at moderate demand levels.  
• Extreme price spikes concentrate near **system peak demand**.
"""
)

# -----------------------------
# SPIKE PROBABILITY BY DEMAND
# -----------------------------

st.subheader("Spike Probability by Demand Level")

col1, col2, col3 = st.columns(3)

col1.metric("P(spike | high demand)", f"{high_demand_prob*100:.2f}%")
col2.metric("P(spike | normal demand)", f"{normal_demand_prob*100:.2f}%")
col3.metric("Risk Multiplier", f"{risk_multiplier:.1f}x")

baseline_spike_probability = df["is_spike"].mean()
st.metric("Baseline Spike Probability", f"{baseline_spike_probability * 100:.2f}%")
st.markdown(
    "Across the dataset, extreme price spikes occur in approximately 1.05% of dispatch intervals. "
    "This highlights that spikes are rare but economically significant events."
)

fig = px.bar(
    spike_probabilities,
    x="demand_regime",
    y=spike_probabilities["is_spike"] * 100,
    labels={"y": "Spike Probability (%)", "demand_regime": "Demand Regime"}
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# EVT EXPLORER
# -----------------------------

st.subheader("Extreme Price Probability Explorer")

target_price = st.number_input(
    "Target price ($/MWh)",
    min_value=0,
    max_value=2000,
    value=500,
    step=50
)

# EVT probability calculation
conditional_prob = genpareto.sf(
    target_price - evt_threshold,
    shape,
    loc=0,
    scale=scale
)
probability = exceedance_prob * conditional_prob

prob_percent = probability * 100

intervals_per_day = 288

expected_intervals = 1 / probability
return_days = expected_intervals / intervals_per_day

col1, col2 = st.columns(2)

col1.metric("Estimated P(price > target)", f"{prob_percent:.3f}%")
col2.metric("Expected return period", f"{return_days:.1f} days")

if return_days < 1.5:
    period_text = "1 day"
else:
    period_text = f"{round(return_days)} days"

st.write(
f"Extreme value modelling suggests a {prob_percent:.3f}% probability of prices exceeding ${target_price}/MWh."
)

st.write(
f"A price above ${target_price}/MWh is expected approximately once every {period_text}."
)

st.markdown(
    f"The positive GPD shape parameter (xi ≈ {shape:.3f}) indicates a heavy-tailed price distribution, "
    "meaning the probability of extreme price spikes decays slowly. As a result, very large price events "
    "remain statistically plausible even if they occur infrequently."
)

# -----------------------------
# EVT PROBABILITY CURVE
# -----------------------------

price_range = np.linspace(evt_threshold, 2000, 200)

conditional_probabilities = genpareto.sf(
    price_range - evt_threshold, shape, loc=0, scale=scale
)
probabilities = exceedance_prob * conditional_probabilities

fig = px.line(
    x=price_range,
    y=probabilities * 100,
    labels={
        "x": "Price Level ($/MWh)",
        "y": "Probability Price Exceeds Level (%)"
    },
    title="Extreme Price Probability Curve"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
"""
### EVT Interpretation

Extreme Value Theory focuses on the tail of the price distribution rather than average behaviour.  
The Generalized Pareto Distribution models exceedances above a high threshold to quantify extreme risk.  
Return periods translate tail probabilities into an intuitive estimate of how often extreme prices may occur.
"""
)
