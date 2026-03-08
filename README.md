# Quantifying Extreme Price Risk in Electricity Markets

## Problem Statement

Electricity markets occasionally experience extreme price spikes far above typical levels. These events are rare but economically significant because a small number of intervals can dominate revenues and trading outcomes.

This project analyzes electricity price data to quantify:

- how frequently extreme price spikes occur
- how spike probability changes under high demand conditions

## Data

Source: Australian National Electricity Market operated by the Australian Energy Market Operator.

### Dispatch Prices

#### Dataset

Dispatch prices before administered price from the NEMWeb archive.

#### Resolution

5 minute dispatch intervals

#### Region Analyzed

NSW1

#### Files Used

- `PUBLIC_DISPATCHPRICES_PRE_AP_20250304.zip`
- `PUBLIC_DISPATCHPRICES_PRE_AP_20250305.zip`
- `PUBLIC_DISPATCHPRICES_PRE_AP_20250306.zip`
- `PUBLIC_DISPATCHPRICES_PRE_AP_20250307.zip`
- `PUBLIC_DISPATCHPRICES_PRE_AP_20250308.zip`
- `PUBLIC_DISPATCHPRICES_PRE_AP_20250309.zip`
- `PUBLIC_DISPATCHPRICES_PRE_AP_20250310.zip`

#### Extracted Fields

- `timestamp`
- `region`
- `price`

### Operational Demand

#### Dataset

Operational demand by region from the NEMWeb archive.

#### Folder Downloaded

`PUBLIC_ACTUAL_OPERATIONAL_DEMAND_HH_AREA_20250304`

This folder contains interval ZIP files with operational demand data.

#### Resolution

30 minute intervals

#### Extracted Fields

- `timestamp`
- `region`
- `demand`

## Dataset Construction

### Steps

- Extract dispatch price records from nested ZIP files
- Extract operational demand records from interval ZIP files
- Filter both datasets to region NSW1
- Restrict datasets to their overlapping time window
- Resample demand to 5 minute frequency using forward fill
- Merge price and demand data on timestamp

### Final Dataset Structure

- `timestamp`
- `price`
- `demand`


- `2025-03-04` -> `2025-03-10`
- 5 minute intervals
- 2005 observations

## Initial Findings

Basic distribution analysis of NSW wholesale prices shows the typical characteristics of electricity markets.

### Price Statistics

- Mean price: 63
- Median price: 75
- Maximum price: 525
- Minimum price: -33

### Distribution Shape

- Skewness: 1.09
- Kurtosis: 5.73

### Interpretation

- Prices exhibit **positive skew**, indicating occasional large upward spikes.
- **High kurtosis** suggests heavy tails, meaning extreme price events occur more frequently than under a normal distribution.
- Prices can also become **negative during oversupply periods**.

Candidate spike thresholds derived from the distribution:

- 90th percentile: 115
- 95th percentile: 163
- 99th percentile: 222

The **99th percentile (~222)** will be used as the baseline threshold for defining extreme price spikes in the subsequent analysis.

## Spike Detection

### Spike Definition

`price > 99th percentile`

### Spike Statistics

- Total intervals: 2005
- Number of spikes: 21

### Baseline Spike Probability

`P(spike) = 21 / 2005 ≈ 1.05%`

## Demand Conditional Risk

### High Demand Definition

`demand > 90th percentile = 8675 MW`

### Observed Probabilities

- `P(spike | high demand) = 17 / 198 ≈ 8.59%`
- `P(spike | normal demand) = 4 / 1807 ≈ 0.22%`

### Risk Multiplier

Risk multiplier quantifies how much spike risk increases during high demand:

`Risk multiplier = P(spike | high demand) / P(spike | normal demand)`

`Risk multiplier ≈ 0.0859 / 0.00221 ≈ 38.8`

### Interpretation

Extreme price spikes occur about 39x more frequently during high demand periods.

## Extreme Value Analysis

To model the behaviour of extreme price events, a Peaks Over Threshold (POT) approach was applied using a Generalized Pareto Distribution (GPD).

### Threshold Selection

Candidate thresholds were evaluated using threshold stability and mean excess diagnostics.

- 90th percentile: 115
- 92.5th percentile: 135
- 95th percentile: 163
- 97.5th percentile: 202

The **95th percentile (≈163)** was selected as the modeling threshold because it captures the extreme tail while retaining sufficient exceedances for stable estimation.

### Number of Exceedances

101 observations above the threshold were used for tail modeling.

### Estimated GPD Parameters

- Shape parameter (xi): 0.155
- Scale parameter (beta): 43.21

A positive shape parameter indicates a **heavy-tailed distribution**, meaning extreme price events decay slowly and very large spikes remain plausible.

### Extreme Price Probability

Using the fitted tail model:

`P(price > 500) ≈ 0.000304`

This corresponds to roughly **0.03% of dispatch intervals**.

Given 288 dispatch intervals per day, the model implies a $500 price event approximately **once every ~11 days**.

### Return Level Estimate

The estimated **1-day return level** is:

`≈ $555`

This represents the price level expected to be exceeded roughly **once per day of dispatch intervals** under the fitted tail model.

### Interpretation

Extreme price spikes are rare but statistically significant. The EVT results confirm that electricity prices exhibit **heavy-tailed behavior**, where extreme events occur more frequently than under normal distributions.

## Interactive Dashboard

An interactive dashboard was built using Streamlit to explore the results of the analysis.

The dashboard allows users to:

- visualize electricity prices over time
- examine the distribution of wholesale prices
- analyze the relationship between demand and price spikes
- explore conditional spike probabilities under high demand
- estimate extreme price probabilities using Extreme Value Theory

Users can adjust the target price to estimate the probability of extreme price events and the expected return period.

Example question the dashboard answers:

"What is the probability of electricity prices exceeding $500/MWh?"
