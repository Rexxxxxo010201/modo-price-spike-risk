import plotly.express as px
import plotly.graph_objects as go


def price_time_series(df, spike_threshold):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["price"],
            mode="lines",
            name="Price"
        )
    )

    spikes = df[df["price"] > spike_threshold]

    fig.add_trace(
        go.Scatter(
            x=spikes["timestamp"],
            y=spikes["price"],
            mode="markers",
            marker=dict(color="red", size=6),
            name="Spikes"
        )
    )

    fig.update_layout(
        title="Electricity Prices Over Time",
        xaxis_title="Time",
        yaxis_title="Price ($/MWh)"
    )

    return fig


def price_distribution_plot(df):

    import numpy as np
    import plotly.graph_objects as go

    p95 = df["price"].quantile(0.95)
    p99 = df["price"].quantile(0.99)

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=df["price"],
            nbinsx=50,
            name="Price Distribution"
        )
    )

    fig.add_vline(
        x=p95,
        line_dash="dash",
        line_color="orange",
        annotation_text="95th percentile"
    )

    fig.add_vline(
        x=p99,
        line_dash="dash",
        line_color="red",
        annotation_text="99th percentile"
    )

    fig.update_layout(
        title="Electricity Price Distribution",
        xaxis_title="Price ($/MWh)",
        yaxis_title="Frequency"
    )

    return fig


def demand_price_scatter(df):

    import plotly.express as px

    fig = px.scatter(
        df,
        x="demand",
        y="price",
        title="Demand vs Electricity Price",
        labels={
            "demand": "Demand (MW)",
            "price": "Price ($/MWh)"
        }
    )

    return fig